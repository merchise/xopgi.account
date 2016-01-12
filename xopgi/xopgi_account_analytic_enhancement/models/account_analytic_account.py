#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# account_analytic_account
# ---------------------------------------------------------------------
# Copyright (c) 2015-2016 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-11-24

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoutil import Unset

from openerp import api, fields, models
from openerp.exceptions import ValidationError

# TODO:  Improve performance.
#
# After a single profiling session on a worker.  We see that most of the time
# is being spent executing queries to the DB (~10s) in 1706 calls, each call
# taking about 0.0059s.  So the thing is trying to make less calls.  But
# that's out of scope for now.
#
# Computed fields are a big performance hog in Odoo.  I haven't found any good
# documentation on the topic about how the `store` option actually works: It
# seems there's no good detection of the 'need for invalidating' the value.
# Cache invalidation is a hard problem.
#
# There are several fields I need to cache for this to be efficient:
#
# - The 4 parameters applicable to each account.  They need to be invalidated
#   whenever any account in the path upwards from the account to the one that
#   provided current value changes one of those parameters.
#
# - The result of margin, commission and the like: They need to invalidated
#   when the balance and/or debit and any of the 4 parameters changes.  This
#   is kind of a chain reaction.  Since balance, debit and credit are also
#   computed (and non-stored) fields.  They change when any journal item
#   (account.move.line) currently attached to the analytic account changes, is
#   deleted or removed from the account or is attached to the account.
#
# We need an efficient signal/reaction algorithm for this to work.  If we cast
# it in terms of production rules, its rules will always be of the type::
#
#     invalidate(*fields) when <conditions>
#
# The conditions may take several forms I'm yet to discover.
#


def _get_from_branch(field_name, default=Unset):
    '''Return a function that will traverse the account's ancestry branch
    looking for the first node in which `field_name` has a non-null value.

    '''
    def _get(record):
        res = getattr(record, field_name, Unset)
        # XXX: Don't test for res is Unset cause we need to traverse the
        # branch when the value is 0
        if not res:
            parent = record.parent_id
            if parent and parent.id:
                return _get(parent)  # recursive to warm the cache
        if res is Unset:
            if default is not Unset:
                return default
            else:
                raise AttributeError(field_name)
        else:
            return res
    return _get


def _compute_from_branch(field_name, update_field_name, default=Unset):
    _get = _get_from_branch(field_name, default=default)

    @api.depends(field_name)
    def _compute(self):
        for record in self:
            setattr(record, update_field_name, _get(record))
    return _compute


