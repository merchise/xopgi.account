#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xopgi.account.post
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-03-18

'''Allows to post several moves in a single click.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp.models import TransientModel


class PostMoveConfirmation(TransientModel):
    _name = 'xopgi.account.move.confirm'

    def post(self, cr, uid, ids, context=None):
        Move = self.pool['account.move']
        return Move.button_validate(cr, uid, context['active_ids'],
                                    context=context)
