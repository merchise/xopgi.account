# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi.xopgi_account.statement
# ---------------------------------------------------------------------
# Copyright (c) 2013-2015 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2013-11-30

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

from openerp.osv.orm import Model
import openerp.addons.account.account_bank_statement as base

from six import integer_types
from xoeuf.osv.orm import get_modelname


class account_bank_statement(Model):
    '''An account bank statement.

    '''
    _name = get_modelname(base.account_bank_statement)
    _inherit = _name

    def onchange_journal_id(self, cr, uid, statement_id, journal_id,
                            context=None):
        '''When the journal changes the period must be refreshed.

        The period is selected according to the journal's company period for
        the selected date.

        '''
        _super = super(account_bank_statement, self).onchange_journal_id
        context = context if context or context == {} else {}
        res = _super(cr, uid, statement_id, journal_id, context=context)
        values = res.setdefault('value', {})
        company = values.get('company_id', False)
        if company:
            if not isinstance(company, integer_types):
                # In Odoo it will the int and not the tuple... Anyways this is
                # safe in cases you get either the int or the (int, str).
                company_id = company[0]
            else:
                company_id = company
            domain = res.setdefault('domain', {})
            domain['period_id'] = [('company_id', '=', company_id)]
            period_context = dict(context, company_id=company_id)
            values['period_id'] = self._get_period(cr, uid,
                                                   context=period_context)
        return res
