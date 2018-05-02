#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

'''Settings for the Unrealized Gain/Loss adjustment.

We need:

- A Journal
- An Unrealized Gain Account
- An Unrealized Loss Account

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import api, fields, models

GENERAL_JOURNAL_DOMAIN = [('type', '=', 'general')]
REGULAR_ACCOUNT_DOMAIN = [('user_type_id.type', '=', 'other')]


class Company(models.Model):
    _inherit = "res.company"

    ugl_journal_id = fields.Many2one(
        'account.journal',
        'Unrealized gain & loss journal',
        domain=GENERAL_JOURNAL_DOMAIN,
    )

    ugl_gain_account_id = fields.Many2one(
        'account.account',
        'Unrealized gain account',
        domain=REGULAR_ACCOUNT_DOMAIN,
    )

    ugl_loss_account_id = fields.Many2one(
        'account.account',
        'Unrealized loss account',
        domain=REGULAR_ACCOUNT_DOMAIN,
    )


class AccountConfigSettings(models.TransientModel):
    _inherit = "account.config.settings"

    ugl_journal_id = fields.Many2one(
        related="company_id.ugl_journal_id"
    )

    ugl_gain_account_id = fields.Many2one(
        related="company_id.ugl_gain_account_id"
    )

    ugl_loss_account_id = fields.Many2one(
        related="company_id.ugl_loss_account_id"
    )

    @api.onchange('ugl_journal_id')
    def _update_ugl_gain_and_loss_account(self):
        if not self.ugl_gain_account_id:
            self.ugl_gain_account_id = self.ugl_journal_id.default_credit_account_id
        if not self.ugl_loss_account_id:
            self.ugl_loss_account_id = self.ugl_journal_id.default_debit_account_id
