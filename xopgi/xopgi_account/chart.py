#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''General Accounting extensions - Account model.'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _absolute_import)


from xoeuf import models, MAJOR_ODOO_VERSION


# Odoo 9 has removed the chart of accounts wizard and the fiscal year object.
assert MAJOR_ODOO_VERSION < 9


class account_chart(models.TransientModel):
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
