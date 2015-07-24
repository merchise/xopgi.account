# -*- coding: utf-8 -*-


from openerp import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    partner_tags = fields.Many2many(related='partner_id.category_id')


class AccountConfigSetting(models.Model):
    _inherit = 'account.config.settings'

    has_invoice_complex_search = fields.Boolean(
        string= "Allow invoice complex search on partner's Tags.",
        help="Allow invoice complex search on partner's Tags.")