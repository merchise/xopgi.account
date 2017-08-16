#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# settings
# ---------------------------------------------------------------------
# Copyright (c) 2016-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
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

from xoeuf import fields, models


class Company(models.Model):
    _inherit = "res.company"

    ugl_journal_id = fields.Many2one(
        'account.journal',
        'Unrealized gain & loss journal',
        domain=[('type', '=', 'general')]
    )

    ugl_gain_account_id = fields.Many2one(
        'account.account',
        'Unrealized gain account',
        domain=[('type', '=', 'other')]
    )

    ugl_loss_account_id = fields.Many2one(
        'account.account',
        'Unrealized loss account',
        domain=[('type', '=', 'other')]
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
