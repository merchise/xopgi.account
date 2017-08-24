# -*- coding: utf-8 -*-
from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from xoeuf import MAJOR_ODOO_VERSION

if 8 <= MAJOR_ODOO_VERSION < 9:
    from . import models  # noqa
    from . import wizard  # noqa
