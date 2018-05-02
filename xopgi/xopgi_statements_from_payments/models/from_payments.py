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

from xoeuf import api, fields, models
from xoeuf.osv.orm import CREATE_RELATED

from xoeuf.odoo import _
from xoeuf.odoo.exceptions import UserError


class Payment(models.Model):
    _inherit = 'account.payment'

    should_reconcile_with_statement = fields.Boolean(
        compute='_compute_should_reconcile',
        store=True,
        string="To reconcile",
        help="Payments which are not reconciled with a bank statement",
    )

    @api.multi
    @api.depends('journal_id.default_debit_account_id',
                 'journal_id.default_credit_account_id',
                 'move_line_ids.account_id',
                 'move_line_ids.statement_id',
                 'amount',
                 'state',)
    def _compute_should_reconcile(self):
        for payment in self:
            line = payment._payment_move_line
            journal = payment.journal_id
            journal_accounts = {journal.default_debit_account_id,
                                journal.default_credit_account_id}
            payment.should_reconcile_with_statement = bool(
                payment.amount
                and payment.state not in ('draft', 'reconciled')
                and line
                # This is the equivalente to the SQL query to get the already
                # paid (but not reconciled with statement) move lines in
                # account_bank_statement.py.  Since we know the line comes from
                # this payment.
                and line.partner_id == payment.partner_id
                and not line.statement_id
                and line.account_id in journal_accounts
            )

    @api.from_active_ids
    def _action_create_statement(self):
        statement = self._create_statement()
        return statement.get_formview_action()

    @property
    @api.requires_singleton
    def _payment_move_line(self):
        '''The liquidity move line that matches this payment.

        '''
        result = self.move_line_ids.filtered(
            lambda l: (l.partner_id == self.partner_id
                       and l.account_id.internal_type == 'liquidity'
                       and abs(l.line_currency_amount) == self.amount)
        )
        if len(result) > 1:
            # Payments can touch the same liquidity account because of
            # transference commissions, but it should very strange to have a
            # 100% commission.  If that's the case, we simply don't know which
            # line is the payment line: return the empty recordset.
            return self.env['account.move.line']
        assert not result or result.payment_id == self
        return result

    @api.from_active_ids
    def _create_statement(self):
        '''Create a Bank Statement from payments.

        Each line in the statement will correspond to each payment (self).
        All lines will be conciliated with the corresponding payments.

        The statement is not completed to have starting/ending balances.

        '''
        payments = self.filtered(lambda p: p.should_reconcile_with_statement)
        if not payments:
            raise UserError(_(
                "You must select at least a payment that needs reconciliation"
            ))
        journal = payments.mapped('journal_id')
        if len(journal) > 1:
            raise UserError(_(
                'You cannot create an statement from payments in different '
                'journals.'
            ))
        Statement = self.env['account.bank.statement']
        lines = payments._new_related_statement_lines()
        statement = Statement.create({
            'date': fields.Date.context_today(self),
            'state': 'open',
            'name': _('New bank statement'),
            'journal_id': journal.id,
            'user_id': self.env.user.id,
            'line_ids': lines,
            'balance_start': Statement.with_context(default_journal_id=journal.id)._default_opening_balance()
        })
        statement.line_ids._reconcile_from_payments()
        statement.balance_end_real = statement.balance_end
        return statement

    @api.multi
    def _new_related_statement_lines(self):
        '''Create a match from payments to CREATE_RELATED statement lines.

        '''
        result = []
        for payment in self:
            if payment.amount and payment.should_reconcile_with_statement:
                name = u'{move}: {comm}, {name}'.format(
                    move=payment.move_name,
                    comm=payment.communication,
                    name=payment.name
                )
                result.append(CREATE_RELATED(
                    name=name,
                    date=payment.payment_date,
                    created_from_payment_id=payment.id,
                    amount=(-1 if payment.payment_type == 'outbound' else 1) * payment.amount,
                    partner_id=payment.partner_id.id,
                ))
        return result


class StatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    # In order to be able to efficiently create the statement from the
    # payments I need to keep the relation of each line which the payment that
    # generated it.
    created_from_payment_id = fields.Many2one(
        'account.payment'
    )

    @api.multi
    def _reconcile_from_payments(self):
        self = self.filtered(lambda l: l.created_from_payment_id and l.created_from_payment_id._payment_move_line)
        for line in self:
            line.process_reconciliation(payment_aml_rec=line.created_from_payment_id._payment_move_line)

    @api.multi
    def button_cancel_reconciliation(self):
        # Allow to revert automatic reconciliations of any date.
        automatically_created = self.filtered(
            lambda l: l.created_from_payment_id and l.created_from_payment_id._payment_move_line
        )
        res = super(
            StatementLine,
            automatically_created.with_context(check_move_validity=False)
        ).button_cancel_reconciliation()
        other = self - automatically_created
        if other:
            res = super(StatementLine, other).button_cancel_reconciliation()
        return res
