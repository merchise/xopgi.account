#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import api, models, MAJOR_ODOO_VERSION


if MAJOR_ODOO_VERSION < 9:
    def is_valid(line):
        return line.state == 'valid'
else:
    def is_valid(line):
        # Since Odoo 9+ there's no way to have an invalid move line
        return True


class MoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def _writeoff_amount(self):
        '''Calculates the amount to be written-off if we were to reconcile
        lines with `ids`.

        '''
        debit = credit = 0
        for line in self.filtered(is_valid):
            debit += line.debit
            credit += line.credit
        return debit - credit


class WriteOffWizard(models.TransientModel):
    _inherit = 'account.move.line.reconcile.writeoff'

    @api.multi
    @api.onchange('journal_id')
    def select_account(self):
        if self.journal_id:
            lines = self.env['account.move.line'].browse(self.env.context['active_ids'])
            writeoff = lines._writeoff_amount()
            if writeoff < 0:
                # debit < credit, we need to debit the account to be balanced
                # and then credit the write-off account
                account = self.journal_id.default_credit_account_id
            else:
                account = self.journal_id.default_debit_account_id
            if account:
                self.writeoff_acc_id = account.id
