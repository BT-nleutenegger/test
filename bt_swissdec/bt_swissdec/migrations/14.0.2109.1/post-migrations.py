##############################################################################
#
#    Copyright (c) 2020 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from odoo import api
from odoo import SUPERUSER_ID


def migrate(cr, version):
    print('14.0.2109.1 post-migration')
    if not version:
        return
    query = """update hr_qst_line set code_medianwert = '' where code_medianwert is null"""
    cr.execute(query)
