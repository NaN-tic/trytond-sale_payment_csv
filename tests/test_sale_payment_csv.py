#!/usr/bin/env python
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.tests.test_tryton import test_view, test_depends, doctest_setup, \
    doctest_teardown
import trytond.tests.test_tryton
import unittest
import doctest


class SalePaymentCSVTestCase(unittest.TestCase):
    'Test Sale Payment CSV module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('sale_payment_csv')

    def test0005views(self):
        'Test views'
        test_view('sale_payment_csv')

    def test0006depends(self):
        'Test depends'
        test_depends()


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        SalePaymentCSVTestCase))
    suite.addTests(doctest.DocFileSuite('scenario_sale_payment_csv.rst',
            setUp=doctest_setup, tearDown=doctest_teardown, encoding='utf-8',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
    return suite
