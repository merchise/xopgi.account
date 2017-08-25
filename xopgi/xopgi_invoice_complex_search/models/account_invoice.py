# -*- coding: utf-8 -*-
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    partner_tags = fields.Many2many(related='partner_id.category_id',
                                    string="Partner's Tags")
