# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['ProfileCSV', 'ImportCSVLog']


class ProfileCSV:
    __metaclass__ = PoolMeta
    __name__ = 'profile.csv'
    journal = fields.Many2One('account.statement.journal',
        'Account Statement Journal')
    write_off_journal = fields.Many2One('account.statement.journal',
        'Write Off Statement Journal')
    sale_domain = fields.Char('Sale Domain Searcher',
        help="Tryton's domain [1] for searching sales which match with "
            "statement lines. You can use these variables:\n"
            " * values: Dictionary with values mapped on the columns of the "
            "csv profile.\n"
            " * row: List with the values of the csv file. This variable can "
            "not process other values than Char type.\n"
            "For instance:\n"
            "[('reference', '=', row[4])]"
            "[1] http://trytond.readthedocs.org/en/latest/topics/domain.html.")
    sale_state = fields.Char('Sale State Filter',
        help="Tryton's domain [1] for searching sales which match with "
            "statement lines. You can use these variables:\n"
            " * values: Dictionary with values mapped on the columns of the "
            "csv profile.\n"
            " * row: List with the values of the csv file. This variable can "
            "not process other values than Char type.\n"
            "For instance:\n"
            "[('state', 'in', ('quotation', 'confirmed', 'processing')), "
            "('invoice_state', 'in', "
            "('draft', 'validated', 'posted', 'waiting'))]"
            "[1] http://trytond.readthedocs.org/en/latest/topics/domain.html.")
    sale_amount = fields.Char('Sale Amount Filter',
        help="Tryton's domain [1] for searching sales which match with "
            "statement lines. You can use these variables:\n"
            " * values: Dictionary with values mapped on the columns of the "
            "csv profile.\n"
            " * row: List with the values of the csv file. This variable can "
            "not process other values than Char type.\n"
            "For instance:\n"
            "[('total_amount_cache', '>', values['amount'] * Decimal(0.99)), "
            "('total_amount_cache', '<', values['amount'] * Decimal(1.01))]\n"
            "[1] http://trytond.readthedocs.org/en/latest/topics/domain.html.")


class ImportCSVLog:
    __metaclass__ = PoolMeta
    __name__ = 'import.csv.log'

    @classmethod
    def _get_origin(cls):
        return (super(ImportCSVLog, cls)._get_origin() +
            ['account.statement'])
