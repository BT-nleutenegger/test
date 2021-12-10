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
    print('14.0.2103.0 post-migration')
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['ir.attachment']._relocate_binary_data('bt_swissdec.tax_account_report', ['pdf_data'])
    env['ir.attachment']._relocate_binary_data('bt_swissdec.bt_swissdec_report_data', ['pdf_data'])
