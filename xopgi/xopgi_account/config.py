#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    module_xopgi_proper_currency = fields.Boolean(
        'Enter foreign currencies in debit/credit columns.'
    )

    module_xopgi_holdings = fields.Boolean('Manage company holdings.')

    module_xopgi_account_report = fields.Boolean(
        'Add reports for receivables/payables accounts '
        'to sales/purchases staff.'
    )

    module_xopgi_invoice_complex_search = fields.Boolean(
        'Allow invoice search based on partner tags.'
    )

    module_xopgi_account_analytic_enhancement = fields.Boolean(
        'Add view data to analytic accounts.'
    )

    module_xopgi_unrealized_gl = fields.Boolean(
        'Manage unrealized gain & loss.'
    )

    module_xopgi_show_journal_items = fields.Boolean(
        'Show the Journal Items to Accounting Advisers.'
    )
