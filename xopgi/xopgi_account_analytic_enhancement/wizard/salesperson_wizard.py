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

from datetime import date
from xoutil.future.codecs import safe_decode

from xoeuf import api, fields, models
from xoeuf.odoo import _
from xoeuf.osv.orm import CREATE_RELATED
from xoeuf.models.proxy import AccountInvoice as Invoice


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
        domain=[("state", "=", "close"), ("supplier_invoice_id", "=", False)]
    )

    @api.onchange("primary_salesperson_id")
    def _onchange_primary_salesperson_id(self):
        self.analytic_account_ids = self.env["account.analytic.account"].search(
            [("primary_salesperson_id.id", "=", self.primary_salesperson_id.id),
             ("state", "=", "close"),
             ("supplier_invoice_id", "=", False)]
        )

    @api.requires_singleton
    def generate_supplier_invoice(self):
        partner = self.primary_salesperson_id.partner_id
        account = partner.property_account_payable_id
        invoice = self._supplier_invoice_generator(
            partner,
            account,
            self.analytic_account_ids
        )
        return invoice.get_formview_action()

    @api.model
    def enqueue_generate_supplier_invoice_cron(self):
        from xoeuf.odoo.jobs import Deferred
        # Avoid performing a big computation within the WorkerCron process
        # which is under tight timeout restriction (because the same
        # restriction applies to Cron and HTTP workers).  Jobs are allowed to
        # take longer.
        Deferred(self.generate_supplier_invoice_cron)

    @api.model
    def generate_supplier_invoice_cron(self):
        commission_ready = self.env["account.analytic.account"].search(
            [('state', '=', 'close'),
             ('supplier_invoice_id', '=', False)]
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
            account = partner.property_account_payable_id
            self._supplier_invoice_generator(
                partner,
                account,
                salesperson_commissions[salesperson_key]
            )

    def _supplier_invoice_generator(self, partner, account, analytic_account_ids):
        d = date.today()
        company = self._context.get('company_id', self.env.user.company_id)
        journal = self.env['account.journal'].search(
            [('type', '=', 'purchase'), ('company_id', '=', company.id)],
            limit=1
        )
        # The context allows Odoo to compute the defaults we're missing here.
        result = Invoice.sudo().with_context(journal_id=journal.id).create(dict(
            partner_id=partner.id,
            account_id=account.id,
            type='in_invoice',  # supplier invoice
            name=_(u"Commission/") + safe_decode(d.strftime("%B")) + u"/" + safe_decode(partner.name),
            journal_id=journal.id,
            invoice_line_ids=[
                CREATE_RELATED(
                    quatity=1,
                    account_analytic_id=analytic_account.id,
                    name=_("Operation") + safe_decode(analytic_account.name),
                    price_unit=analytic_account.commission
                )
                for analytic_account in analytic_account_ids
            ]
        ))
        analytic_account_ids.write(dict(supplier_invoice_id=result.id))
        followers = [partner.id]
        employees = self.env["hr.employee"].search([("user_id.partner_id", "=", partner.id)])
        for employee in employees:
            if employee.parent_id:
                manager = employee.parent_id.user_id.partner_id
                if any(manager):
                    followers.append(manager.id)
        result.message_subscribe(partner_ids=followers)
        return result
