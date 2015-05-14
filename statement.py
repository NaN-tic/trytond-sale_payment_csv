# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from datetime import datetime
from decimal import Decimal
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.wizard import Button, StateTransition, StateView, Wizard

__all__ = ['PaymentFromSaleImportCSVStart', 'PaymentFromSaleImportCSV']
__metaclass__ = PoolMeta


class PaymentFromSaleImportCSVStart(ModelView):
    'Payment From Sale Import CSV Start'
    __name__ = 'import.csv.payment.from.sale.start'
    profile_domain = fields.Function(fields.One2Many('profile.csv', None,
        'Profile Domain', states={
            'invisible': True
            }),
        'on_change_with_profile_domain')
    profile = fields.Many2One('profile.csv', 'Profile CSV', required=True,
        domain=[
            ('id', 'in', Eval('profile_domain')),
            ], depends=['profile_domain']
        )
    import_file = fields.Binary('Import File', required=True)
    attach = fields.Boolean('Attach File',
        help='Attach CSV file after import.')

    @fields.depends('attach')
    def on_change_with_profile_domain(self, name=None):
        pool = Pool()
        Model = pool.get('ir.model')
        Profile = pool.get('profile.csv')

        model, = Model.search([
                ('model', '=', 'account.statement.line')
                ])
        profiles = Profile.search([
                ('model', '=', model.id),
                ])

        return [p.id for p in profiles]

    @classmethod
    def default_profile(cls):
        profiles = cls().on_change_with_profile_domain()
        if len(profiles) == 1:
            return profiles[0]

    @classmethod
    def default_attach(cls):
        return True


