# -*- coding: utf-8 -*-
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from openerp import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    send_date = fields.Datetime(string="Send Date", help="Order send date",
                                copy=False)

    def action_sent_mail(self):
        self.write({"state": "sent", "send_date": fields.Datetime.now()})


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    call_date = fields.Datetime(string="Call Date",
                                help="Begin call for bids date", copy=False)

    def tender_in_progress(self):
        return self.write(
            {"state": "in_progress", "call_date": fields.Datetime.now()})


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    send_date = fields.Datetime(string="Send Date",
                                help="Purchase order send date", copy=False)

    def action_sent_mail(self):
        self.write({"state": "sent", "send_date": fields.Datetime.now()})
