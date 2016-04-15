#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.account.reconcile
# ---------------------------------------------------------------------
# Copyright (c) 2015, 2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-18


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp.models import TransientModel, Model


class MoveLine(Model):
    _inherit = 'account.move.line'

    def _writeoff_amount(self, cr, uid, ids, context=None):
        '''Calculates the amount to be written-off if we were to reconcile
        lines with `ids`.

        '''
        debit = credit = 0
        for line in self.browse(cr, uid, ids, context=context):
            if line.state == 'valid':
                debit += line.debit
                credit += line.credit
        return debit - credit


class WriteOffWizard(TransientModel):
    _inherit = 'account.move.line.reconcile.writeoff'

    def select_account(self, cr, uid, ids, journal_id, context=None):
        if journal_id:
            writeoff = self.pool['account.move.line']._writeoff_amount(
                cr, uid, context['active_ids'], context=context
            )
            journal = self.pool['account.journal'].browse(cr, uid, journal_id)
            if writeoff < 0:
                # debit < credit, we need to debit the account to be balanced
                # and then credit the write-off account
                account = journal.default_credit_account_id
            else:
                account = journal.default_debit_account_id
            if account:
                return dict(value=dict(writeoff_acc_id=account.id))
        return {}
