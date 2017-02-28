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

try:
    from odoo import models, api, _
    from odoo.jobs import Deferred, report_progress, until_timeout
    from odoo.addons.web_celery import WAIT_FOR_TASK
    from odoo.exceptions import ValidationError
except ImportError:
    from openerp import models, api, _
    from openerp.jobs import Deferred, report_progress, until_timeout
    from openerp.addons.web_celery import WAIT_FOR_TASK
    from openerp.exceptions import ValidationError


try:
    from odoo.addons.web_celery import CLOSE_PROGRESS_BAR
except ImportError:
    try:
        from openerp.addons.web_celery import CLOSE_PROGRESS_BAR
    except ImportError:
        CLOSE_PROGRESS_BAR = None


class ValidateInvoice(models.Model):
    _inherit = _name = 'account.invoice'

    @api.multi
    def invoice_open_with_celery(self):
        return WAIT_FOR_TASK(Deferred(self._do_validate))

    @api.multi
    def _do_validate(self):
        # Do the real work inside an iterator so that we can use the
        # until_timeout.
        def _validate():
            report_progress(
                _("Validating the invoices. This may take several "
                  "minutes depending on the length of the invoices "),
                valuemin=0,
                valuemax=len(self)
            )
            records = self.sorted(lambda invoice: len(invoice.invoice_line))
            for progress, record in enumerate(records):
                report_progress(progress=progress)
                with self.env.cr.savepoint():
                    # Since the soft time-limit may occur after the first
                    # invoice was validate, but before the second finishes, we
                    # must ensure all DB changes for each invoice is
                    # 'atomically' done or not done at all.
                    record.signal_workflow('invoice_open')
                yield record

        res = list(until_timeout(_validate()))
        if not res and any(self):
            raise ValidationError(_("No invoice could be validated"))
        else:
            return CLOSE_PROGRESS_BAR


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