class PaymentFromSaleImportCSV(Wizard):
    'Payment From Sale Import CSV'
    __name__ = 'import.csv.payment.from.sale'
    start = StateView('import.csv.payment.from.sale.start',
        'sale_payment_csv.import_csv_payment_from_sale_start_form_view', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Import File', 'import_file', 'tryton-ok', default=True),
            ])
    import_file = StateTransition()

    @classmethod
    def __setup__(cls):
        super(PaymentFromSaleImportCSV, cls).__setup__()
        cls._error_messages.update({
                'sale_domain_searcher_field_empty_error':
                    'Sale Domain Searcher field can not be empty.',
                'csv_format_error': 'Please, check that the Statement CSV '
                    'configuration matches with the format of the CSV file.',
                'statement_already_exists_error': 'Statement line %s skipped. '
                    'Already exists.',
                'sale_domain_searcher_error': 'Error in field Sale Domain '
                    'Searcher.\nError raised: %s',
                'sale_domain_searcher_help': "Tryton's domain [1] for "
                    "searching sales which match with statement lines. You "
                    "can use these variables:\n"
                    " * values: Dictionary with values mapped on the columns "
                    "of the csv profile.\n"
                    " * row: List with the values of the csv file. This "
                    "variable can not process other values than Char type.\n"
                    "As a example:\n[('reference', '=', row[4])]\n\n"
                    "[1] http://trytond.readthedocs.org/en/latest/topics/"
                    "domain.html.",
                'sale_state_filter_error': 'Error in field Sale State Filter .'
                    '\nError raised: %s',
                'sale_state_filter_help': "Tryton's domain [1] for searching "
                    "sales which match with statement lines. You can use these"
                    " variables:\n"
                    " * values: Dictionary with values mapped on the columns "
                    "of the csv profile.\n"
                    " * row: List with the values of the csv file. This "
                    "variable can not process other values than Char type.\n"
                    "For instance:\n"
                    "[('state', 'in', "
                    "('quotation', 'confirmed', 'processing')), "
                    "('invoice_state', 'in', "
                    "('draft', 'validated', 'posted', 'waiting'))]"
                    "[1] http://trytond.readthedocs.org/en/latest/topics/"
                    "domain.html.",
                'state_match_error': 'Sale %s skipped. '
                    'Sale state %s does not match.',
                'sale_amount_filter_error': 'Error in field Sale '
                    'Amount Filter.\nError raised: %s',
                'sale_amount_filter_help': "Tryton's domain [1] for searching "
                    "sales which match with statement lines. You can use these"
                    " variables:\n"
                    " * values: Dictionary with values mapped on the columns "
                    "of the csv profile.\n"
                    " * row: List with the values of the csv file. This "
                    "variable can not process other values than Char type.\n"
                    "For instance:\n"
                    "[('total_amount_cache', '>', "
                    "values['amount'] * Decimal(0.99)), "
                    "('total_amount_cache', '<', "
                    "values['amount'] * Decimal(1.01))]\n"
                    "[1] http://trytond.readthedocs.org/en/latest/topics/"
                    "domain.html.",
                'sale_amount_match_error':
                    'Sale %s does not match its quantity.',
                'sale_not_found_error': 'Sale %s skipped. Not found.',
                'sale_too_match_error': 'Sale %s skipped. More than one sale '
                    'found matching the different criteria. Please, be more '
                    'precise.',
                'not_statement_journal': 'No statement journal configured for '
                    '%s account journal. Please configure one.',
                'not_draft_statement_found': 'There isn\'t any statement in '
                    'draft state. Please open one.',
                })

    def transition_import_file(self):
        pool = Pool()
        Sale = pool.get('sale.sale')
        Statement = pool.get('account.statement')
        StatementLine = pool.get('account.statement.line')
        Date = pool.get('ir.date')
        Attachment = pool.get('ir.attachment')
        ImportCSVLog = pool.get('import.csv.log')

        profile = self.start.profile
        if not profile.sale_domain:
            self.raise_user_error('sale_domain_searcher_field_empty_error')

        import_file = self.start.import_file
        has_header = profile.header
        attach = self.start.attach

        data = profile.read_csv_file(import_file)

        if has_header:
            next(data, None)

        vlist = []
        sales_found = []
        log_values = []
        for row in list(data):
            values = {}
            statement_line_domain = []

            for column in profile.columns:
                cells = column.column.split(',')
                try:
                    value = ','.join(row[int(c)] for c in cells)
                except IndexError:
                    self.raise_user_error('csv_format_error')
                ttype = column.ttype
                get_value = getattr(column, 'get_%s' % ttype)
                values[column.field.name] = get_value(value)
                statement_line_domain.append(
                    (column.field.name, '=', values[column.field.name])
                    )

            statements = StatementLine.search(statement_line_domain)
            if statements:
                log_value = {
                    'date_time': datetime.now(),
                    }
                log_value['comment'] = self.raise_user_error(
                    'statement_already_exists_error',
                    error_args=(statements[0].description,),
                    raise_exception=False)
                log_value['status'] = 'skipped'
                log_values.append(log_value)
                continue

            try:
                sale_domain = eval(profile.sale_domain, globals(), locals())
            except (NameError, TypeError) as e:
                self.raise_user_error('sale_domain_searcher_error',
                    error_args=(e,),
                    error_description='sale_domain_searcher_help')
            sales = Sale.search(sale_domain)

            if sales:
                if profile.sale_state:
                    try:
                        state_domain = eval(profile.sale_state, globals(),
                            locals())
                    except (NameError, TypeError) as e:
                        self.raise_user_error('sale_state_filter_error',
                            error_args=(e,),
                            error_description='sale_state_filter_help')
                    state_domain.extend([('id', 'in', [s.id for s in sales])])
                    sales = Sale.search(state_domain)
                    if not sales:
                        log_value = {
                            'date_time': datetime.now(),
                            }
                        log_value['comment'] = self.raise_user_error(
                            'state_match_error',
                            error_args=(sale_domain, state_domain),
                            raise_exception=False)
                        log_value['status'] = 'skipped'
                        log_values.append(log_value)
                        continue

                if profile.sale_amount:
                    try:
                        amount_filter = eval(profile.sale_amount, globals(),
                            locals())
                    except (NameError, TypeError) as e:
                        self.raise_user_error('sale_amount_filter_error',
                            error_args=(e,),
                            error_description='sale_amount_filter_help')
                    amount_filter.extend([('id', 'in', [s.id for s in sales])])
                    sales = Sale.search(amount_filter)
                    if not sales:
                        log_value = {
                            'date_time': datetime.now(),
                            }
                        log_value['comment'] = self.raise_user_error(
                            'sale_amount_match_error',
                            error_args=(sale_domain, state_domain),
                            raise_exception=False)
                        log_value['status'] = 'skipped'
                        log_values.append(log_value)
                        continue

            else:
                log_value = {
                    'date_time': datetime.now(),
                    }
                log_value['comment'] = self.raise_user_error(
                    'sale_not_found_error',
                    error_args=(sale_domain,),
                    raise_exception=False)
                log_value['status'] = 'skipped'
                log_values.append(log_value)
                continue
            if len(sales) > 1:
                log_value = {
                    'date_time': datetime.now(),
                    }
                log_value['comment'] = self.raise_user_error(
                    'sale_too_match_error',
                    error_args=(sale_domain,),
                    raise_exception=False)
                log_value['status'] = 'skipped'
                log_values.append(log_value)
                continue
            sale, = sales
            Sale.workflow_to_end([sale])

            values['write_off'] = Decimal('0.0')
            if sale.total_amount_cache != values['amount']:
                values['write_off'] = (sale.total_amount_cache -
                    values['amount'])

            log_value = {
                'date_time': datetime.now(),
                }
            log_value['comment'] = ('Sale %s found.' % sale.reference)
            log_value['status'] = 'done'
            log_values.append(log_value)
            log_value = {
                'date_time': datetime.now(),
                }

            account = (sale.party.account_receivable
                and sale.party.account_receivable.id
                or self.raise_user_error('party_without_account_receivable',
                    error_args=(sale.party.name,)))

            values['party'] = sale.party.id
            values['account'] = account
            values['sale'] = sale.id
            if 'date' not in values:
                values['date'] = Date.today()

            log_value = {
                'date_time': datetime.now(),
                }
            log_value['comment'] = ('Statement line of party %s and sale %s '
                'added.' % (sale.party.name, sale.reference))
            log_value['status'] = 'done'
            log_values.append(log_value)

            vlist.append(values)
            sales_found.append(sale)

        statements = Statement.search([
                ('journal', '=', profile.journal),
                ('state', '=', 'draft'),
                ], order=[
                ('create_date', 'DESC'),
                ], limit=1)
        if not statements:
            statements = Statement.search([
                    ('journal', '=', profile.journal),
                    ('state', '!=', 'cancel'),
                    ], order=[
                    ('create_date', 'DESC'),
                    ], limit=1)
            if statements:
                start_balance = statements[0].end_balance
            else:
                start_balance = Decimal('0.0')
            statements = Statement.create([{
                        'name': '%s %s' % (profile.journal.name,
                            datetime.now()),
                        'journal': profile.journal,
                        'start_balance': start_balance,
                        'end_balance': Decimal('0.0'),
                        }])
        statement, = statements

        for values in vlist:
            values['statement'] = statement.id

        if any([v['write_off'] for v in vlist]):
            write_off_statements = Statement.search([
                    ('journal', '=', profile.write_off_journal),
                    ('state', '=', 'draft'),
                    ], order=[
                    ('create_date', 'DESC'),
                    ], limit=1)
            if not write_off_statements:
                write_off_statements = Statement.search([
                        ('journal', '=', profile.write_off_journal),
                        ('state', '!=', 'cancel'),
                        ], order=[
                        ('create_date', 'DESC'),
                        ], limit=1)
                if write_off_statements:
                    start_balance = write_off_statements[0].end_balance
                else:
                    start_balance = Decimal('0.0')
                write_off_statements = Statement.create([{
                            'name': '%s %s' % (profile.write_off_journal.name,
                                datetime.now()),
                            'journal': profile.write_off_journal,
                            'start_balance': start_balance,
                            'end_balance': Decimal('0.0'),
                            }])
            write_off_statement, = write_off_statements
            write_off_vlist = []
            for values in vlist:
                if not values['write_off']:
                    continue
                write_off_values = {k: v for k, v in values.items()}
                write_off_values['amount'] = write_off_values.pop('write_off')
                write_off_values['statement'] = write_off_statement.id
                write_off_vlist.append(write_off_values)

            StatementLine.create(write_off_vlist)

        for values in vlist:
            values.pop('write_off')
        StatementLine.create(vlist)

        Sale.workflow_to_end(sales_found)

        if attach:
            attachment = Attachment(
                name=datetime.now().strftime('%y/%m/%d %H:%M:%S'),
                type='data',
                data=import_file,
                resource=str(statement))
            attachment.save()

        for log_value in log_values:
            log_value['origin'] = 'account.statement,%s' % statement.id
        ImportCSVLog.create([{
                'date_time': datetime.now(),
                'origin': 'account.statement,%s' % statement.id,
                'comment': '%s %s' % (statement.name, statement.date),
                'status': 'done',
                'children': [
                    ('create', log_values),
                    ],
                }])

        return 'end'
