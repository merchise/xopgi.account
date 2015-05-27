#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# summarize
# ---------------------------------------------------------------------
# Copyright (c) 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-05-27

from openerp.osv import fields, orm


class SummarizeAccountPartnerBalanceWizard(orm.TransientModel):
    """Will launch partner balance report and pass required args"""

    _inherit = "account.common.balance.report"
    _name = "partner.balance.webkit"
    _description = "Summarize Partner Balance Report"

    _columns = {
        'result_selection': fields.selection(
            [('customer', 'Receivable Accounts'),
             ('supplier', 'Payable Accounts'),
             ('customer_supplier', 'Receivable and Payable Accounts')],
            "Partner's", required=True),
        'partner_ids': fields.many2many(
            'res.partner', string='Filter on partner',
            help="Only selected partners will be printed. \
                  Leave empty to print all partners."),
        'amount_currency': fields.boolean("With Currency",
                                          help="It adds the currency column"),
    }

    _defaults = {
        'result_selection': 'customer_supplier',
        'amount_currency': True,
    }

    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(SummarizeAccountPartnerBalanceWizard, self).pre_print_report(
            cr, uid, ids, data, context)
        vals = self.read(
            cr, uid, ids,
            ['result_selection', 'partner_ids', 'amount_currency'],
            context=context
        )[0]
        data['form'].update(vals)
        return data

    def _print_report(self, cursor, uid, ids, data, context=None):
        data = self.pre_print_report(cursor, uid, ids, data, context=context)
        return {'type': 'ir.actions.report.xml',
                'report_name': 'summarize_partner_balance_webkit',
                'datas': data}
