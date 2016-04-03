# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi.xopgi_account.invoice
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

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _absolute_import)

from openerp.osv.orm import TransientModel
from openerp.release import version_info as ODOO_VERSION_INFO


class account_invoice_refund(TransientModel):
    '''An invoice refund.

    Restricts the journals to those belonging to the selected company.

    '''
    _inherit = 'account.invoice.refund'

    def fields_view_get(self, cr, uid, view_id=None, view_type=False,
                        context=None, toolbar=False, submenu=False):
        '''The ORM calls this method when the view is being shown.'''
        context = context or {}
        _super = super(account_invoice_refund, self).fields_view_get
        res = _super(cr, uid,
                     view_id=view_id, view_type=view_type, context=context,
                     toolbar=toolbar, submenu=submenu)
        if ODOO_VERSION_INFO < (9, 0):
            # TODO: Verify if this is needed in Odoo 9.  This only applicable
            # for multi-company scenarios.
            journal = self.pool.get('account.journal')
            company_id = context.get('invoice_company_id', False)
            journals = res['fields'].get('journal_id', {})
            if company_id and journals:
                def current_company_journal(item):
                    journal_id, _name = item
                    cpn = journal.browse(
                        cr, uid, journal_id, context=context
                    ).company_id
                    return cpn.id == company_id
                journals['selection'] = filter(current_company_journal,
                                               journals['selection'])
        return res
