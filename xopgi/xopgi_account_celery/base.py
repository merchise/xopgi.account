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

from xoeuf.ui import CLOSE_WINDOW

from xoeuf import models, api, MAJOR_ODOO_VERSION
from xoeuf.odoo import _
from xoeuf.odoo.jobs import Deferred, report_progress, until_timeout
from xoeuf.odoo.addons import web_celery
from xoeuf.odoo.addons.web_celery import WAIT_FOR_TASK
from xoeuf.odoo.exceptions import ValidationError


QUIETLY_WAIT_FOR_TASK = getattr(web_celery, 'QUIETLY_WAIT_FOR_TASK',
                                WAIT_FOR_TASK)

CLOSE_PROGRESS_BAR = getattr(web_celery, 'CLOSE_FEEDBACK', None)


# The only differences of any importance to us between Odoo 8 and Odoo 9+, is
# how to get the invoice's lines, and how to actually perform the validation.
if MAJOR_ODOO_VERSION == 8:
    def get_lines(invoice):
        return invoice.invoice_line

elif MAJOR_ODOO_VERSION < 11:
    def get_lines(invoice):
        return invoice.invoice_line_ids


if MAJOR_ODOO_VERSION < 10:
    def perform_validate(invoice):
        invoice.signal_workflow('invoice_open')

else:
    def perform_validate(invoice):
        invoice.action_invoice_open()


class ValidateInvoice(models.Model):
    _inherit = _name = 'account.invoice'

    @api.multi
    def invoice_open_with_celery(self):
        return QUIETLY_WAIT_FOR_TASK(Deferred(self._do_validate))

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
            records = self.sorted(lambda invoice: len(get_lines(invoice)))
            for progress, record in enumerate(records):
                report_progress(progress=progress)
                with self.env.cr.savepoint():
                    # Since the soft time-limit may occur after the first
                    # invoice was validate, but before the second finishes, we
                    # must ensure all DB changes for each invoice is
                    # 'atomically' done or not done at all.
                    perform_validate(record)
                yield record

        def count(iterable):
            result = 0
            for _ in iterable:
                result += 1
            return result

        res = count(until_timeout(_validate()))
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
