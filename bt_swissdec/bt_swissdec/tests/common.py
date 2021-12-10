##############################################################################
# Copyright (c) 2020 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

import base64
from logging import getLogger
import os
import subprocess
import tempfile
from odoo.tests.common import Form, SavepointCase

_logger = getLogger(__name__)


class TestBTSwissdec(SavepointCase):

    def setUp(self):
        ret = super(TestBTSwissdec, self).setUp()
        self.env = self.env(context=dict(self.env.context, tracking_disable=True))
        # Configuring the demo user
        demo_group_ids = [
            self.ref('base.group_private_addresses'),
            self.ref('hr.group_hr_manager'),
            self.ref('hr_payroll.group_hr_payroll_manager'),
            self.ref('hr_holidays.group_hr_holidays_manager'),
            self.ref('hr_contract.group_hr_contract_manager'),
            self.ref('hr_holidays.group_hr_holidays_user'),
            self.ref('account.group_account_invoice'),
            self.ref('base.group_partner_manager'),
            self.ref('base.group_user'),
            self.ref('hr.group_hr_user'),
            self.ref('hr_payroll.group_hr_payroll_user'),
            self.ref('hr_holidays.group_hr_holidays_responsible'),
            self.ref('account.group_show_line_subtotals_tax_excluded'),
        ]
        self.browse_ref('base.user_demo').write({
            'company_id': self.ref('base.main_company'),
            'company_ids': [(6, 0, [self.ref('base.main_company')])],
            'groups_id': [(6, 0, demo_group_ids)],
            'lang': 'de_CH',
            'tz': 'Europe/Zurich',
        })
        user = self.env['res.users'].sudo().search([('login', '=', 'demo2')])
        if user:
            p = user.partner_id
            user.unlink()
            p = self.env['res.partner'].sudo().search([('id', '=', p.id)])
            if p:
                p.unlink()
        partner_demo2 = self.env['res.partner'].create({
            'name': 'demo2',
            'company_id': self.ref('bt_swissdec.second_company'),
            'company_name': 'PROCESS AG',
            'street': '3575  Buena Vista Avenue',
            'city': 'Eugene',
            'email': 'demo2@example.com',
        })
        self.demo2 = self.env['res.users'].create({
            'partner_id': partner_demo2.id,
            'login': 'demo2',
            'password': 'demo2',
            'company_id': self.ref('bt_swissdec.second_company'),
            'company_ids': [(6, 0, [self.ref('bt_swissdec.second_company')])],
            'groups_id': [(6, 0, self.browse_ref('base.user_demo').groups_id.ids)],
            'lang': 'de_CH',
            'tz': 'Europe/Zurich',
        })
        user5 = self.env['res.users'].sudo().search([('login', '=', 'demo2_5')])
        if user5:
            p = user5.partner_id
            user5.unlink()
            p = self.env['res.partner'].sudo().search([('id', '=', p.id)])
            if p:
                p.unlink()
        partner_demo2_5 = self.env['res.partner'].create({
            'name': 'demo2_5',
            'company_id': self.ref('bt_swissdec.second_company5'),
            'company_name': 'PROCESS_5 AG',
            'street': '3575  Buena Vista Avenue',
            'city': 'Eugene',
            'email': 'demo2_5@example.com',
        })
        self.demo2_5 = self.env['res.users'].create({
            'partner_id': partner_demo2_5.id,
            'login': 'demo2_5',
            'password': 'demo2_5',
            'company_id': self.ref('bt_swissdec.second_company5'),
            'company_ids': [(6, 0, [self.ref('bt_swissdec.second_company5')])],
            'groups_id': [(6, 0, self.browse_ref('base.user_demo').groups_id.ids)],
            'lang': 'de_CH',
            'tz': 'Europe/Zurich',
        })
        return ret

    def restore_backup_db(self):
        import subprocess
        db_actual = self.env.cr.dbname
        # the backup db must end with '_b'
        db_backup = "{0}_{1}".format(db_actual, 'b')
        subprocess.check_call(
            """psql -d {} -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{}' AND pid <> pg_backend_pid();" """.format(
                db_backup, db_actual), shell=True,
            stdout=subprocess.DEVNULL)
        subprocess.check_call("psql -d {} -c 'DROP DATABASE IF EXISTS {}'".format(db_backup, db_actual),
                              shell=True,
                              stdout=subprocess.DEVNULL)

        subprocess.check_call('createdb {}'.format(db_actual), shell=True, stdout=subprocess.DEVNULL)
        subprocess.check_call('pg_dump {} | psql {}'.format(db_backup, db_actual), shell=True,
                              stdout=subprocess.DEVNULL)
        subprocess.check_call(
            """psql -d {} -c "update ir_module_module set state = 'installed' where name = 'bt_swissdec';" """.format(
                db_actual), shell=True, stdout=subprocess.DEVNULL)

    def add_category_adc_to_contract(self, date_from, date_to, matrix_nr, name, amount, contract_id, company_id):
        slip_grosswage_line_pool = self.env['hr.payslip.grosswage.line']
        hr_adc_pool = self.env['hr.allounce.deduction.categoty']
        hr_adc_history_pool = self.env['hr.adc.history']
        add_category = hr_adc_pool.search([('matrix_nr', '=', matrix_nr), ('company_id', '=', company_id)])
        matrix_buchhaltung = \
            hr_adc_history_pool.get_actual_value_at_date(
                add_category.id,
                'matrix_buchhaltung_account',
                date_from)
        vals = {
            'category_adc_id': add_category.id,
            'value': amount,
            'code': hr_adc_history_pool.get_actual_value_at_date(add_category.id, 'code', date_from),
            'contract_id': contract_id,
            'name': name,
            'account_id': matrix_buchhaltung,
            'sequence': add_category.sequence,
            'date_from': date_from,
            'date_to': date_to,
        }
        slip_grosswage_line_pool.create(vals)

    def create_payroll_register(self, user, name, date, journal, payment_journal):
        payroll_register_form = Form(self.env['hr.payroll.register'].with_user(user))
        payroll_register_form.name = name
        payroll_register_form.date = date
        payroll_register_form.journal_id = journal
        payroll_register_form.payment_journal_id = payment_journal
        payroll_register = payroll_register_form.save()
        payroll_register.compute_sheet_check_wizard()
        return payroll_register

    def compute_payroll_register(self, payroll_register, expected_qty):
        _logger.warning('Book Register Lohn %s - Total Auszahlung: %s' % (payroll_register.name, payroll_register.auszahlung))
        _logger.warning('KORREKT - Total Auszahlung: %s' % (expected_qty))
        # self.assertAlmostEquals(payroll_register.auszahlung, expected_qty)
        _logger.warning('Lohn %s ist korrekt' % payroll_register.name)
        payroll_register.approval2()
        payroll_register.verify_sheet()
        payroll_register.final_verify_sheet()

    def create_lohn(self, user, date_display_name, employees, journal, payment_journal, date_str,
                    zahlung_nach_austritt, zahlung_nach_austritt_qst_separate_sb=False):
        _logger.info('%s - Create Lohn %s' % (date_display_name.upper(), date_display_name))
        for emp in employees:
            _logger.info('emp: %s' % (emp))
            self.create_payslip(
                user,
                emp,
                journal,
                payment_journal,
                date_str,
                zahlung_nach_austritt,
                zahlung_nach_austritt_qst_separate_sb
            )

    def create_payslip(self, user, employee, journal, payment_journal, date_str, zahlung_nach_austritt,
                       zahlung_nach_austritt_qst_separate_sb=False):
        payslip_form = Form(self.env['hr.payslip'].with_user(user))
        payslip_form.employee_id = employee
        payslip_form.journal_id = journal
        payslip_form.payment_journal_id = payment_journal
        payslip_form.date = date_str
        payslip_form.zahlung_nach_austritt = zahlung_nach_austritt
        payslip_form.zahlung_nach_austritt_qst_separate_sb = zahlung_nach_austritt_qst_separate_sb
        payslip = payslip_form.save()
        payslip.compute_sheet_check_wizard()
        return payslip

    def create_gui_stat_form(self, user, transmitter, name, month, qst_month, qst_year, raise_error_for_check_xml,
                             xml_name_to_save, delete=False):
        gui_tax_at_source_transmission_form = Form(self.env['gui_tax_at_source_transmission'].with_user(user))
        gui_tax_at_source_transmission_form.name = name
        gui_tax_at_source_transmission_form.transmitter_configuration_id = transmitter
        gui_tax_at_source_transmission_form.qst_month_id = qst_month
        gui_tax_at_source_transmission_form.year_id = qst_year
        gui_tax_at_source_transmission = gui_tax_at_source_transmission_form.save()
        gui_tax_at_source_transmission.action_print_data_review()
        if delete:
            gui_tax_at_source_transmission.unlink()
        else:
            gui_tax_at_source_transmission.action_send_declaration()
            _logger.info('Test Compare XML')
            compare_xml = self.compare_xml(name, 'gui_tax_at_source_transmission', month,
                                           gui_tax_at_source_transmission.company_id, xml_name_to_save)
            _logger.info('Result compare_xml: %s' % (compare_xml))
            if raise_error_for_check_xml:
                self.assertTrue(compare_xml == 0, 'The comparison with the XML went wrong: Files are different')

            gui_tax_at_source_transmission.sudo().write({
                'advance_mode': True,
            })
            gui_tax_at_source_transmission.action_get_status()
            gui_tax_at_source_transmission.all_get_all_information()
            gui_tax_at_source_transmission.do_next()
        return

    def create_salary_zahlung_nach_austritt(self, user, journal, bank, year, month, emp_ids, separate_sb=False):
        _logger.info("#############################")
        # used for salary_totals
        month_orig = month
        if int(month) > 12:
            month = int(month) - 12
            month = str(month)
            year = int(year) + 1
            year = str(year)
        self.create_lohn(
            user,
            "{0} {1}".format(month, year),
            emp_ids,
            journal,
            bank,
            "{0}-{1}-01".format(year, month),
            True,
            separate_sb,
        )

    def run_before_sal_01_2021(self, user_demo2, journal_qst, bank, year):
        pass

    def run_before_sal_02_2021(self, user_demo2, journal_qst, bank, year):
        # set entry for employee 31M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'entry', 'entryCompany', '2021-02-10',
                self.env.ref('bt_swissdec.hr_employee_31M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Degelo0_31M_qst5').with_user(user_demo2).id)
        except:
            print('bt_swissdec.hr_employee_31M_qst5 does not exist')
        # set entry for employee 31Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'entry', 'entryCompany', '2021-02-10',
                self.env.ref('bt_swissdec.hr_employee_31Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Degelo0_31Y_qst5').with_user(user_demo2).id)
        except:
            print('bt_swissdec.hr_employee_31Y_qst5 does not exist')

    def run_before_sal_03_2021(self, user_demo2, journal_qst, bank, year):
        pass

    def run_before_sal_04_2021(self, user_demo2, journal_qst, bank, year):
        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> TRUE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_1_4Y_qst5').with_user(user_demo2)]
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '04', emp_ids, True)
        except:
            print('bt_swissdec.hr_employee_1_4Y_qst5employee does not exist')

    def run_before_sal_05_2021(self, user_demo2, journal_qst, bank, year):
        # set entry for employee 32M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'entry', 'entryCompany', '2021-05-01',
                self.env.ref('bt_swissdec.hr_employee_32M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Duss0_32M_qst5').with_user(user_demo2).id)
        except:
            print('bt_swissdec.hr_employee_32M_qst5 does not exist')
        # set entry for employee 32Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'entry', 'entryCompany', '2021-05-01',
                self.env.ref('bt_swissdec.hr_employee_32Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Duss0_32Y_qst5').with_user(user_demo2).id)
        except:
            print('bt_swissdec.hr_employee_32Y_qst5 does not exist')

        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> TRUE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_1_2Y_qst5').with_user(user_demo2)]
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '05', emp_ids, True)
        except:
            print('bt_swissdec.hr_employee_1_2Y_qst5 employee does not exist')
        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> TRUE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_1_4Y_qst5').with_user(user_demo2)]
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '05', emp_ids, True)
        except:
            print('bt_swissdec.hr_employee_1_4Y_qst5 employee does not exist')

    def run_before_sal_06_2021(self, user_demo2, journal_qst, bank, year):
        # set withdrawal for employee 31M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-06-15',
                self.env.ref('bt_swissdec.hr_employee_31M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Degelo0_31M_qst5').with_user(user_demo2).id)
        except:
            print('bt_swissdec.hr_employee_31M_qst5 does not exist')
        # set withdrawal for employee 31Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-06-15',
                self.env.ref('bt_swissdec.hr_employee_31Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Degelo0_31Y_qst5').with_user(user_demo2).id)
        except:
            print('bt_swissdec.hr_employee_31Y_qst5 does not exist')

        # set withdrawal for employee 7.1Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-06-30',
                self.env.ref('bt_swissdec.hr_employee_7_1Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_7_1Y_qst5').with_user(user_demo2).id)
        except:
            print('bt_swissdec.hr_employee_7_1Y_qst5 does not exist')

        try:
            # we need to set for 40M and 40Y from april on qst to B0N
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET qst_code=(select id from hr_qst where name = 'B0N' and kanton = (select id from res_country_state where code = 'BE' and country_id in (select id from res_country where code = 'CH'))) WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_40M_qst5') and name = '2021') "
                "and valid_from >= '2021-04-01';")
            self.env['hr.employee.calculationparameter.qst'].flush()
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET needs_to_be_send_in_xml = True, test_scenario_id = Null WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_40M_qst5') and name = '2021') "
                "and valid_from in ('2021-04-01','2021-05-01');")
            self.env['hr.employee.calculationparameter.qst'].flush()
        except:
            print('bt_swissdec.hr_employee_40M_qst5 employee does not exist')
        try:
            # we need to set for 40M and 40Y from april on qst to B0N
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET qst_code=(select id from hr_qst where name = 'B0N' and kanton = (select id from res_country_state where code = 'TI' and country_id in (select id from res_country where code = 'CH'))) WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_40Y_qst5') and name = '2021') "
                "and valid_from >= '2021-04-01';")
            self.env['hr.employee.calculationparameter.qst'].flush()
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET needs_to_be_send_in_xml = True, test_scenario_id = Null WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_40Y_qst5') and name = '2021') "
                "and valid_from in ('2021-04-01','2021-05-01');")
            self.env['hr.employee.calculationparameter.qst'].flush()
        except:
            print('bt_swissdec.hr_employee_40Y_qst5 employee does not exist')

        try:
            # we need to set for 40_1Y from march on qst to B0N
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET qst_code=(select id from hr_qst where name = 'B0N' and kanton = (select id from res_country_state where code = 'TI' and country_id in (select id from res_country where code = 'CH'))) WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_40_1Y_qst5') and name = '2021') "
                "and valid_from >= '2021-03-01';")
            self.env['hr.employee.calculationparameter.qst'].flush()
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET needs_to_be_send_in_xml = True, test_scenario_id = Null WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_40_1Y_qst5') and name = '2021') "
                "and valid_from in ('2021-03-01','2021-04-01','2021-05-01');")
            self.env['hr.employee.calculationparameter.qst'].flush()
        except:
            print('bt_swissdec.hr_employee_40_1Y_qst5 employee does not exist')

        try:
            # we need to set for 42M and 42Y from april on qst to B0N
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET "
                "marital_validasof= '2021-03-26', "
                "marital_code = (select id from hr_employee_marital_status where code = 'married'), "
                "qst_code = (select id from hr_qst "
                "where name = 'B0N' and kanton = (select id from res_country_state where code = 'BE' and "
                "country_id in (select id from res_country where code = 'CH'))) WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_42M_qst5') and name = '2021') "
                "and valid_from >= '2021-04-01';")
            self.env['hr.employee.calculationparameter.qst'].flush()
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET needs_to_be_send_in_xml = True, test_scenario_id = Null WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_42M_qst5') and name = '2021') "
                "and valid_from in ('2021-04-01','2021-05-01');")
            self.env['hr.employee.calculationparameter.qst'].flush()
        except:
            print('bt_swissdec.hr_employee_42M_qst5 employee does not exist')
        try:
            # we need to set for 42M and 42Y from april on qst to B0N
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET "
                "marital_validasof= '2021-03-26', "
                "marital_code = (select id from hr_employee_marital_status where code = 'married'), "
                "qst_code = (select id from hr_qst "
                "where name = 'B0N' and kanton = (select id from res_country_state where code = 'TI' and "
                "country_id in (select id from res_country where code = 'CH'))) WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_42Y_qst5') and name = '2021') "
                "and valid_from >= '2021-04-01';")
            self.env['hr.employee.calculationparameter.qst'].flush()
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET needs_to_be_send_in_xml = True, test_scenario_id = Null WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_42Y_qst5') and name = '2021') "
                "and valid_from in ('2021-04-01','2021-05-01');")
            self.env['hr.employee.calculationparameter.qst'].flush()
        except:
            print('bt_swissdec.hr_employee_42Y_qst5 employee does not exist')

    def run_before_sal_07_2021(self, user_demo2, journal_qst, bank, year):
        try:
            # we need to set for 42M from may on qst to B1N
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET qst_code=(select id from hr_qst where name = 'B1N' and kanton = (select id from res_country_state where code = 'BE' and country_id in (select id from res_country where code = 'CH'))) WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_42M_qst5') and name = '2021') "
                "and valid_from >= '2021-05-01';")
            self.env['hr.employee.calculationparameter.qst'].flush()
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET needs_to_be_send_in_xml = True, test_scenario_id = Null WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_42M_qst5') and name = '2021') "
                "and valid_from in ('2021-05-01', '2021-06-01');")
            self.env['hr.employee.calculationparameter.qst'].flush()
        except:
            print('bt_swissdec.hr_employee_42M_qst5 employee does not exist')

        try:
            # we need to set for 42Y from may on qst to B1N
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET qst_code=(select id from hr_qst where name = 'B1N' and kanton = (select id from res_country_state where code = 'TI' and country_id in (select id from res_country where code = 'CH'))) WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_42Y_qst5') and name = '2021') "
                "and valid_from >= '2021-05-01';")
            self.env['hr.employee.calculationparameter.qst'].flush()
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET needs_to_be_send_in_xml = True, test_scenario_id = Null WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_42Y_qst5') and name = '2021') "
                "and valid_from in ('2021-05-01', '2021-06-01');")
            self.env['hr.employee.calculationparameter.qst'].flush()
        except:
            print('bt_swissdec.hr_employee_42Y_qst5 employee does not exist')

    def run_before_sal_08_2021(self, user_demo2, journal_qst, bank, year):
        pass

    def run_before_sal_09_2021(self, user_demo2, journal_qst, bank, year):
        # set withdrawal for employee 35M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-09-30',
                self.env.ref('bt_swissdec.hr_employee_35M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Estermann0_35M_qst5').with_user(user_demo2).id)
        except:
            print('bt_swissdec.hr_employee_35M_qst5 does not exist')
        # set withdrawal for employee 35Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-09-30',
                self.env.ref('bt_swissdec.hr_employee_35Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Estermann0_35Y_qst5').with_user(user_demo2).id)
        except:
            print('bt_swissdec.hr_employee_35Y_qst5 does not exist')

        # set withdrawal for employee 37M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-09-30',
                self.env.ref('bt_swissdec.hr_employee_37M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Farine0_37M_qst5').with_user(user_demo2).id)
        except:
            print('bt_swissdec.hr_employee_37M_qst5 does not exist')
        # set withdrawal for employee 37Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-09-30',
                self.env.ref('bt_swissdec.hr_employee_37Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Farine0_37Y_qst5').with_user(user_demo2).id)
        except:
            print('bt_swissdec.hr_employee_37Y_qst5 does not exist')

    def run_before_sal_10_2021(self, user_demo2, journal_qst, bank, year):
        # set entry for employee 7_1Y
        try:
            new_entry = self.create_entry_withdrawal(
                user_demo2,
                '2021-10-01',
                self.env.ref('bt_swissdec.hr_employee_7_1Y_qst5').with_user(user_demo2).id)
            self.create_qst_mutation_table_entry(
                user_demo2, 'entry', 'entryCompany', '2021-10-01',
                self.env.ref('bt_swissdec.hr_employee_7_1Y_qst5').with_user(user_demo2).id,
                new_entry.id)
        except:
            print('bt_swissdec.hr_employee_7_1Y_qst5 does not exist')

    def run_before_sal_11_2021(self, user_demo2, journal_qst, bank, year):
        try:
            employee_m = self.env.ref('bt_swissdec.hr_employee_35M_qst5').with_user(user_demo2)
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> FALSE
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '11', [employee_m])
        except:
            print('employee does not exist')
        try:
            employee_y = self.env.ref('bt_swissdec.hr_employee_35Y_qst5').with_user(user_demo2)
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> FALSE
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '11', [employee_y])
        except:
            print('employee does not exist')

        try:
            # we need to set for 37M from november on qst to B0N
            employee_m = self.env.ref('bt_swissdec.hr_employee_37M_qst5').with_user(user_demo2)
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET qst_code=(select id from hr_qst where name = 'B0N' and kanton = (select id from res_country_state where code = 'BE' and country_id in (select id from res_country where code = 'CH'))) WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_37M_qst5') and name = '2021') "
                "and valid_from in ('2021-11-01','2021-12-01');")
            self.env['hr.employee.calculationparameter.qst'].flush()
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> TRUE
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '11', [employee_m], True)
        except:
            print('bt_swissdec.hr_employee_37M_qst5 employee does not exist')
        try:
            # we need to set for 37Y from november on qst to B0N
            employee_y = self.env.ref('bt_swissdec.hr_employee_37Y_qst5').with_user(user_demo2)
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET qst_code=(select id from hr_qst where name = 'B0N' and kanton = (select id from res_country_state where code = 'TI' and country_id in (select id from res_country where code = 'CH'))) WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title = '_37Y_qst5') and name = '2021') "
                "and valid_from in ('2021-11-01','2021-12-01');")
            self.env['hr.employee.calculationparameter.qst'].flush()
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> TRUE
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '11', [employee_y], True)
        except:
            print('bt_swissdec.hr_employee_37Y_qst5 employee does not exist')
        self.env['hr.employee.calculationparameter.qst'].flush()

    def run_before_sal_12_2021(self, user_demo2, journal_qst, bank, year):
        # set hr_contract date_end to '2021-12-31' for all contracts
        self.env.cr.execute(
            "UPDATE hr_contract SET date_end='2021-12-31' WHERE employee_id in (select id from hr_employee "
            "where date_end is null and job_title in ('_1M_qst5', '_1Y_qst5', '_7M_qst5', '_7Y_qst5', '_7_1Y_qst5', "
            "'_9M_qst5', '_9Y_qst5', '_11_1M_qst5', '_11_1Y_qst5', '_15M_qst5', '_15Y_qst5', '_24M_qst5', '_24Y_qst5', "
            "'_25M_qst5', '_25Y_qst5', '_26M_qst5', '_26Y_qst5', '_27M_qst5', '_27Y_qst5', '_28M_qst5', '_28Y_qst5', "
            "'_29M_qst5', '_29Y_qst5', '_33M_qst5', '_33Y_qst5', '_36M_qst5', '_36Y_qst5', '_38M_qst5', '_38Y_qst5', "
            "'_39M_qst5', '_39Y_qst5', '_42M_qst5', '_42Y_qst5'));")
        self.env['hr.contract'].flush()
        # set hr_employee_entry_withdrawal date_end to '2021-12-31' for all contracts
        self.env.cr.execute(
            "UPDATE hr_employee_entry_withdrawal SET date_end='2021-12-31' WHERE employee_id in (select id from hr_employee "
            "where date_end is null and job_title in ('_1M_qst5', '_1Y_qst5', '_7M_qst5', '_7Y_qst5', '_7_1Y_qst5', "
            "'_9M_qst5', '_9Y_qst5', '_11_1M_qst5', '_11_1Y_qst5', '_15M_qst5', '_15Y_qst5', '_24M_qst5', '_24Y_qst5', "
            "'_25M_qst5', '_25Y_qst5', '_26M_qst5', '_26Y_qst5', '_27M_qst5', '_27Y_qst5', '_28M_qst5', '_28Y_qst5', "
            "'_29M_qst5', '_29Y_qst5', '_33M_qst5', '_33Y_qst5', '_36M_qst5', '_36Y_qst5', '_38M_qst5', '_38Y_qst5', "
            "'_39M_qst5', '_39Y_qst5', '_42M_qst5', '_42Y_qst5'));")
        self.env['hr.employee.entry.withdrawal'].flush()

        # set withdrawal for employee 1M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_1M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_1M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_1M_qst5 does not exist')

        # set withdrawal for employee 1Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_1Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_1Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_1Y_qst5 does not exist')

        # set withdrawal for employee 7M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_7M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_7M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_7M_qst5 does not exist')
        # set withdrawal for employee 7Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_7Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_7Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_7Y_qst5 does not exist')

        # set withdrawal for employee 7_1Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_7_1Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi1_7_1Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_7_1Y_qst5 does not exist')

        # set withdrawal for employee 9M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_9M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_9M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_9M_qst5 does not exist')
        # set withdrawal for employee 9Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_9Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_9Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_9Y_qst5 does not exist')

        # set withdrawal for employee 11_1M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_11_1M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_11_1M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_11_1M_qst5 does not exist')
        # set withdrawal for employee 11_1Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_11_1Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_11_1Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_11_1Y_qst5 does not exist')

        # set withdrawal for employee 15M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_15M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_15M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_15M_qst5 does not exist')
        # set withdrawal for employee 15Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_15Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_15Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_15Y_qst5 does not exist')

        # set withdrawal for employee 24M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_24M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_24M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_24M_qst5 does not exist')
        # set withdrawal for employee 24Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_24Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_24Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_24Y_qst5 does not exist')

        # set withdrawal for employee 25M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_25M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_25M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_25M_qst5 does not exist')
        # set withdrawal for employee 25Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_25Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_25Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_25Y_qst5 does not exist')

        # set withdrawal for employee 26M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_26M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_26M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_26M_qst5 does not exist')
        # set withdrawal for employee 26Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_26Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_26Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_26Y_qst5 does not exist')

        # set withdrawal for employee 27M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_27M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_27M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_27M_qst5 does not exist')
        # set withdrawal for employee 27Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_27Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_27Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_27Y_qst5 does not exist')

        # set withdrawal for employee 28M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_28M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_28M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_28M_qst5 does not exist')
        # set withdrawal for employee 28Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_28Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_28Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_28Y_qst5 does not exist')

        # set withdrawal for employee 29M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_29M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_29M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_29M_qst5 does not exist')
        # set withdrawal for employee 29Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_29Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_rinaldi0_29Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_29Y_qst5 does not exist')

        # set withdrawal for employee 33M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_33M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Egli0_33M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_33M_qst5 does not exist')
        # set withdrawal for employee 33Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_33Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Egli0_33Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_33Y_qst5 does not exist')

        # set withdrawal for employee 36M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_36M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Fankhauser0_36M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_36M_qst5 does not exist')
        # set withdrawal for employee 36Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_36Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Fankhauser0_36Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_36Y_qst5 does not exist')

        # set withdrawal for employee 38M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_38M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Brun0_38M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_38M_qst5 does not exist')
        # set withdrawal for employee 38Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_38Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Brun0_38Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_38Y_qst5 does not exist')

        # set withdrawal for employee 39M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_39M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Müller0_39M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_39M_qst5 does not exist')
        # set withdrawal for employee 39Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_39Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Müller0_39Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_39Y_qst5 does not exist')

        # set withdrawal for employee 42M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_42M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Armanini0_42M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_42M_qst5 does not exist')
        # set withdrawal for employee 42Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2021-12-31',
                self.env.ref('bt_swissdec.hr_employee_42Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Armanini0_42Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_42Y_qst5 does not exist')

    def run_before_sal_01_2022(self, user_demo2, journal_qst, bank, year):
        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> FALSE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_33M_qst5').with_user(user_demo2)]
            _logger.info("emp_ids: {0}".format(emp_ids))
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '13', emp_ids)
        except:
            print('employee does not exist')
        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> FALSE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_33Y_qst5').with_user(user_demo2)]
            _logger.info("emp_ids: {0}".format(emp_ids))
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '13', emp_ids)
        except:
            print('employee does not exist')
        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> FALSE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_33_1M_qst5').with_user(user_demo2)]
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '13', emp_ids)
        except:
            print('employee does not exist')
        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> FALSE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_33_1Y_qst5').with_user(user_demo2)]
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '13', emp_ids)
        except:
            print('employee does not exist')

    def run_before_sal_02_2022(self, user_demo2, journal_qst, bank, year):
        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> TRUE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_33M_qst5').with_user(user_demo2)]
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '14', emp_ids, True)
        except:
            print('employee does not exist')
        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> TRUE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_33Y_qst5').with_user(user_demo2)]
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '14', emp_ids, True)
        except:
            print('employee does not exist')
        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> TRUE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_38M_qst5').with_user(user_demo2)]
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '14', emp_ids, True)
        except:
            print('employee does not exist')
        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> TRUE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_38Y_qst5').with_user(user_demo2)]
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '14', emp_ids, True)
        except:
            print('employee does not exist')
        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> FALSE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_36M_qst5').with_user(user_demo2)]
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '14', emp_ids)
        except:
            print('employee does not exist')
        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> FALSE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_36Y_qst5').with_user(user_demo2)]
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '14', emp_ids)
        except:
            print('employee does not exist')
        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> FALSE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_38_1M_qst5').with_user(user_demo2)]
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '14', emp_ids, True)
        except:
            print('employee does not exist')
        try:
            # zahlung_nach_austritt -> TRUE / zahlung_nach_austritt_qst_separate_sb -> FALSE
            emp_ids = [self.env.ref('bt_swissdec.hr_employee_38_1Y_qst5').with_user(user_demo2)]
            self.create_salary_zahlung_nach_austritt(user_demo2, journal_qst, bank, year, '14', emp_ids, True)
        except:
            print('employee does not exist')

    def run_before_sal_03_2022(self, user_demo2, journal_qst, bank, year):
        # set hr_contract date_end to '2022-03-31' for 32M, 32Y, 41M and 41Y
        self.env.cr.execute(
            "UPDATE hr_contract SET date_end='2022-03-31' WHERE employee_id in (select id from hr_employee "
            "where job_title in ('_32M_qst5', '_32Y_qst5', '_41M_qst5', '_41Y_qst5'));")
        self.env['hr.contract'].flush()
        # set hr_employee_entry_withdrawal date_end to '2022-03-31' for 32M and 32Y
        self.env.cr.execute(
            "UPDATE hr_employee_entry_withdrawal SET date_end='2022-03-31' WHERE employee_id in (select id from hr_employee "
            "where job_title in ('_32M_qst5', '_32Y_qst5', '_41M_qst5', '_41Y_qst5'));")
        self.env['hr.employee.entry.withdrawal'].flush()
        # set withdrawal for employee 32M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2022-03-31',
                self.env.ref('bt_swissdec.hr_employee_32M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Duss0_32M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_32M_qst5 does not exist')
        # set withdrawal for employee 32Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2022-03-31',
                self.env.ref('bt_swissdec.hr_employee_32Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Duss0_32Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_32Y_qst5 does not exist')

        # set withdrawal for employee 41M
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2022-03-31',
                self.env.ref('bt_swissdec.hr_employee_41M_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Maldini0_41M_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_41M_qst5 does not exist')
        # set withdrawal for employee 41Y
        try:
            self.create_qst_mutation_table_entry(
                user_demo2, 'withdrawal', 'withdrawalCompany', '2022-03-31',
                self.env.ref('bt_swissdec.hr_employee_41Y_qst5').with_user(user_demo2).id,
                self.env.ref('bt_swissdec.hr_entry_withdrawal_Maldini0_41Y_qst5').with_user(user_demo2).id
            )
        except:
            print('bt_swissdec.hr_employee_41Y_qst5 does not exist')
        # self.flush()

    def create_salary_and_qst_transmission(self, user, transmitter, journal_qst, bank, delete_gui_stat,
                                           raise_error_for_check_xml, year, month, salary_totals, year_id,
                                           xml_name_to_save='2.xml', create_dump_name=False):
        _logger.info("#############################")
        # used for salary_totals
        month_orig = month
        if int(month) > 12:
            month = int(month) - 12
            month = str(month)
            year = int(year) + 1
            year = str(year)
        _logger.info("Create Salary {0} {1}".format(month, year))
        _logger.info("Value year_id: {0}".format(year_id))
        payroll_register = self.create_payroll_register(
            user,
            "{0} {1}".format(month, year),
            "{0}-{1}-01".format(year, month),
            journal_qst,
            bank,
        )
        amount_payroll = sum(total[int(month_orig)-1] for total in salary_totals)
        _logger.info("salary_totals: {0}".format(salary_totals))
        _logger.info("salary_totals current month: {0}".format(amount_payroll))
        self.compute_payroll_register(payroll_register, amount_payroll)
        if delete_gui_stat:
            _logger.info("Create QST {0} {1} and delete it".format(month, year))
            self.create_gui_stat_form(
                user,
                transmitter,
                "{0} {1}".format(month, year),
                month_orig,
                self.browse_ref("bt_swissdec.qst_month_{0}".format(month.lstrip('0'))),
                year_id,
                raise_error_for_check_xml,
                xml_name_to_save,
                True,
            )

        _logger.info("Create QST {0} {1}".format(month, year))
        self.create_gui_stat_form(
            user,
            transmitter,
            "{0} {1}".format(month, year),
            month_orig,
            self.browse_ref("bt_swissdec.qst_month_{0}".format(month.lstrip('0'))),
            year_id,
            raise_error_for_check_xml,
            xml_name_to_save,
        )
        if create_dump_name:
            db_actual = self.env.cr.dbname
            month_year = "{0}_{1}".format(month, year)
            db_new = '{}_{}_{}'.format(db_actual, create_dump_name, month_year)
            self.env.cr.commit()
            subprocess.check_call("psql -d {} -c 'DROP DATABASE IF EXISTS {}'".format(db_actual, db_new), shell=True, stdout=subprocess.DEVNULL)
            subprocess.check_call('createdb {}'.format(db_new), shell=True, stdout=subprocess.DEVNULL)
            subprocess.check_call('pg_dump {} | psql {}'.format(db_actual, db_new), shell=True, stdout=subprocess.DEVNULL)
            subprocess.check_call("""psql -d {} -c "update ir_module_module set state = 'installed' where name = 'bt_swissdec';" """.format(db_new), shell=True, stdout=subprocess.DEVNULL)

    def create_entry_withdrawal(self, user, entry_date, emp_id):
        vals_entry = {
            'employee_id': emp_id,
            'date_start': entry_date,
        }
        new_entry = self.env['hr.employee.entry.withdrawal'].with_user(user).create(vals_entry)
        self.env['hr.employee.entry.withdrawal'].flush()
        return new_entry

    def create_qst_mutation_table_entry(self, user, internal_state, reason, valid_as_of_date, emp_id, entry_id):
        vals_qst_mutation = {
            'employee_id': emp_id,
            'review': True,
            'internal_state': internal_state,
            'state': 'to_send',
            'reason': reason,
            'automatic_generated': True,
            'valid_as_of_date': valid_as_of_date,
            'hr_employee_entry_withdrawal_id': entry_id,
        }
        self.env['qst_mutation_table'].with_user(user).create(vals_qst_mutation)
        self.env['qst_mutation_table'].flush()
        return True

    def compare_xml(self, name, model, month, company_id, xml_name_to_save):
        rec = self.env[model].search([('name', 'like', name)], limit=1)
        if company_id and company_id.name == 'PROCESS_5 AG':
            month += '_qst5'
        if not rec:
            return 9999
        is_yearly_test = False
        is_yearly_each_test = False
        is_yearly_only_test = False
        if month.startswith('ye'):
            is_yearly_each_test = True
            month = month[2:]
        elif month.startswith('yo'):
            is_yearly_only_test = True
            month = month[2:]
        elif month.startswith('y'):
            is_yearly_test = True
            month = month[1:]
        from . import __file__
        root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'xml_compare')
        try:
            # Removes the old diff_qst_month.txt
            # call via subprocess "python prepare.py jan/out-flow-report--message.xml  jan/2.xml"
            subprocess.call(['rm', '-rf', 'diff_qst_month.txt'])
            output = base64.b64decode(rec.execution_ids[0].output_binary)
            if isinstance(output, bytes):
                output = output.decode("utf-8")
            with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as tmp_file:
                subprocess.call(['echo', tmp_file.name])
                with open(tmp_file.name, 'w') as file_out:
                    file_out.write(output)
            sp_call_params = ['python', os.path.join(root_path, 'prepare.py'), tmp_file.name]
            if month == 'muster_2013':
                sp_call_params.append(os.path.join(root_path, 'temp.xml'))
                sp_call_params.append(os.path.join(root_path, 'muster_lohnmeldung_2013_to_compare_with.xml'))
            else:
                if month not in ('feb_saner', 'march_saner'):
                    if 'muster_ag' in month:
                        if month == 'muster_ag_jan_in_march':
                            compare_with_file = 'bt-good_jan_in_march.xml'
                        elif month == 'muster_ag_march_in_march':
                            compare_with_file = 'bt-good_march_in_march.xml'
                        else:
                            compare_with_file = 'bt-good_jan.xml'

                        sp_call_params.append(os.path.join(root_path, 'muster_ag', '2.xml'))
                        sp_call_params.append(os.path.join(root_path, 'muster_ag', compare_with_file))
                    else:
                        if is_yearly_test or is_yearly_each_test or is_yearly_only_test:
                            sp_call_params.append(
                                os.path.join(root_path, 'yearly_compensation_tests', month, '2.xml')
                            )
                            if is_yearly_test:
                                sp_call_params.append(
                                    os.path.join(root_path, 'yearly_compensation_tests', month, 'bt-good.xml')
                                )
                            elif is_yearly_each_test:
                                sp_call_params.append(
                                    os.path.join(root_path, 'yearly_compensation_tests', month, 'bt-good-each.xml')
                                )
                            else:
                                sp_call_params.append(
                                    os.path.join(root_path, 'yearly_compensation_tests', month, 'bt-good-only.xml')
                                )
                        else:
                            if month == 'may2015':
                                sp_call_params.append(os.path.join(root_path, 'may', '2.xml'))
                                sp_call_params.append(os.path.join(root_path, 'may', 'its-good-2015.xml'))
                            elif 'qst5' in month:
                                sp_call_params.append(os.path.join(root_path, month, xml_name_to_save))
                                sp_call_params.append(os.path.join(root_path, month, 'its-good-qst5.xml'))
                            else:
                                sp_call_params.append(os.path.join(root_path, month, '2.xml'))
                                sp_call_params.append(os.path.join(root_path, month, 'its-good.xml'))

                else:
                    if month == 'feb_saner':
                        month = 'feb'
                    else:
                        month = 'march'
                    sp_call_params.append(os.path.join(root_path, month, '2.xml'))
                    sp_call_params.append(
                        os.path.join(root_path, month, 'bt-good-test_saner_remove_qst_pflicht.xml')
                    )

            subprocess.call(sp_call_params)
            # get file size
            with open("diff_qst_month.txt", 'r') as f:
                st = os.fstat(f.fileno())
                file_size = st.st_size
                content = f.read()
            if file_size == 0:
                subprocess.call(['rm', '-rf', 'diff_qst_month.txt'])
            else:
                _logger.warning('Files differ: diff file size %s' % file_size)
                _logger.warning('Files differ: params "%s"' % sp_call_params)
                _logger.warning('Files differ: content "%s"' % content)
            return file_size
        except Exception as e:
            _logger.error(e)
            return 9998
        return 9997

    def run_process_ag5_full_test(self, user_demo2, journal_qst, bank, year, test_transmitter, delete_gui_stat,
                                  raise_error_for_check_xml, salary_totals, year_id, xml_name_to_save,
                                  create_dump_name):
        # Januar 2021
        self.run_before_sal_01_2021(user_demo2, journal_qst, bank, year)
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '01', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # Februar 2021
        self.run_before_sal_02_2021(user_demo2, journal_qst, bank, year)
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '02', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # März 2021
        self.run_before_sal_03_2021(user_demo2, journal_qst, bank, year)
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '03', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # April 2021
        self.run_before_sal_04_2021(user_demo2, journal_qst, bank, year)
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '04', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # Mai 2021
        self.run_before_sal_05_2021(user_demo2, journal_qst, bank, year)
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '05', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # Juni 2021
        self.run_before_sal_06_2021(user_demo2, journal_qst, bank, year)
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '06', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # Juli 2021
        self.run_before_sal_07_2021(user_demo2, journal_qst, bank, year)
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '07', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # August 2021
        self.run_before_sal_08_2021(user_demo2, journal_qst, bank, year)
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '08', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # September 2021
        self.run_before_sal_09_2021(user_demo2, journal_qst, bank, year)
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '09', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # Oktober 2021
        self.run_before_sal_10_2021(user_demo2, journal_qst, bank, year)
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '10', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # November 2021
        self.run_before_sal_11_2021(user_demo2, journal_qst, bank, year)
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '11', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # Dezember 2021
        self.run_before_sal_12_2021(user_demo2, journal_qst, bank, year)
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '12', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # # duplicate year 2021 in company
        # company = self.env.ref('bt_swissdec.second_company5').with_user(user_demo2)
        # company.create_year()
        # self.env.cr.execute('UPDATE res_company_year SET qst_tarif_import_done=True WHERE company_id=%s;',
        #                     (company.id,))
        # company.sudo().write({})
        #
        # try:
        #     self.env.cr.execute(
        #         "UPDATE hr_employee_calculationparameter_qst SET workdays_ch=9 WHERE year_id in (select id from "
        #         "hr_employee_year where employee_id in (select id from hr_employee where job_title in ('_32M_qst5', '_32Y_qst5')) and name = '2022') "
        #         "and valid_from='2022-01-01';")
        #     self.env.cr.execute(
        #         "UPDATE hr_employee_calculationparameter_qst SET workdays_ch=18 WHERE year_id in (select id from "
        #         "hr_employee_year where employee_id in (select id from hr_employee where job_title in ('_32M_qst5', '_32Y_qst5')) and name = '2022') "
        #         "and valid_from='2022-02-01';")
        #     self.env.cr.execute(
        #         "UPDATE hr_employee_calculationparameter_qst SET workdays_ch=11 WHERE year_id in (select id from "
        #         "hr_employee_year where employee_id in (select id from hr_employee where job_title in ('_32M_qst5', '_32Y_qst5')) and name = '2022') "
        #         "and valid_from='2022-03-01';")
        #
        #     # # set for all contracts the end date 2021-12-31 which should not be calculated any more in 2022
        #     # self.env.cr.execute("""UPDATE hr_contract SET date_end = '2021-12-31'
        #     #     WHERE date_end is null AND company_id = (select id from res_company where name = 'PROCESS_5 AG') AND
        #     #     name not in ('Duss_32M_qst5 Regula', 'Duss_32Y_qst5 Regula');""")
        #     # company.sudo().write({})
        # except:
        #     print('employee does not exist')
        #
        # company = self.env.ref('bt_swissdec.second_company5').with_user(user_demo2)
        # year_id = company.year_ids[0]
        # _logger.info("'{0}' year_id set: {1}".format(year_id.name, year_id.id))
        #
        # # Januar 2022
        # self.run_before_sal_01_2022(user_demo2, journal_qst, bank, year)
        # self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
        #                                         raise_error_for_check_xml, year, '13', salary_totals, year_id,
        #                                         xml_name_to_save)
        #
        # # Februar 2022
        # self.run_before_sal_02_2022(user_demo2, journal_qst, bank, year)
        # self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
        #                                         raise_error_for_check_xml, year, '14', salary_totals, year_id,
        #                                         xml_name_to_save)
        #
        # # März 2022
        # self.run_before_sal_03_2022(user_demo2, journal_qst, bank, year)
        # self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
        #                                         raise_error_for_check_xml, year, '15', salary_totals, year_id,
        #                                         xml_name_to_save)
