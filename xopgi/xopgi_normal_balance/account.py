#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_normal_balance.account
# ---------------------------------------------------------------------
# Copyright (c) 2014-2017 Merchise Autrement [~º/~] and Contributors
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


from xoeuf import fields, models, api


DEBIT_NORMAL_BALANCE = 'debit'
CREDIT_NORMAL_BALANCE = 'credit'

DEBIT_BALANCE_ACCOUNTS = ('asset', 'expense')
CREDIT_BALANCE_ACCOUNTS = ('liability', 'income', 'equity')


class Account(models.Model):
    '''Add the field ``normal_balance`` to manage account's Normal balance.

    In the `double-entry bookkeeping system`_, an account has either «credit»
    or «debit» normal balance.

    - To increase the value of an account with normal balance of credit, one
      would credit the account.

    - To increase the value of an account with normal balance of debit, one
      would likewise debit the account.

    This is directly applicable to «Regular» accounts.  Since this is actually
    inferred from reports types, «view» accounts are also classified, but
    you'd need to be careful when doing that: how would you classify its
    children accounts if reported separately?

    See field "sign" help in model
    :mod:`openerp.addons.account.account_financial_report` for more info.

    This new field must be used when a balance be calculated.

    .. _Normal balance: http://en.wikipedia.org/wiki/Normal_balance
    .. _double-entry bookkeeping system: http://en.wikipedia.org/wiki/Double-entry_bookkeeping

    The `normal_balance` fields is:

    - "debit" for assets, and expenses.

    - "credit" for liabilities, equity and income.

    '''
    _inherit = 'account.account'

    @api.multi
    def _get_normal_balance(self):
        '''Functional field getter for ``normal_balance``.'''
        for account in self:
            if account.user_type.report_type in DEBIT_BALANCE_ACCOUNTS:
                account.normal_balance = DEBIT_NORMAL_BALANCE
            elif account.user_type.report_type in CREDIT_BALANCE_ACCOUNTS:
                account.normal_balance = CREDIT_NORMAL_BALANCE
            else:
                account.normal_balance = ''

    normal_balance = fields.Char(
        compute=_get_normal_balance,
        size=64,
        string='Normal balance',
        store=True,
        help=('Identifies the normal balance of the '
              'account.  An account has either "credit" or '
              '"debit" normal balance.  An account with '
              'credit normal balance increases its value '
              'by credits; an account with debit normal balance '
              'increases its value by debits.')
    )
