# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.account.misc
# ---------------------------------------------------------------------
# Copyright (c) 2014-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-11-19

'''Other very small fixes.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from openerp.osv.orm import TransientModel


class OpenClosedFiscalYear(TransientModel):
    '''Override the cancel of a closing entry to refresh the page.'''

    _inherit = "account.open.closed.fiscalyear"

    def remove_entries(self, cr, uid, ids, context=None):
        super(OpenClosedFiscalYear, self).remove_entries(
            cr, uid, ids, context=context
        )
        return {
            'type': 'ir.actions.act_window',
            'view': 'form',
            'view_mode': 'tree',
            'res_model': 'account.move',
        }
