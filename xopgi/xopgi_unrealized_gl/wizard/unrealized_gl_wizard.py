# -*- coding: utf-8 -*-

import datetime
from openerp import api, fields, models


class UnrealizedGLWizard(models.TransientModel):
    _name = "xopgi.unrealized_gl_wizard"

    def _get_close_date(self):
        return datetime.date.today()

    def _get_valid_currencies(self):
        accounts = self.env["account.account"].search(
            [("currency_id", "!=", False)])
        currencies = []

        for account in accounts:
            if account.currency_id.id not in currencies:
                currencies.append(account.currency_id.id)

        return [("id", "in", currencies)]

    def _get_currency(self):
        return self.env["res.currency"].search(self._get_valid_currencies(),
                                               limit=1)

    def _get_journal(self):
        return self.env["account.config.settings"].search(
            [("company_id", "=", self.env.user.company_id.id)],
            limit=1).ugl_journal_id

    def _get_gain_account(self):
        return self.env["account.config.settings"].search(
            [("company_id", "=", self.env.user.company_id.id)],
            limit=1).ugl_gain_account_id

    def _get_loss_account(self):
        return self.env["account.config.settings"].search(
            [("company_id", "=", self.env.user.company_id.id)],
            limit=1).ugl_loss_account_id

    close_date = fields.Date(string="Close Date", required=True,
                             default=_get_close_date)

    currency_id = fields.Many2one("res.currency", "Currency", required=True,
                                  default=_get_currency,
                                  domain=_get_valid_currencies)

    currency_rate = fields.Float(string="Currency Rate", required=True,
                                 digits=(6, 6))

    journal_id = fields.Many2one("account.journal", string="Journal",
                                 required=True,
                                 domain=[('type', '=', 'general')],
                                 default=_get_journal, readonly=True)

    gain_account_id = fields.Many2one("account.account", string="Gain Account",
                                      required=True,
                                      domain=[('type', '=', 'other')],
                                      default=_get_gain_account, readonly=True)

    loss_account_id = fields.Many2one("account.account", string="Loss Account",
                                      required=True,
                                      domain=[('type', '=', 'other')],
                                      default=_get_loss_account, readonly=True)

    @api.onchange("close_date", "currency_id")
    def _onchange_close_date(self):
        if any(self.currency_id):
            self.currency_rate = self.currency_id.rate_ids.search(
                [("currency_id", "=", self.currency_id.id),
                 ("name", "<=", self.close_date)], limit=1,
                order="name desc").rate

    @api.multi
    def generate(self):
        if self.currency_rate <= 0:
            return False
        accounts = self.env["account.account"].search(
            [("currency_id", "=", self.currency_id.id)])
        period = self.env["account.period"].get_period_by_date(
            fields.Date.from_string(self.close_date)).id
        for account in accounts:
            if account.type == "view":
                continue
            ugl = self.get_ugl_data(account)
            if ugl == 0:
                continue
            main_line = self.env["account.move.line"].search(
                [("account_id", "=", account.id),
                 ("move_id.to_be_reversed", "=", True)], limit=1)
            if any(main_line):
                main_move = self.env["account.move"].browse(
                    [main_line.move_id.id])
                main_move.reverse_and_reconcile_move(
                    fields.Date.from_string(self.close_date))
                ugl = self.get_ugl_data(account)
            move = self.env["account.move"].create(
                {"name": "UGL-" + self.close_date,
                 # "company_id": self.env.user.company_id.id,
                 "journal_id": self.journal_id.id,  # "state": "draft",
                 "period_id": period, "date": self.close_date,
                 "to_be_reversed": True})
            if ugl == 0:
                continue
            if ugl > 0:
                self.env["account.move.line"].create(
                    {"name": "UGL-" + self.close_date,
                     "account_id": self.gain_account_id.id,
                     "credit": abs(ugl), "move_id": move.id})
                self.env["account.move.line"].create(
                    {"name": "UGL-" + self.close_date,
                     "account_id": account.id,
                     "debit": abs(ugl), "move_id": move.id,
                     "amount_currency": 0,
                     "currency_id": account.currency_id.id})
            else:
                self.env["account.move.line"].create(
                    {"name": "UGL-" + self.close_date,
                     "account_id": self.loss_account_id.id,
                     "debit": abs(ugl), "move_id": move.id})
                self.env["account.move.line"].create(
                    {"name": "UGL-" + self.close_date,
                     "account_id": account.id,
                     "credit": abs(ugl), "move_id": move.id,
                     "amount_currency": 0,
                     "currency_id": account.currency_id.id})

    def get_ugl_data(self, account):
        full_ugl = account._account_account__compute(
            field_names=('credit', 'debit', 'balance', 'foreign_balance',
                         'adjusted_balance', 'unrealized_gain_loss'),
            query="l.date <= '" + self.close_date + "'")
        account_ugl = full_ugl[account.id]
        ugl = account_ugl["foreign_balance"] / self.currency_rate - \
              account_ugl["balance"]
        return ugl
