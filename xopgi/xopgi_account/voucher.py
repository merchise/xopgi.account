# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi.xopgi_account.invoice
# ---------------------------------------------------------------------
# Copyright (c) 2013-2016 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2013-12-27

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

from openerp.osv import fields
from openerp.osv.orm import Model
import openerp.addons.account_voucher.account_voucher as base_account_voucher


class account_voucher_line(Model):
    '''Adds an invoice reference to the voucher line.

    '''
    _name = str('account.voucher.line')
    _inherit = str('account.voucher.line')
    _columns = {
        'invoice':
            fields.related('move_line_id', 'invoice', 'origin', type='char',
                           size=64, string='Invoice'),
        'invoice_partner':
            fields.related('move_line_id', 'invoice', 'partner_id',
                           relation='res.partner',
                           type='many2one', string='Invoice Partner')
    }


class account_voucher(Model):
    '''Cleans the journal and period fields when the company changes.

    This avoids errors. Since a voucher requires both the journal and the
    period, but those are (probably) linked to the company, selecting a new
    company will most likely imply chosing other journal and period.

    '''
    _name = base_account_voucher.account_voucher._name
    _inherit = _name

    def onchange_company(self, cr, uid, ids, context=None):
        '''Cleans the journal and period when the company changes.'''
        return {'value': {'journal_id': False, 'period_id': False}}

    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id,
                                price, currency_id, ttype, date, context=None):
        '''Computes the `invoice` related field for the voucher line.

        For each credit and debit line, simply fills the `invoice` column.

        This method is called by the OpenERP's voucher addon, specifically in
        the onchange_amount, and onchange_partner_id.

        It also cleans amount assignment cause it's more usable.

        '''
        from xoutil.objects import traverse
        from six.moves import zip
        res = super(account_voucher, self).recompute_voucher_lines(
            cr, uid,
            ids, partner_id, journal_id, price,
            currency_id, ttype, date, context=context
        )
        ml = self.pool['account.move.line']
        for which in ('line_cr_ids', 'line_dr_ids'):
            vlines = [vl for vl in res['value'][which]
                      # In some cases the vl may hold a "command" tuple for
                      # removing lines.
                      if isinstance(vl, dict)]
            ids = [vl['move_line_id'] for vl in vlines]
            for line, mline in zip(vlines, ml.browse(cr, uid, ids)):
                invoice_partner = traverse(
                    mline,
                    'invoice.partner_id.id',
                    default=None,
                    getter=getattr
                )
                if invoice_partner:
                    line['invoice_partner'] = (invoice_partner, 'res.partner')
                else:
                    line['invoice_partner'] = None
                line['invoice'] = traverse(
                    mline,
                    'invoice.origin',
                    default='',
                    getter=getattr
                )
        return res
