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
 crm_lead.id DESC