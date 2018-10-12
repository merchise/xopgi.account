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

from xoeuf import models, api
from xoeuf.odoo import _
from xoeuf.odoo.jobs import Deferred, report_progress, until_timeout
from xoeuf.odoo.addons import web_celery
from xoeuf.odoo.addons.web_celery import WAIT_FOR_TASK
from xoeuf.odoo.exceptions import ValidationError


QUIETLY_WAIT_FOR_TASK = getattr(web_celery, 'QUIETLY_WAIT_FOR_TASK',
                                WAIT_FOR_TASK)

CLOSE_PROGRESS_BAR = getattr(web_celery, 'CLOSE_FEEDBACK', None)


def get_lines(move):
    return move.line_ids


def perform_post(move):
    move.post()


class ValidateMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post_with_celery(self):
        return QUIETLY_WAIT_FOR_TASK(Deferred(self._do_post_with_celery))

    @api.multi
    def _do_post_with_celery(self):
        # Do the real work inside an iterator so that we can use the
        # until_timeout.
        def _validate():
            report_progress(
                _("Posting the entries. This may take several "
                  "minutes depending on the length of the entries."),
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
                    perform_post(record)
                yield record

        def count(iterable):
            result = 0
            for _x in iterable:  # noqa: F402
                result += 1
            return result

        res = count(until_timeout(_validate()))
        if not res:
            raise ValidationError(_("No entry could be posted"))
        else:
            return CLOSE_PROGRESS_BAR
