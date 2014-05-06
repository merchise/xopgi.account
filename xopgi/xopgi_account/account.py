# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xopgi.xopgi.xopgi_account.account
#----------------------------------------------------------------------
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


CONSOLIDATE_CHART = 'consolidate'
AGGREGATED_CHART = 'aggregate'


class account_chart(TransientModel):  # pylint: disable=W0223
    '''Wizard for "Chart of Accounts".

    Extended in `Xopgi` for decided if is ``aggregate`` (standard variant of
    ``OpenERP``: sum all operations), and add ``consolidate`` (remove internal
    operations between companies from holdings).

    This must be migrated to a configurable implementation to decide which
    companies are or not holdings of the kind that can use this tool.

    This migration process must be decided when the definitive implementation
    of the structure of "Cuba Autrement" as a concept is done. If this feature
    is general (that can be used for any kind of business) must stay in
    `Xopgi`, else must be moved to ``xhg.autrement`` or ``xhg.ca``.

    '''
    _name = get_modelname(base_account.wizard.account_chart.account_chart)
    _inherit = _name
    _columns = {
        'chart_mode':
            fields.selection([(AGGREGATED_CHART, 'Aggregate'),
                              (CONSOLIDATE_CHART, 'Consolidate')],
                             'Chart mode',
                             help='You may select "Aggregate" for standard '
                             'chart: ie. all journal items are '
                             'displayed. Consolidated charts exclude journal '
                             'items between companies of the same holding. '
                             'Use the "Consolidate" only for Holdings.')
    }

    _defaults = {
        'chart_mode': AGGREGATED_CHART
    }

    def account_chart_open_window(self, cr, uid, ids, context=None):
        '''Redefine super :meth:`account_chart_open_window` in order to update the
        context with the selected chart mode to be recovered in the wizard.

        Also define that a symbol of currency is used instead the ISO acronym.

        The updated context is used in :meth:`res_currency.name_get`.

        See
        :meth:`xopgi.addons.xopgi_account.move.account_move_line._query_get`
        for more info.

        '''
        from xoeuf.osv.model_extensions import field_value
        _super = super(account_chart, self).account_chart_open_window
        result = _super(cr, uid, ids, context=context)
        res_context = result.get('context')
        if res_context:
            ctx = eval(res_context)
            chart_mode = field_value(self, cr, uid, ids[0], 'chart_mode',
                                     context=context)
            if chart_mode == CONSOLIDATE_CHART:
                ctx.update({str('consolidate'): True})
            ctx.update({str('currency_symbol'): True})
            result['context'] = repr(ctx)
        return result

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
        # TODO: Find out what happens when a single company (not multicompany)
        # is being used. Is this code general enough for both cases?
        company_id = field_value(model, cr, uid, fiscalyear_id, 'company_id',
                                 context=context)
        if company_id:
            domain = result.setdefault('domain', {})
            domain.setdefault('period_from', [('company_id', '=', company_id)])
            domain.setdefault('period_to', [('company_id', '=', company_id)])
        return result


DEBIT_NORMAL_BALANCE = str('debit')
CREDIT_NORMAL_BALANCE = str('credit')


class xopgi_account_account(Model):
    '''Add the field ``normal_balance`` to the standard `OpenERP` base class to
    manage account's `Normal balance`_ [#cuba]_.

    In the `double-entry bookkeeping system`_, an account has either «credit»
    or «debit» normal balance.

    - To increase the value of an account with normal balance of credit, one
      would credit the account.

    - To increase the value of an account with normal balance of debit, one
      would likewise debit the account.

    This is directly applicable to «Regular» accounts.  Since this is actually
    inferred from reports types, «view» accounts are also classified, but you'd
    need to be careful when doing that: how would you classify its children
    accounts if reported separately?

    See field "sign"`` help in model
    :mod:`openerp.addons.account.account_financial_report` for more info.

    This new field must be used when a balance be calculated.

    .. _Normal balance: http://en.wikipedia.org/wiki/Normal_balance
    .. _double-entry bookkeeping system: http://en.wikipedia.org/wiki/Double-entry_bookkeeping

    .. [#cuba] En Cuba se utiliza la terminología «Cuenta acreedora» para una
       cuenta con balance normal por créditos («credit normal balance») y
       «Cuenta deudora» para una cuenta con balance normal por débitos («debit
       normal balance»).

    '''
    _name = get_modelname(base_account.account.account_account)
    _inherit = _name

    def _get_normal_balance(self, cr, uid, ids, field, args, context=None):
        '''Functional field getter for ``normal_balance``.'''
        res = {}
        for account in self.browse(cr, uid, ids, context=context):
            if account.user_type.report_type in ['asset', 'expense']:
                res[account.id] = DEBIT_NORMAL_BALANCE
            elif account.user_type.report_type in ['liability', 'income']:
                res[account.id] = CREDIT_NORMAL_BALANCE
            else:
                # TODO: False in a type='char' ????
                res[account.id] = False
                # assert account.type = 'view'
        return res

    _columns = {
        str('normal_balance'):
            fields.function(_get_normal_balance, method=True, type='char',
                            size=64, string='Normal balance', store=True,
                            help='Identifies the normal balance of the '
                            'account.  An account has either "credit" or '
                            '"debit" normal balance.  An account with '
                            'credit normal balance increases its value '
                            'by credits; an account with debit normal balance '
                            'increases its value by debits.'),
    }
