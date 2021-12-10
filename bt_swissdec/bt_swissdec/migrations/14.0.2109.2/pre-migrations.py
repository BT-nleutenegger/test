##############################################################################
#
#    Copyright (c) 2021 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################


def migrate(cr, version):
    print('14.0.2109.2 pre-migration')
    if not version:
        return
    # This values ('mb92','mb128','mt92','mt128') do not exist anymore
    query = """update res_company set margin_bottom_address_payslip = 'mb64' 
    where margin_bottom_address_payslip in ('mb92','mb128')"""
    cr.execute(query)
    query = """update res_company set margin_top_address_payslip = 'mt64' 
    where margin_top_address_payslip in ('mt92','mt128')"""
    cr.execute(query)
