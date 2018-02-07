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


import operator
from operator import attrgetter
from itertools import groupby
from functools import reduce

from datetime import date
from xoutil.future.codecs import safe_decode

from xoeuf import api, fields, models
from xoeuf.odoo import _
from xoeuf.osv.orm import (
    CREATE_RELATED,
    UNLINKALL_RELATED,
    LINK_RELATED,
    UPDATE_RELATED,
    COMMAND_INDEX,
    ID_INDEX
)
from xoeuf.models.proxy import AccountInvoice as Invoice


class CreateInvoiceWizard(models.TransientModel):
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

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        # Sanitize the result of the onchange.  Odoo and the Web Client seems
        # not to look eye to eye when dealing with x2many.  Odoo sends
        # UNLINKALL and the UPDATE commands.  I thought that if Odoo would
        # send the LINK_RELATED before, it would fix all the issues.  However,
        # it does not work.
        #
        # This hack solves this for this specific case: Replace all
        # UPDATE_RELATED by LINK_RELATED.  We can do this at this point,
        # because we're no editing any of the values of the accounts.
        def correct(cmd):
            if cmd[COMMAND_INDEX] == UPDATE_RELATED:
                return LINK_RELATED(cmd[ID_INDEX])
            else:
                return cmd
        result = super(CreateInvoiceWizard, self).onchange(values, field_name, field_onchange)
        value = result.setdefault('value', {})
        links = value.setdefault('analytic_account_ids', [])
        if links and links[0] == (UNLINKALL_RELATED, ):
            links[1:] = [correct(cmd) for cmd in links[1:]]
        return result

    @api.onchange('primary_salesperson_id')
    def _update_accounts(self):
        accounts = self.env["account.analytic.account"].search(
            [("primary_salesperson_id.id", "=", self.primary_salesperson_id.id),
             ("state", "=", "close"),
             ("supplier_invoice_id", "=", False)]
        )
        self.analytic_account_ids = accounts

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
        Account = self.env["account.analytic.account"]
        accounts = Account.search(
            [('state', '=', 'close'),
             ('supplier_invoice_id', '=', False),
             ('primary_salesperson_id', '!=', False)],
            order='primary_salesperson_id'
        )
        for user, partner_accounts in groupby(accounts, attrgetter('primary_salesperson_id')):
            self._supplier_invoice_generator(
                user.partner_id,
                user.property_account_payable_id,
                reduce(operator.or_, partner_accounts, Account)
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
            name=_(u"Commission. ") + safe_decode(d.strftime("%B")) + u" / " + safe_decode(partner.name),
            origin=_(u"Commission. ") + safe_decode(d.strftime("%B")) + u" / " + safe_decode(partner.name),
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
