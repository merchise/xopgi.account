#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi_account.analytic
# ---------------------------------------------------------------------
# Copyright (c) 2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2016-01-06

'''Extends the Analytic Account model in several general ways.

Summary:

- Introduces a `temporarily_open` context manager that ensures analytic
  accounts to be open within the context manager.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import contextlib
from openerp import models, api


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @contextlib.contextmanager
    @api.multi
    def temporarily_open(self):
        '''A context manager where all the accounts in the recordset are
        temporarily reopen if needed.

        Only closed accounts are reopen.  If no account is close, this is a
        no-op.

        If any account in the recordset is cancelled, raise a ValueError.
        Also the recordset must contain only accounts of type: 'normal' or
        'contract', otherwise raise a ValueError.

        The context manager yields the filtered recordset of closed accounts
        that were reopen.

        Usage::

            >>> with accounts.temporarily_open() as closed:
            ...    # Do something with 'accounts'...

        .. note:: No message tracking the temporary change is produced.

        '''
        self.ensure_not_in_state('cancelled')
        self.ensure_type('normal', 'contract')
        closed = self.filtered(lambda account: account.state == 'close')
        closed.with_context(tracking_disable=True).write({'state': 'open'})
        try:
            yield closed
        finally:
            closed.with_context(tracking_disable=True).write({'state': 'close'})

    def ensure_not_in_state(self, *states):
        invalid = self.filtered(lambda account: account.state in states)
        if any(invalid):
            raise ValueError(invalid)

    def ensure_type(self, *types):
        invalid = self.filtered(
            lambda account: account.type not in types)
        if any(invalid):
            raise ValueError(invalid)
