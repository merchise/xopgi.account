#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# invoice
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-02-27

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf.ui import CLOSE_WINDOW

from xoeuf import models, api
from xoeuf.odoo.jobs import Deferred
from xoeuf.odoo.addons import web_celery
from xoeuf.odoo.addons.web_celery import WAIT_FOR_TASK


QUIETLY_WAIT_FOR_TASK = getattr(web_celery, 'QUIETLY_WAIT_FOR_TASK',
                                WAIT_FOR_TASK)

CLOSE_PROGRESS_BAR = getattr(web_celery, 'CLOSE_FEEDBACK', None)


class ValidateInvoice(models.Model):
    _inherit = _name = 'account.invoice'

    @api.multi
    def invoice_open_with_celery(self):
        return QUIETLY_WAIT_FOR_TASK(Deferred(self._do_validate))

    # _do_validate implemented per major Odoo version in invoice8 and
    # invoice10.


class ConfirmInvoices(models.TransientModel):
    _name = _inherit = 'account.invoice.confirm'

    @api.multi
    def invoice_confirm_with_celery(self):
        invoice_ids = self.env.context.get('active_ids', []) or []
        invoices = self.env['account.invoice'].browse(invoice_ids).filtered(
            lambda invoice: invoice.state in ('draft', 'proforma', 'proforma2')
        )
        if any(invoices):
            return invoices.invoice_open_with_celery()
        else:
            return CLOSE_WINDOW
