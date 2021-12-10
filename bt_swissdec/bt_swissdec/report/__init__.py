##############################################################################
#
#    Copyright (c) 2016 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################
# HACK: 18.09.17 11:10: jool1: leave this for odoo10 as mako because we don't know in which direction swissdec goes with BVG

from . import report_bvg_declaration

from . import report_payslip
from . import report_payslip_register
from . import report_payslip_account_move_lines
from . import report_payslip_account_move_lines_register
from . import report_payslip_voucher
from . import report_payslip_voucher_register
from . import report_payslip_voucher_kst
from . import report_payslip_voucher_kst_register

#report xlsx
from . import ir_report
from . import report_xlsx

#HR Reports
from . import report_hr_wagetypesrecap
from . import report_hr_matrix
from . import report_hr_yearlyrecap
from . import report_hr_recap_employees_per_wagetypes
from . import report_hr_yearlyrecap_qst
from . import report_hr_company
from . import report_hr_employee
from . import report_hr_yearlyrecap_xlsx

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