def _compute_margin_commission(record):
    # XXX: Technically debit != invoiced, since purchase refunds increase
    # debit.  Nevertheless we can't ignore that.
    invoiced, balance = record.debit, record.balance
    margin = balance/invoiced if invoiced > 0 else 0
    # Since all the margins are expected to be given in percent units
    # we normalize them to the interval 0-1.
    required_margin = record.current_required_margin / 100
    max_margin = record.current_max_margin / 100
    min_comm = record.current_min_comm / 100
    max_comm = record.current_max_comm / 100
    if required_margin and max_margin and min_comm and max_comm:
        alpha = (max_margin - margin)/(max_margin - required_margin)
        if alpha < 0:
            # Ensure the formula below will never surpass max_comm
            alpha = 0
        commission_percent = min_comm*alpha + max_comm*(1 - alpha)
        if commission_percent < min_comm:
            # Bad sales are given nothing
            commission_percent = 0
    else:
        commission_percent = 0
    return margin, commission_percent, balance


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    # The formulae for the commission to salesmen is based on a simple
    # projection from the desired sales margin (required_margin, max_margin)
    # to the commission margins salesmen earn per sale.
    #
    # The projection is simply a geometrical projection: required_margin
    # yields the minimal commission margin, the max_margin yields the maximal
    # commission margin.  Accounts that fail to achieve the required_margin
    # yield 0% commission, accounts that surpass the max_margin yields just
    # the maximal commission margin.
    #
    # The projection follows the scheme below:
    #
    #     min margin ----------X------------------ max margin
    #                          |
    #     min com    ----------V------------------ max comm
    #
    # X represents the actual margin, V represents the resultant commission
    # margin.
    #
    # V = min_comm * alpha + max_comm * (1 - alpha), where alpha is given by
    # the formula:
    #
    # alpha = (max_margin - X)/(max_margin - min_margin)
    #
    # if alpha < 0: alpha = 0   # Too much margin
    #
    # if V < min_comm: V = 0
    #
    # Each account may have any desired required_margin and max_margin,
    # provided the required_margin is greater or equal of is parent account
    # and the max_margin is less or equal than the parent account.
    #
    # The account may have any desired min commission and max commission, no
    # restrictions are placed.
    #
    # By default, accounts take all these parameters from it's parent. So it's
    # wise to only establish them at accounts that consolidate operational
    # branches.
    #

    required_margin = fields.Float(
        string='Required margin',
        help=('This is the minimum margin required for an operation. If 0 '
              'no commission will be calculated.'),
        required=False,
        default=0,
        track_visibility='onchange',
    )
    max_margin = fields.Float(
        string='Maximum margin',
        help='This is maximum margin allowed for an operation.',
        required=False,
        default=0,
        track_visibility='onchange',
    )
    min_commission_margin = fields.Float(
        string='Minimum commission margin',
        help='This is minimum margin for commissions.',
        required=False,
        default=0,
        track_visibility='onchange',
    )
    max_commission_margin = fields.Float(
        string='Maximum commission margin',
        help='This is maximum margin for commissions.',
        required=False,
        default=0,
        track_visibility='onchange',
    )

    current_required_margin = fields.Float(
        compute=_compute_from_branch('required_margin',
                                     'current_required_margin', default=0)
    )
    current_max_margin = fields.Float(
        compute=_compute_from_branch('max_margin',
                                     'current_max_margin', default=0)
    )
    current_min_comm = fields.Float(
        compute=_compute_from_branch('min_commission_margin',
                                     'current_min_comm', default=0)
    )
    current_max_comm = fields.Float(
        compute=_compute_from_branch('max_commission_margin',
                                     'current_max_comm', default=0)
    )

    percentage_margin = fields.Float(
        string='Margin %', help='Percentage margin related to credit.',
        compute='_compute_commission')

    percentage_commission = fields.Float(
        string='Commission %', help='Percentage commission related to profit.',
        compute='_compute_commission')

    commission = fields.Float(
        string='Commission', help='Commission related to profit.',
        compute='_compute_commission')

    primary_salesperson_id = fields.Many2one(
        "res.users", string="Salesperson",
        help="Primary salesperson in operation",
        compute="_compute_primary_salesperson", store=True)

    supplier_invoice_id = fields.Many2one('account.invoice',
                                          ondelete='set null')

    # TODO: Ensure only groups='base.group_sale_manager' can update the
    # commission margins.  So far, only the goodwill of ignorance may save us.

    @api.depends('debit', 'balance')
    def _compute_commission(self):
        for record in self:
            margin, comm_percent, balance = _compute_margin_commission(record)
            record.percentage_margin = margin * 100
            record.percentage_commission = comm_percent * 100
            record.commission = comm_percent * balance

    @api.depends("type", "line_ids.invoice_id.user_id.name")
    def _compute_primary_salesperson(self):
        for record in self:
            if record.type != "contract":
                record.primary_salesperson_id = False
            else:
                main_line = record.line_ids.search(
                    [("account_id", "=", record.id),
                     ("invoice_id.user_id", "!=", False)], limit=1, order="id")
                if any(main_line):
                    record.primary_salesperson_id = main_line.invoice_id.user_id
                else:
                    record.primary_salesperson_id = False

    # TODO: This can be embedded in _compute_primary_salesperson.
    @api.one
    def has_many_salespeople(self):
        if self.type != "contract":
            return False
        else:
            lines = self.line_ids.search(
                [("account_id", "=", self.id),
                 ("invoice_id.user_id", "!=", False)])
            if any(lines):
                salesperson = lines[0].invoice_id.user_id
                for line in lines[1:]:
                    if line.invoice_id.user_id != salesperson:
                        return True
                return False
            return False

    @api.constrains('required_margin', 'max_margin')
    def _validate_margins(self):
        for record in self:
            required_margin = record.required_margin
            max_margin = record.max_margin
            if bool(required_margin) != bool(max_margin):
                # Either both are set or both are unset
                raise ValidationError('You must set both required_margin '
                                      'and max_margin or none.')
            if required_margin < 0 or required_margin > 100:
                raise_validation_error('required minimum margin')
            if max_margin < 0 or max_margin > 100:
                raise_validation_error('maximum allowed margin')
            if required_margin and max_margin and \
               required_margin >= max_margin:
                raise ValidationError('required margin must be less that '
                                      'max margin.')
            parent = record.parent_id
            if parent and parent.id:
                if parent.required_margin and required_margin and \
                   required_margin < parent.required_margin:
                    raise ValidationError(
                        'You cannot lower the required margin')
                if parent.max_margin and max_margin and \
                   max_margin > parent.max_margin:
                    raise ValidationError(
                        'You cannot raise the maximum margin')
            # TODO: If the children enter in violation what to do?
            # for child in record.complete_child_ids:
            #     child._validate_margins()

    @api.constrains('min_commission_margin', 'max_commission_margin')
    def _validate_commission_margins(self):
        for record in self:
            min_comm = record.min_commission_margin
            max_comm = record.max_commission_margin
            if bool(min_comm) != bool(max_comm):
                # Either both are set or both are unset
                    raise ValidationError('You must set both min commission '
                                          'and max commission or none.')
            if min_comm < 0 or min_comm > 100:
                raise_validation_error('minimum commission margin')
            if max_comm < 0 or max_comm > 100:
                raise_validation_error('maximum commission margin')
            if min_comm and max_comm and min_comm >= max_comm:
                raise ValidationError('min commission must be less that '
                                      'max commission.')


def raise_validation_error(*fields):
    raise ValidationError('Invalid value for field(s) %r', fields)
