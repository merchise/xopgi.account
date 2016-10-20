#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_normal_balance.account
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
from openerp.osv.orm import Model

import openerp.addons.account as base_account

from xoeuf.osv.orm import get_modelname


DEBIT_NORMAL_BALANCE = str('debit')
CREDIT_NORMAL_BALANCE = str('credit')

DEBIT_BALANCE_ACCOUNTS = (str('asset'), str('expense'))
CREDIT_BALANCE_ACCOUNTS = (str('liability'), str('income'), str('equity'))


class xopgi_account_account(Model):
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
    _name = get_modelname(base_account.account.account_account)
    _inherit = _name

    def _get_normal_balance(self, cr, uid, ids, field, args, context=None):
        '''Functional field gutter for ``normal_balance``.'''
        from xoutil.eight import integer_types
        res = {}
        if isinstance(ids, integer_types):
            ids = [ids]
        for account in self.browse(cr, uid, ids, context=context):
            if account.user_type.report_type in DEBIT_BALANCE_ACCOUNTS:
                res[account.id] = DEBIT_NORMAL_BALANCE
            elif account.user_type.report_type in CREDIT_BALANCE_ACCOUNTS:
                res[account.id] = CREDIT_NORMAL_BALANCE
            else:
                res[account.id] = False
        return res

    _columns = {
        str('normal_balance'):
            fields.function(
                _get_normal_balance, method=True, type='char',
                size=64, string='Normal balance', store=True,
                help='Identifies the normal balance of the '
                'account.  An account has either "credit" or '
                '"debit" normal balance.  An account with '
                'credit normal balance increases its value '
                'by credits; an account with debit normal balance '
                'increases its value by debits.'),
    }
