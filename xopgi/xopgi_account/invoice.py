# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.xopgi.xopgi_account.invoice
# ---------------------------------------------------------------------
# Copyright (c) 2013-2017 Merchise Autrement [~º/~]
# All rights reserved.
#
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# @created: 2013-11-30

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _absolute_import)

from xoeuf import models, fields


class Invoice(models.Model):
    '''An account invoice.

    Parent's agency field and use it in search view.

    '''
    _inherit = 'account.invoice'

    partner_company = fields.Many2one(
        related='partner_id.parent_id',
        string="Partner's Company",
        store=True
    )
