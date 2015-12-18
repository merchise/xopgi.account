# -*- coding: utf-8 -*-

import logging
from openerp import api, fields, models


class PrimaryInstructorWizard(models.TransientModel):
    _name = "xopgi.salesperson_wizard"
    _description = "Create supplier invoice in form of commission"

    def _get_salesperson(self):
        return self.env["account.analytic.account"].browse(
            self._context.get("active_id")).primary_salesperson_id

    primary_salesperson_id = fields.Many2one(
        "res.users", string="Salesperson", required=True,
        default=_get_salesperson)
    analytic_account_ids = fields.Many2many(
        "account.analytic.account", string="Operations", required=True,
        domain=[("type", "=", "contract"), ("state", "=", "close"),
                ("supplier_invoice_id", "=", False)])

    @api.onchange("primary_salesperson_id")
    def _onchange_primary_salesperson_id(self):
        self.analytic_account_ids = self.env[
            "account.analytic.account"].search(
            [("primary_salesperson_id.id", "=",
              self.primary_salesperson_id.id), ("type", "=", "contract"),
             ("state", "=", "close"), ("supplier_invoice_id", "=", False)])

    @api.multi
    def generate_supplier_invoice(self):
        partner = self.primary_salesperson_id.partner_id
        account_id = partner.property_account_payable.id
        self._supplier_invoice_generator(partner, account_id,
                                         self.analytic_account_ids)

    def enqueue_generate_supplier_invoice_cron(self, cr, uid, context=None):
        from openerp.jobs import Deferred
        # Avoid performing a big computation within the WorkerCron process
        # which is under tight timeout restriction (because the same
        # restriction applies to Cron and HTTP workers).  Jobs are allowed to
        # take longer.
        Deferred(self._name, cr, uid, 'generate_supplier_invoice_cron',
                 context=context)

    def generate_supplier_invoice_cron(self, cr, uid, context=None):
        with api.Environment.manage():
            self.env = api.Environment(cr, uid, {})
            commission_ready = self.env["account.analytic.account"].search(
                [('type', '=', 'contract'), ('state', '=', 'close'),
                 ('supplier_invoice_id', '=', False)])
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
                self._supplier_invoice_generator(partner, account_id,
                                                 salesperson_commissions[
                                                     salesperson_key])
            del self.env

    def _supplier_invoice_generator(self, partner, account_id,
                                    analytic_account_ids):
        supplier_invoice = self.env["account.invoice"].sudo().create(
            {"partner_id": partner.id,
             "account_id": account_id,
             "type": "in_invoice"})
        supplier_invoice.message_follower_ids |= self.env[
            "res.partner"].browse([partner.id])
        employees = self.env["hr.employee"].search(
            [("user_id.partner_id", "=", partner.id)])
        for employee in employees:
            if employee.parent_id:
                manager = employee.parent_id.user_id.partner_id
                if any(manager):
                    supplier_invoice.message_follower_ids |= manager
        for analytic_account_id in analytic_account_ids:
            self.env["account.invoice.line"].sudo().create(
                {"invoice_id": supplier_invoice.id,
                 "quantity": 1,
                 "account_analytic_id": analytic_account_id.id,
                 "name": "Operation " + analytic_account_id.complete_name,
                 "price_unit": analytic_account_id.commission})
            analytic_account_id.supplier_invoice_id = supplier_invoice.id
            if analytic_account_id.has_many_salespeople():
                logging.warning("More than one salesperson in operation: %s",
                                analytic_account_id.complete_name)
