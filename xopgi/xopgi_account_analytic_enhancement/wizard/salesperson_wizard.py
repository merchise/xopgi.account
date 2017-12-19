#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# salesperson_wizard
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

import logging
from datetime import date
from xoutil.future.codecs import safe_decode

from xoeuf import api, fields, models, MAJOR_ODOO_VERSION
from xoeuf.odoo import _

# The difference between Odoo 8 and Odoo 9, is how to get valid domain to
# search analytic accounts.
if MAJOR_ODOO_VERSION == 8:
    def account_domain():
        return [("type", "=", "contract")]
elif MAJOR_ODOO_VERSION == 9:
    def account_domain():
        return [("account_type", "=", "normal")]
elif MAJOR_ODOO_VERSION == 10:
    def account_domain():
        return [("active", "=", True)]
else:
    raise NotImplemented


class PrimaryInstructorWizard(models.TransientModel):
    _name = "xopgi.salesperson_wizard"
    _description = "Create supplier invoice in form of commission"

    def _get_salesperson(self):
        return self.env["account.analytic.account"].browse(
            self._context.get("active_id")).primary_salesperson_id

    primary_salesperson_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        required=True,
        default=_get_salesperson
    )
    analytic_account_ids = fields.Many2many(
        "account.analytic.account",
        string="Operations",
        required=True,
        domain=[("state", "=", "close"),
                ("supplier_invoice_id", "=", False)] + account_domain()
    )

    @api.onchange("primary_salesperson_id")
    def _onchange_primary_salesperson_id(self):
        self.analytic_account_ids = self.env["account.analytic.account"].search(
            [("primary_salesperson_id.id", "=", self.primary_salesperson_id.id),
             ("state", "=", "close"),
             ("supplier_invoice_id", "=", False)] + account_domain()
        )

    @api.multi
    def generate_supplier_invoice(self):
        partner = self.primary_salesperson_id.partner_id
        account_id = partner.property_account_payable.id
        self._supplier_invoice_generator(partner, account_id,
                                         self.analytic_account_ids)

    @api.model
    def enqueue_generate_supplier_invoice_cron(self):
        from openerp.jobs import Deferred
        # Avoid performing a big computation within the WorkerCron process
        # which is under tight timeout restriction (because the same
        # restriction applies to Cron and HTTP workers).  Jobs are allowed to
        # take longer.
        Deferred(self.generate_supplier_invoice_cron)

    @api.model
    def generate_supplier_invoice_cron(self):
        commission_ready = self.env["account.analytic.account"].search(
            [('state', '=', 'close'),
             ('supplier_invoice_id', '=', False)] + account_domain()
        )
        salesperson_commissions = {}
        for commission in commission_ready:
            salesperson = commission.primary_salesperson_id
            if salesperson:
                sale_partner = salesperson.partner_id
                comm = salesperson_commissions.setdefault(
                    sale_partner.id, []
                )
                comm.append(commission)
        for salesperson_key in salesperson_commissions:
            partner = self.env["res.partner"].browse([salesperson_key])
            account_id = partner.property_account_payable.id
            self._supplier_invoice_generator(
                partner,
                account_id,
                salesperson_commissions[salesperson_key]
            )

    def _supplier_invoice_generator(self, partner, account_id,
                                    analytic_account_ids):
        # TODO: Performance.  This code: issues lots of SQL, if needed use the
        # xoeuf.orm.get_creator API to make this easier.
        d = date.today()
        supplier_invoice = self.env["account.invoice"].sudo().create(
            {"partner_id": partner.id,
             "account_id": account_id,
             "type": "in_invoice",
             "name": _(u"Commission/") + safe_decode(d.strftime("%B")) + u"/" + safe_decode(partner.name),
             "journal_id": self.env['account.journal'].search(
                 [('type', 'in', ['purchase']),
                  ('company_id', '=', self._context.get(
                      'company_id', self.env.user.company_id.id))],
                 limit=1).id})
        supplier_invoice.message_follower_ids |= self.env["res.partner"].browse(partner.id)  # UPDATE ...
        employees = self.env["hr.employee"].search([("user_id.partner_id", "=", partner.id)])
        for employee in employees:
            if employee.parent_id:
                manager = employee.parent_id.user_id.partner_id
                if any(manager):
                    supplier_invoice.message_follower_ids |= manager  # UPDATE ...
        for analytic_account_id in analytic_account_ids:
            # Lots of INSERT INTO (and possible UPDATE...)
            self.env["account.invoice.line"].sudo().create(
                {"invoice_id": supplier_invoice.id,
                 "quantity": 1,
                 "account_analytic_id": analytic_account_id.id,
                 "name": _(u"Operation ") + safe_decode(analytic_account_id.complete_name),
                 "price_unit": analytic_account_id.commission})
            analytic_account_id.supplier_invoice_id = supplier_invoice.id
            if analytic_account_id.has_many_salespeople():
                logging.warning("More than one salesperson in operation: %s",
                                analytic_account_id.complete_name)
