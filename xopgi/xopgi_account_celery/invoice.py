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


from xoeuf.ui import RELOAD_UI

try:
    from odoo import models, api, _
    from odoo.jobs import Deferred, report_progress
    from odoo.addons.web_celery import WAIT_FOR_TASK
except ImportError:
    from openerp import models, api, _
    from openerp.jobs import Deferred, report_progress
    from openerp.addons.web_celery import WAIT_FOR_TASK


class ValidateInvoice(models.Model):
    _inherit = _name = 'account.invoice'

    @api.multi
    def invoice_open_with_celery(self):
        return WAIT_FOR_TASK(Deferred(self._do_validate))

    @api.multi
    def _do_validate(self):
        report_progress(
            _("Validating the invoices. This may take several "
              "minutes depending on the length of the invoices "),
            valuemin=0,
            valuemax=len(self)
        )
        for progress, record in enumerate(self):
            report_progress(progress=progress)
            record.signal_workflow('invoice_open')
        return RELOAD_UI
