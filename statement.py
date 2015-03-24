# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from datetime import datetime
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Button, StateTransition, StateView, Wizard


__all__ = ['PaymentFromSaleImportCSVStart', 'PaymentFromSaleImportCSV']
__metaclass__ = PoolMeta


class PaymentFromSaleImportCSVStart(ModelView):
    'Payment From Sale Import CSV Start'
    __name__ = 'import.csv.payment.from.sale.start'
    profile = fields.Many2One('profile.csv', 'Profile CSV', required=True)
    import_file = fields.Binary('Import File', required=True)
    attach = fields.Boolean('Attach File',
        help='Attach CSV file after import.')

    @classmethod
    def default_profile(cls):
        Profile = Pool().get('profile.csv')
        profiles = Profile.search([])
        if len(profiles) == 1:
            return profiles[0].id

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
                'csv_format_error': 'Please, check that the Statement CSV '
                    'configuration matches with the format of the CSV file.',
                'no_sales_found': 'No sales found for this csv file.',
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
        import_file = self.start.import_file
        has_header = profile.header
        attach = self.start.attach

        data = profile.read_csv_file(import_file)

        if has_header:
            next(data, None)

        vlist = []
        found_sales = []
        log_values = []
        for row in list(data):
            sale_domain = eval(profile.sale_domain)
            log_value = {}
            sales = Sale.search(sale_domain)
            if not sales:
                log_value['comment'] = ('Sale %s skipped. Not found.' %
                    sale_domain)
                log_value['status'] = 'skipped'
                log_values.append(log_value)
                continue
            elif len(sales) > 1:
                log_value['comment'] = ('Sale %s skipped. Found more than '
                    'once: %s.' % (
                        sale_domain,
                        ' '.join(s.reference for s in sales)
                        )
                    )
                log_value['status'] = 'skipped'
                log_values.append(log_value)
                continue
            sale, = sales
            log_value['comment'] = ('Sale %s found.' % sale.reference)
            log_value['status'] = 'done'
            log_values.append(log_value)

            log_value = {}
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
                log_value['comment'] = ('Statement line %s skipped. Already '
                    'exists.' % statements[0].description)
                log_value['status'] = 'skipped'
                log_values.append(log_value)
                continue

            account = (sale.party.account_receivable
                and sale.party.account_receivable.id
                or self.raise_user_error('party_without_account_receivable',
                    error_args=(sale.party.name,)))

            values['party'] = sale.party.id
            values['account'] = account
            values['sale'] = sale.id
            if 'date' not in values:
                values['date'] = Date.today()

            log_value['comment'] = ('Statement line %s added.' %
                values['description'])
            log_value['status'] = 'done'
            log_values.append(log_value)

            vlist.append(values)
            found_sales.append(sale)

        if found_sales:
            statements = Statement.search([
                    ('journal', '=', profile.journal),
                    ('state', '=', 'draft'),
                    ], order=[
                    ('date', 'DESC'),
                    ], limit=1)
            if not statements:
                self.raise_user_error('not_draft_statement_found')
            statement, = statements

            for values in vlist:
                values['statement'] = statement.id
            StatementLine.create(vlist)
            Sale.workflow_to_end(found_sales)

            if attach:
                attachment = Attachment(
                    name=datetime.now().strftime('%y/%m/%d %H:%M:%S'),
                    type='data',
                    data=import_file,
                    resource=str(statement))
                attachment.save()
        else:
            self.raise_user_error('no_sales_found')

        for log_value in log_values:
            log_value['origin'] = 'account.statement,%s' % statement.id
        ImportCSVLog.create(log_values)

        return 'end'
