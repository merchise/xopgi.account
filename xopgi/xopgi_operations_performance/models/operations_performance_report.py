# -*- coding: utf-8 -*-

from openerp import tools
from openerp import fields, models


class OperationPerformanceReport(models.Model):
    _name = "xopgi_operations_performance.opperf_report"
    _description = "Operation Performance Statistics"
    _auto = False

    lead_id = fields.Many2one("crm.lead", "Opportunity")
    # create_date = fields.date("Opportunity Date")
    response_time = fields.Integer(
        "Response Time",
        help="Time between opportunity creation and first Quotation")
    invoice_time = fields.Integer(
        "Invoice Time",
        help="Time between opportunity creation and first Invoice")

    def init(self, cr):
        tools.drop_view_if_exists(cr, "xopgi_operations_performance_opperf_report")
        cr.execute(
            """CREATE or REPLACE VIEW xopgi_operations_performance_opperf_report AS (
            SELECT
             crm_lead.id,
             crm_lead.id AS lead_id,
             CAST(DATE_PART('day', MIN(sale_order.date_order - crm_lead.create_date)) AS INTEGER) AS response_time,
             CAST(DATE_PART('day', MIN(account_invoice.date_invoice - crm_lead.create_date)) AS INTEGER) AS invoice_time
            FROM
             public.crm_lead
            INNER JOIN
             public.sale_order
            ON
             sale_order.origin = 'Opportunity: ' || crm_lead.id
            OR
             sale_order.origin = 'Oportunidad: ' || crm_lead.id
            OR
             sale_order.origin = 'Opportunité : ' || crm_lead.id
            LEFT OUTER JOIN
             public.account_invoice
            ON
             account_invoice.origin = sale_order.name
            GROUP BY
             crm_lead.id
            ORDER BY
             crm_lead.id DESC)""")
