# -*- coding: utf-8 -*-

from openerp import fields, models


class AccountConfigSettings(models.Model):
    _inherit = "account.config.settings"

    ugl_journal_id = fields.Many2one('account.journal',
                                     'Unrealized gain & loss journal',
                                     domain=[('type', '=', 'general')])

    ugl_gain_account_id = fields.Many2one('account.account',
                                          'Unrealized gain account',
                                          domain=[('type', '=', 'other')])

    ugl_loss_account_id = fields.Many2one('account.account',
                                          'Unrealized loss account',
                                          domain=[('type', '=', 'other')])
