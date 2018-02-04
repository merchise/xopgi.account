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

from xoeuf import models, fields, api


class MoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    @api.depends('move_id.line_ids')
    def _compute_counterpart_accounts(self):
        for line in self:
            line.counterpart_account_ids = line.move_id.mapped(
                'line_ids.account_id'
            ).filtered(lambda account: account != line.account_id)

    def _search_counterpart_accounts(self, operator, value):
        # XXX: This will search in any of the accounts (included the line's
        # account).  This is because I can't express the predicate of being
        # not equal to the line's account_id.
        return [('move_id.line_ids.account_id', operator, value)]

    counterpart_account_ids = fields.Many2many(
        'account.account',
        string='Counterpart accounts',
        compute=_compute_counterpart_accounts,
        search=_search_counterpart_accounts,
    )
