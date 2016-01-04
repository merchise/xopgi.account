# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi.xopgi_account.move
# ---------------------------------------------------------------------
# Copyright (c) 2013-2016 Merchise Autrement
# All rights reserved.
#
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2013-11-30

'''Extensions & fixes for account move lines.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

from openerp.osv.orm import Model
from openerp.addons.account.account import account_move as base_move

from xoeuf.osv.orm import get_modelname


class account_move(Model):
    '''Fixes to account move.'''
    _name = get_modelname(base_move)
    _inherit = _name

    def onchange_journal(self, cr, uid, ids, journal_id, previous_period_id,
                         date, context=None):
        '''Handles the on_change trigger for the journal.

        It takes care of calculating the domain for the period_id and it's
        value.  Also if the currently selected period does not comply with
        it's new domain, it defaults to the period that matches `date` for the
        newly selected journal's company.

        Finally the `company_id` is re-calculated.

        '''
        from openerp.addons.account.account import account_period
        from openerp.addons.account.account import account_journal
        from xoeuf.osv.model_extensions import field_value
        result = {}
        if journal_id:
            journal_obj = self.pool[get_modelname(account_journal)]
            company_id = field_value(journal_obj, cr, uid, journal_id,
                                     'company_id', context=context)
            values = result.setdefault('value', {})
            domains = result.setdefault('domain', {})
            domains['period_id'] = [('company_id', '=', company_id)]
            if previous_period_id:
                period_obj = self.pool[get_modelname(account_period)]
                previous_period = period_obj.browse(
                    cr, uid, previous_period_id, context=context)
                if previous_period.company_id.id != company_id:
                    context = dict(context, company_id=company_id)
                    period_id = period_obj.find(cr, uid, date,
                                                context=context)
                    if isinstance(period_id, list):
                        period_id = period_id[0]
                    values['period_id'] = period_id
            values['company_id'] = company_id
        return result
