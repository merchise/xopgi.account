Allow to validate invoices using background celery jobs.

Some long invoices take too long to validate.  This makes it hard to validate
under normal HTTP processes.  This addon validates the invoices inside a
celery job.
