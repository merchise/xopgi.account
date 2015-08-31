# -*- coding: utf-8 -*-

from openerp import fields, models


class Company(models.Model):
    _inherit = "res.company"

    ugl_journal_id = fields.Many2one('account.journal',
                                     'Unrealized gain & loss journal',
                                     domain=[('type', '=', 'general')])

    ugl_gain_account_id = fields.Many2one('account.account',
                                          'Unrealized gain account',
                                          domain=[('type', '=', 'other')])

    ugl_loss_account_id = fields.Many2one('account.account',
                                          'Unrealized loss account',
                                          domain=[('type', '=', 'other')])


class AccountConfigSettings(models.TransientModel):
    _inherit = "account.config.settings"

    ugl_journal_id = fields.Many2one(related="company_id.ugl_journal_id")

    ugl_gain_account_id = fields.Many2one(
        related="company_id.ugl_gain_account_id")

    ugl_loss_account_id = fields.Many2one(
        related="company_id.ugl_loss_account_id")
