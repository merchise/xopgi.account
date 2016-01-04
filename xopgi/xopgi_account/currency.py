# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_account.currency
# ---------------------------------------------------------------------
# Copyright (c) 2014-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-05-02

'''Changes to currency model.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


from xoeuf.osv.orm import get_modelname

from openerp.addons.base.res.res_currency import res_currency as base
from openerp.osv.orm import Model


class res_currency(Model):
    '''Redefine base `OpenERP` model for currencies to return a proper name
    when ``symbol`` is set in context.

    See above :meth:`account_chart.account_chart_open_window` for more info.

    '''
    _name = get_modelname(base)
    _inherit = _name

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'symbol'], context=context)
        symbol = context.get('currency_symbol')
        key = 'symbol' if symbol else 'name'
        return [(r['id'], r[key]) for r in reads]
