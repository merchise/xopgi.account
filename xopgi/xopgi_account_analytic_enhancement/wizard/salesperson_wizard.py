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
        supplier_invoice = self.env["account.invoice"].sudo().create(
            {"partner_id": partner.id,
             "account_id": account_id,
             "type": "in_invoice"})
        for analytic_account_id in self.analytic_account_ids:
            self.env["account.invoice.line"].sudo().create(
                {"invoice_id": supplier_invoice.id,
                 "quantity": 1,
                 "account_analytic_id": analytic_account_id.id,
                 "name": "Operation " + analytic_account_id.complete_name,
                 "price_unit": analytic_account_id.commission})
            analytic_account_id.supplier_invoice_id = supplier_invoice.id
            if analytic_account_id.has_many_salespeople():
                logging.warning("More than one salesperson in operation: " +
                                analytic_account_id.complete_name)
