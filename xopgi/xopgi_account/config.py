#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_account.config
# ---------------------------------------------------------------------
# Copyright (c) 2014-2016 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-12-18

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp.osv import fields
from openerp.models import TransientModel


class AccountConfigSettings(TransientModel):
    _name = 'account.config.settings'
    _inherit = _name

    _columns = {
        'module_xopgi_invisible_tax':
            fields.boolean('Hide account tax column when editing journal '
                           'items.'),

        'module_xopgi_invisible_conciliation':
            fields.boolean('Hides conciliation columns when editing journal '
                           'items.'),

        'module_xopgi_proper_currency':
            fields.boolean('Enter foreign currencies in debit/credit '
                           'columns.'),

        'module_xopgi_holdings':
            fields.boolean('Manage company holdings.'),

        'module_xopgi_account_report':
            fields.boolean('Add reports for receivables/payables accounts '
                           'to sales/purchases staff.'),

        'module_xopgi_invoice_complex_search':
            fields.boolean('Allow invoice search based on partner tags.'),

        'module_xopgi_account_analytic_enhancement':
            fields.boolean('Add view data to analytic accounts.'),

        'module_xopgi_operations_performance':
            fields.boolean('Show reports about operations performance.'),

        'module_xopgi_unrealized_gl':
            fields.boolean('Manage unrealized gain & loss.'),

        'module_xopgi_payment_extension':
            fields.boolean('Set payments enhancements.')
    }
