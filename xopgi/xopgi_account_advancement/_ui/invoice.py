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
        if self._advancements:
            if self.type == 'out_invoice':
                title = PRECOLLECTION_TITLE
            elif self.type == 'in_invoice':
                title = PREPAYMENT_TITLE
            data = {
                'title': title,
                'content': self._advancements,
                'invoice_id': self.id,
                'partner_id': self.partner_id.id
            }
            self.advance_credits_debits_widget = json.dumps(data)
            self.has_advancements = True
        else:
            self.advance_credits_debits_widget = json.dumps(False)
            self.has_advancements = False
