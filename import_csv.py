# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['ProfileCSV']
__metaclass__ = PoolMeta


class ProfileCSV:
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
            "As a example:\n["
            "('reference', '=', row[4]), "
            "('total_amount_cache', '>', values['amount'] * Decimal(0.99)), "
            "('total_amount_cache', '<', values['amount'] * Decimal(1.01)), "
            "('state', 'not in', ['cancel', 'done'])]\n\n"
            "[1] http://trytond.readthedocs.org/en/latest/topics/domain.html.")
