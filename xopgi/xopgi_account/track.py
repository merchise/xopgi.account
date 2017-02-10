#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# partner
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-02-01

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _setup_complete(self):
        # Instead of rewriting the columns, we simply add the required
        # attribute to the fields after the model is properly setup.
        # TODO: This is kind of a hack... but rewriting the entire column just
        # to add a metadata-like attribute seems overreaching.
        super(ResPartner, self)._setup_complete()
        for field in ('property_account_receivable',
                      'property_account_receivable'):
            self._fields[field].track_visibility = 'onchange'
