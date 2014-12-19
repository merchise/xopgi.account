# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi.xopgi_account.account
# ---------------------------------------------------------------------
# Copyright (c) 2013, 2014 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2013-11-11

'''General Accounting extensions - Account model.'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

from openerp.osv import fields
from openerp.osv.orm import Model, TransientModel

import openerp.addons.account as base_account

from xoeuf.osv.orm import get_modelname

class account_chart(TransientModel):
    '''Wizard for "Chart of Accounts".

    Minor usability fixes.

    '''
    _name = get_modelname(base_account.wizard.account_chart.account_chart)
    _inherit = _name

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id, context=None):
        '''Filters the possible periods depending on the selected fiscal year.

        Only periods of the same company are allowed.

        '''
        from openerp.addons.account.account import account_fiscalyear
        from xoeuf.osv.model_extensions import field_value
        _super = super(account_chart, self).onchange_fiscalyear
        result = _super(cr, uid, ids, fiscalyear_id, context=context)
        model_name = get_modelname(account_fiscalyear)
        model = self.pool[model_name]
        company_id = field_value(model, cr, uid, fiscalyear_id, 'company_id',
                                 context=context)
        if company_id:
            domain = result.setdefault('domain', {})
            domain.setdefault('period_from', [('company_id', '=', company_id)])
            domain.setdefault('period_to', [('company_id', '=', company_id)])
        return result


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

    .. [#cuba] En Cuba se utiliza la terminología «Cuenta acreedora» para una
       cuenta con balance normal por créditos («credit normal balance») y
       «Cuenta deudora» para una cuenta con balance normal por débitos («debit
       normal balance»).

    '''
    _name = get_modelname(base_account.account.account_account)
    _inherit = _name

    def _get_normal_balance(self, cr, uid, ids, field, args, context=None):
        '''Functional field gutter for ``normal_balance``.'''
        from six import integer_types
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
                'increases its value by debits.'
            ),
    }
