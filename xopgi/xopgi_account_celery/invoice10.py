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
from xoeuf.odoo import _
from xoeuf.odoo.jobs import report_progress, until_timeout
from xoeuf.odoo.exceptions import ValidationError

from .base import CLOSE_PROGRESS_BAR


class ValidateInvoice(models.Model):
    _inherit = _name = 'account.invoice'

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
            records = self.sorted(lambda invoice: len(invoice.invoice_line_ids))
            for progress, record in enumerate(records):
                report_progress(progress=progress)
                with self.env.cr.savepoint():
                    # Since the soft time-limit may occur after the first
                    # invoice was validate, but before the second finishes, we
                    # must ensure all DB changes for each invoice is
                    # 'atomically' done or not done at all.
                    record.action_invoice_open()
                yield record

        res = list(until_timeout(_validate()))
        if not res and any(self):
            raise ValidationError(_("No invoice could be validated"))
        else:
            return CLOSE_PROGRESS_BAR
