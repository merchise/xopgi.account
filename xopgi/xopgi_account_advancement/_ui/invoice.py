#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from __future__ import division, print_function, absolute_import

import json
from xoeuf import api, fields, models
from odoo import _


PRECOLLECTION_TITLE = _("Pre-collections")
PREPAYMENT_TITLE = _("Pre-payments")


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    advance_credits_debits_widget = fields.Text(
        compute='_get_advance_accounts_info_JSON'
    )
    has_advancements = fields.Boolean(
        compute='_get_advance_accounts_info_JSON',
    )

    @api.one
    def _get_advance_accounts_info_JSON(self):
        if self.type not in ('out_invoice', 'in_invoice'):
            # TODO: Deal with refunds later.
            self.advance_credits_debits_widget = json.dumps(False)
            self.has_advancements = False
            return
        advacements = []
        if self.state == 'open':
            accounts = self._get_advancement_accounts()
            for pre_account in accounts:
                if not pre_account.currency_id or pre_account.currency_id == self.currency_id:
                    amount = abs(self._credit_debit_get(pre_account.id))
                    if amount:
                        advacements.append({
                            'id': pre_account.id,
                            'journal_name': pre_account.name,
                            'amount': amount,
                            'max_reduction': min(self.residual, amount),
                            'currency_symbol': self.currency_id.symbol,
                            'position': self.currency_id.position,
                            # TODO: What does 69 mean?
                            'digits': [69, self.currency_id.decimal_places],
                        })
        if advacements:
            if self.type == 'out_invoice':
                title = PRECOLLECTION_TITLE
            elif self.type == 'in_invoice':
                title = PREPAYMENT_TITLE
            data = {
                'title': title,
                'content': advacements,
                'invoice_id': self.id,
                'partner_id': self.partner_id.id
            }
            self.advance_credits_debits_widget = json.dumps(data)
            self.has_advancements = True
        else:
            self.advance_credits_debits_widget = json.dumps(False)
            self.has_advancements = False
