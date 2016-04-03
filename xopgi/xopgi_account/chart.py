# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi.xopgi_account.chart
# ---------------------------------------------------------------------
# Copyright (c) 2013-2016 Merchise Autrement
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
                        absolute_import as _absolute_import)


from openerp.models import TransientModel


class account_chart(TransientModel):
    '''Wizard for "Chart of Accounts".

    Minor usability fixes:

    - Limit the periods to those of the selected company.

    '''
    _inherit = 'account.chart'

    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id, context=None):
        '''Filter the periods depending on the selected fiscal year.

        Only periods of the same company are allowed.

        '''
        from xoeuf.osv.model_extensions import field_value
        _super = super(account_chart, self).onchange_fiscalyear
        result = _super(cr, uid, ids, fiscalyear_id, context=context)
        model = self.pool['account.fiscalyear']
        company_id = field_value(
            model,
            cr, uid,
            fiscalyear_id, 'company_id',
            context=context
        )
        if company_id:
            domain = result.setdefault('domain', {})
            domain.setdefault(
                'period_from',
                [('company_id', '=', company_id)]
            )
            domain.setdefault(
                'period_to',
                [('company_id', '=', company_id)]
            )
        return result
