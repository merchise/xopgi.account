=====================================================
 Merchise's General Extensions to OpenERP Accounting
=====================================================

Overview
========

This module patches up several stuff we consider should be done otherwise in
OpenERP.  These are not (or should not be) customizations specific to any
business, but things that are general in any accounting setting.


Summary of changes
------------------

- When working in a multi-company database, some forms are setup such that
  once the company is known (for instance by choosing a Journal), other fields
  (like `periods`) are allowed to select only values that belong to the
  company.

- Allow to group items in several list by currency.  This is useful in
  multi-currency settings.


Installation
============

This package is prepared to be installed as a Python distribution, and run
with `xoeuf <installation with xoeuf_>`__.

In fact, several addons may use xoeuf's tools like `xoeuf.models`:mod:
and `xoeuf.osv`:mod:.

You may install these addons by copying them, but make sure that you have all
the required packages installed as well (see the `setup.py` file).

.. note:: We use buildout to install our Odoo deployments, this and other
          packages get installed like normal
