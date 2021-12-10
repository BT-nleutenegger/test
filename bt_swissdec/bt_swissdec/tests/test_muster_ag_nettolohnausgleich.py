##############################################################################
# Copyright (c) 2021 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from logging import getLogger

from .common import TestBTSwissdec

_logger = getLogger(__name__)


class TestMusterAGNettolohnausgleich(TestBTSwissdec):

    def test_nettolohnausgleich(self):
        user_demo = self.ref('base.user_demo')
        # Remove all existing data from previous tests
        self.env.cr.execute('delete from hr_payslip;')
        self.env.cr.execute('delete from hr_payroll_register;')
        self.env.cr.execute('delete from account_move_line;')
        self.env.cr.execute('delete from account_move;')
        self.env.cr.execute('delete from account_move_line_salary;')
        self.env.cr.execute('delete from account_move_salary;')
        self.env.cr.commit()

        # set 'Personalaufwand Lohn QST'
        journal = self.browse_ref('bt_swissdec.account_journal_personalaufwandlohn0')
        # set 'Bank'
        bank = self.env['account.journal'].search([('name', '=', 'Bank'), ('company_id', '=', 1)], limit=1)

        # Employees : Herz Monica
        self.env.cr.execute("update hr_contract set date_end = '2013-12-31', state = 'close' "
                            "where id not in (select id from hr_contract where name like '%Herz%') "
                            "and company_id in (select id from res_company where name = 'MUSTER AG')")
        self.env.cr.execute("update hr_contract set date_end = '2014-12-31' "
                            "where id in (select id from hr_contract where name like '%Herz%')")
        self.env.cr.execute("delete from hr_payslip_grosswage_line "
                            "where contract_id in (select id from hr_contract where name like '%Herz%')")
        self.env.cr.execute("update hr_employee_calculationparameter_nettolohnausgleich set code = '1' "
                            "where year_id in (select id from hr_employee_year where employee_name = 'Herz')")

        # set year
        company_year = self.env['res.company'].browse(1)
        company_year.with_user(user_demo).create_year()  # 2014

        # Create contract entries
        # add Monatslohn
        self.add_category_adc_to_contract('2014-1-1', False, '1000', 'Monatslohn', 5000,
                                          self.env.ref('bt_swissdec.hr_contract_herzmonica0').id,
                                          1)

        # add Familienzulage
        self.add_category_adc_to_contract('2014-1-1', False, '3030', 'Familienzulage', 450,
                                          self.env.ref('bt_swissdec.hr_contract_herzmonica0').id,
                                          1)

        # add Kranken-Taggeld
        self.add_category_adc_to_contract('2014-2-1', False, '2035', 'Kranken-Taggeld', 2200,
                                          self.env.ref('bt_swissdec.hr_contract_herzmonica0').id,
                                          1)

        # add Korrektur Taggelder
        self.add_category_adc_to_contract('2014-2-1', False, '2050', 'Korrektur Taggelder', 2200,
                                          self.env.ref('bt_swissdec.hr_contract_herzmonica0').id,
                                          1)

        self.env.cr.execute("delete from account_move where id = 1")

        auszahlung_correct = 5015.95
        # create salary jan 2014
        payroll_register = self.create_payroll_register(
            user_demo,
            "{0} {1}".format('01', '2014'),
            "{0}-{1}-01".format('2014', '01'),
            journal,
            bank,
        )
        self.compute_payroll_register(payroll_register, auszahlung_correct)

        # create salary feb 2014
        payroll_register = self.create_payroll_register(
            user_demo,
            "{0} {1}".format('02', '2014'),
            "{0}-{1}-01".format('2014', '02'),
            journal,
            bank,
        )
        self.compute_payroll_register(payroll_register, auszahlung_correct)

        # check if all is correct
        nettolohnausgleich_correct = -209.15
        nettolohnausgleich_category = self.env['hr.allounce.deduction.categoty'].search(
            [('matrix_nr', '=', '2051'), ('company_id', '=', 1)])
        feb_nettolohnausgleich = 0
        for payslip_feb in self.env['hr.payslip'].search([('date', '=', '2014-2-1')]):
            for grosswage_line in payslip_feb.grosswage_ids:
                if grosswage_line.category_adc_id.id == nettolohnausgleich_category.id:
                    feb_nettolohnausgleich += grosswage_line.amount_total

        jan_auszahlung = sum(payslip.auszahlung for payslip in self.env['hr.payslip'].search([('date', '=', '2014-1-1')]))
        feb_auszahlung = sum(payslip.auszahlung for payslip in self.env['hr.payslip'].search([('date', '=', '2014-2-1')]))
        self.assertTrue(
            round(jan_auszahlung, 2) == round(feb_auszahlung, 2) == auszahlung_correct,
            "The value of 'Auszahlung' Jan and Feb should be identical (%s)." % (auszahlung_correct)
        )
        self.assertTrue(
            round(feb_nettolohnausgleich, 2) == nettolohnausgleich_correct,
            "The value of 'Nettolohnausgleich' for Feb is not correct (%s). It should be %s." % (round(feb_nettolohnausgleich, 2), nettolohnausgleich_correct)
        )
