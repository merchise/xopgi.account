# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi.xopgi_account.chart
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

from openerp.osv.orm import TransientModel
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
