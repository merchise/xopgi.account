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



Several words of warning
------------------------

OpenERP's addons are not distributed like that, so ``python setup.py install``
will not work as you may expect from other distributions, though we try hard
to simulate its external behavior.
