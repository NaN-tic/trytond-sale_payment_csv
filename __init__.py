# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .import_csv import *
from .statement import *

def register():
    Pool.register(
        ProfileCSV,
        PaymentFromSaleImportCSVStart,
        module='sale_payment_csv', type_='model')
    Pool.register(
        PaymentFromSaleImportCSV,
        module='sale_payment_csv', type_='wizard')
