#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_holdings.chart
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-12-18

'''General Accounting extensions - Account model.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp.osv import fields
from openerp.osv.orm import TransientModel
import openerp.addons.account as base_account

from xoeuf.osv.orm import get_modelname


CONSOLIDATE_CHART = 'consolidate'
AGGREGATED_CHART = 'aggregate'


class account_chart(TransientModel):
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
