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
from xoeuf.models import get_modelname
from xoeuf.models.proxy import AccountMove as BaseMove


class Move(models.Model):
    _name = get_modelname(BaseMove)
    _inherit = _name

    # Keeps the unbalanced amount of the move.  This is only used to put the
    # *default* debit/credit lines when creating or editing a journal entry.
    #
    # NOTICE that the currency_id is defined in Odoo and that matches the
    # company's currency.
    unbalanced_amount = fields.Monetary(
        compute='_compute_balance',
    )

    @api.multi
    @api.depends('line_ids', 'line_ids.balance')
    def _compute_balance(self):
        for move in self:
            move.unbalanced_amount = sum(move.line_ids.mapped('balance'))
