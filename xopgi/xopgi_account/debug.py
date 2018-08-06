#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import logging
from xoeuf import models, api

logger = logging.getLogger()


class DebugReopenedInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def write(self, vals):
        explicitly_open = vals.get('state', None) == 'open'
        if explicitly_open:
            return super(DebugReopenedInvoice, self).write(vals)
        else:
            closed_before = len(self.filtered(lambda i: i.state == 'paid'))
            res = super(DebugReopenedInvoice, self).write(vals)
            closed_after = len(self.filtered(lambda i: i.state == 'paid'))
            if closed_before > closed_after:
                logger.error(
                    'Reopening invoices %r: UID: %r.',
                    self.mapped('number'),
                    self.env.uid,
                    extra=dict(stack=True),
                )
            return res
