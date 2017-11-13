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
