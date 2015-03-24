# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta


__all__ = ['ProfileCSV']
__metaclass__ = PoolMeta


class ProfileCSV:
    __name__ = 'profile.csv'
#     margin = fields.Float('Margin', help='Margin of write-off in percentage')
    journal = fields.Many2One('account.statement.journal',
        'Account Statement Journal')
    sale_domain = fields.Char('Sale Domain Searcher')
