#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import logging
from datetime import date as Date

from xoeuf import models, api, fields
from xoeuf.tools import normalize_date

logger = logging.getLogger()


class DebugReopenedInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def write(self, vals):
        today = normalize_date(fields.Date.today())
        try:
            date = max(
                normalize_date(d)
                for d in self.mapped('date_invoice')
                if d
            )
        except ValueError:
            date = normalize_date(fields.Date.today())
        old = date < Date(2018, 2, 1)
        closed_before = len(self.filtered(lambda i: i.state == 'paid'))
        res = super(DebugReopenedInvoice, self).write(vals)
        closed_after = len(self.filtered(lambda i: i.state == 'paid'))
        if old and closed_before > closed_after:
            logger.error(
                'Reopening old invoices %r: UID: %r.',
                self.mapped('number'),
                self.env.uid,
                extra=dict(stack=True),
            )
        return res
