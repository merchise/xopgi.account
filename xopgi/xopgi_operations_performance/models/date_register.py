# -*- coding: utf-8 -*-

from openerp import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    send_date = fields.Datetime(string="Send Date", help="Order send date",
                                copy=False)

    @api.one
    def action_sent_mail(self):
        self.write({"state": "sent", "send_date": fields.Datetime.now()})


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    call_date = fields.Datetime(string="Call Date",
                                help="Begin call for bids date", copy=False)

    @api.one
    def tender_in_progress(self):
        return self.write(
            {"state": "in_progress", "call_date": fields.Datetime.now()})


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    send_date = fields.Datetime(string="Send Date",
                                help="Purchase order send date", copy=False)

    @api.one
    def action_sent_mail(self):
        self.write({"state": "sent", "send_date": fields.Datetime.now()})
