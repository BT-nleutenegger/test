##############################################################################
# Copyright (c) 2020 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from logging import getLogger

from .common import TestBTSwissdec

_logger = getLogger(__name__)


class TestProcessAG5ChangeQstCanton(TestBTSwissdec):

    def test_change_qst_canton(self):
        self.env.cr.execute('delete from hr_payslip;')
        self.env.cr.execute('delete from hr_payroll_register;')
        self.env.cr.execute('delete from account_move_line;')
        self.env.cr.execute('delete from account_move;')
        self.env.cr.execute('delete from account_move_line_salary;')
        self.env.cr.execute('delete from account_move_salary;')

        # All the test is executed as demo
        user_demo2 = self.demo2_5.id

        # install lang it_IT
        self.env["base.language.install"].sudo().create({'lang': 'it_IT', 'overwrite': True}).lang_install()

        # set lang to it_IT for all yearly employees
        self.env.cr.execute(
            "UPDATE hr_employee SET lang= 'it_IT' where job_title like '%Y_qst5';")

        run_only = False
        # This is only to run the tests to compare xml's for BERN (monthly)
        run_only = tuple(set(['_42M_qst5', '_42Y_qst5', '_43M_qst5', '_43Y_qst5']))
        if run_only:
            self.env.cr.execute(
                "delete from hr_payslip where employee_id in (select distinct id from hr_employee where job_title not in %s);",
                (run_only,))
            self.env.cr.execute(
                "delete from hr_work_entry where employee_id in (select distinct id from hr_employee where job_title not in %s);",
                (run_only,))
            self.env.cr.execute(
                "delete from hr_contract where employee_id in (select distinct id from hr_employee where job_title not in %s);",
                (run_only,))
            self.env.cr.execute(
                "delete from hr_employee_year where employee_id in (select id from hr_employee where job_title not in %s);",
                (run_only,))
            self.env.cr.execute(
                "delete from hr_employee_children where parent_id in (select distinct id from hr_employee where job_title not in %s);",
                (run_only,))
            self.env.cr.execute(
                "delete from hr_leave where employee_id in (select distinct id from hr_employee where job_title not in %s);",
                (run_only,))
            self.env.cr.execute(
                "delete from hr_leave_allocation where employee_id in (select distinct id from hr_employee where job_title not in %s);",
                (run_only,))
            self.env.cr.execute(
                "delete from hr_employee where job_title not in %s;", (run_only,))

        # Configure Transmitter
        _logger.info('Configure Transmitter')
        test_transmitter = self.env.ref('bt_swissdec.transmitter_configuration_0003_qst5').with_user(user_demo2)
        if test_transmitter.state_default != 'default':
            test_transmitter.action_next_next_state()
            test_transmitter.sudo().write({
                'group': 'identification_id_bt',
            })
            test_transmitter.action_state_default()

        # set 'Personalaufwand Lohn QST'
        journal_qst = self.browse_ref('bt_swissdec.account_journal_personalaufwandlohn0_qst5')
        # set 'Bank'
        bank = self.env['account.journal'].with_user(user_demo2).search([('name', '=', 'Bank')])
        # set year
        year = '2021'
        year_id = self.browse_ref('bt_swissdec.year2021_qst5')
        # if this value is set to True it will first create a gui_stat, delete it and create a new one
        delete_gui_stat = False
        # if this value is set to True it will raise an error if the xml check fails
        raise_error_for_check_xml = False
        # if create_dump_name is set we create a dump after each month
        create_dump_name = '4_change_incl_42_send_again'
        create_dump_name = False
        xml_name_to_save = '4_change_qst_canton_incl_42_send_again_test.xml'

        salary_totals = [
            [4525, 4525, 4525, 4525, 4525, 5335, 5664.4, 5085.6, 5085.6, 5085.6, 5085.6, 9190.2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # M42
            [4525, 4525, 4525, 4525, 4525, 5335, 5637.4, 5090.8, 5090.8, 5070.8, 5090.8, 9644.4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Y42
            [4525, 24465, 4525, 4525, 4525, 4795, 4795, 4795, 4795, 4795, 4900, 9330, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # MY44
            [4525, 29955, 4310, 4310, 4310, 4570, 4570, 4570, 4795, 4795, 4900, 9050, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # YM43
        ]

        # Januar 2021
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '01', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # Februar 2021
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '02', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # März 2021
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '03', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # April 2021
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '04', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # Mai 2021
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '05', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # Juni 2021
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

        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '06', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # Juli 2021
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

        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '07', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        try:
            # we need to set for 43M and 43Y from jan on qst to needs_to_be_send_in_xml = True (triggered after qst import)
            self.env.cr.execute(
                "UPDATE hr_employee_calculationparameter_qst SET needs_to_be_send_in_xml = True, "
                "test_scenario_id = Null WHERE year_id in (select id from "
                "hr_employee_year where employee_id in (select id from hr_employee where job_title in ('_42M_qst5', '_42Y_qst5', '_43M_qst5', '_43Y_qst5')) and name = '2021') "
                "and sent_in_xml = True;")
            self.env['hr.employee.calculationparameter.qst'].flush()
        except:
            print('employee 43M or 43Y does not exist')

        # August 2021
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '08', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # September 2021
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '09', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # Oktober 2021
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '10', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # November 2021
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '11', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        # Dezember 2021
        self.create_salary_and_qst_transmission(user_demo2, test_transmitter, journal_qst, bank, delete_gui_stat,
                                                raise_error_for_check_xml, year, '12', salary_totals, year_id,
                                                xml_name_to_save, create_dump_name)

        self.env.cr.commit()

        # delete db and create new from backup (*_b)
        self.restore_backup_db()
