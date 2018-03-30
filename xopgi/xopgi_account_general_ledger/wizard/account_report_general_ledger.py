#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from odoo import fields, models


class AccountReportGeneralLedger(models.TransientModel):
    _inherit = "account.report.general.ledger"

    account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Accounts'
    )

    def _print_report(self, data):
        this = self
        if self.account_ids:
            # In case the 'active model' is 'account.account', it shows only
            # those accounts in the general ledger.
            this = self.with_context(
                active_model='account.account',
                active_ids=self.account_ids.ids
            )
        return super(AccountReportGeneralLedger, this)._print_report(data)
