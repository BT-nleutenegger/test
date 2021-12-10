##############################################################################
# Copyright (c) 2020 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from logging import getLogger

from .common import TestBTSwissdec

_logger = getLogger(__name__)


class TestProcessAGFullTestInstallation(TestBTSwissdec):

    def test_001_full_test_installation(self):
        # All the test is executed as demo
        user_demo2 = self.demo2_5.id

        # install lang it_IT
        self.env["base.language.install"].sudo().create({'lang': 'it_IT', 'overwrite': True}).lang_install()

        # set lang to it_IT for all yearly employees
        self.env.cr.execute(
            "UPDATE hr_employee SET lang= 'it_IT' where job_title like '%Y_qst5';")

        # This is only to run the tests to compare xml's for TESSIN (yearly)
        run_only = tuple(set(['_1Y_qst5','_7Y_qst5','_7_1Y_qst5','_9Y_qst5','_11_1Y_qst5','_15Y_qst5','_24Y_qst5','_25Y_qst5','_26Y_qst5','_27Y_qst5','_28Y_qst5','_29Y_qst5','_31Y_qst5','_32Y_qst5','_33Y_qst5','_35Y_qst5','_36Y_qst5','_37Y_qst5','_38Y_qst5','_39Y_qst5','_42Y_qst5']))
        if run_only:
            self.env.cr.execute(
                "delete from hr_payslip where employee_id in (select distinct id from hr_employee where job_title not in %s);", (run_only,))
            self.env.cr.execute(
                "delete from hr_work_entry where employee_id in (select distinct id from hr_employee where job_title not in %s);", (run_only,))
            self.env.cr.execute(
                "delete from hr_contract where employee_id in (select distinct id from hr_employee where job_title not in %s);", (run_only,))
            self.env.cr.execute(
                "delete from hr_employee_year where employee_id in (select id from hr_employee where job_title not in %s);", (run_only,))
            self.env.cr.execute(
                "delete from hr_employee_children where parent_id in (select distinct id from hr_employee where job_title not in %s);", (run_only,))
            self.env.cr.execute(
                "delete from hr_leave where employee_id in (select distinct id from hr_employee where job_title not in %s);", (run_only,))
            self.env.cr.execute(
                "delete from hr_leave_allocation where employee_id in (select distinct id from hr_employee where job_title not in %s);", (run_only,))
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
        # test XML's yearly
        salary_totals = [
            [2880, 2880, 7008, 2923, 2889, 8147, 2945.5, 2916.5, 5988.6, 2917.2, 2892.9, 9731.3, 0, 0, 0, 0],  # Y1
            [3843, 3843, 3843, 3843, 3843, 3843, 3843, 3843, 3843, 3843, 3843, 7159.5, 0, 0, 0, 0],  # Y7
            [3843, 3843, 3843, 3843, 3843, 3843, 0, 0, 0, 3843, 3843, 6330.37, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            # Y7_1
            [1018.5, 1018.5, 1018.5, 1018.5, 1018.5, 1018.5, 1018.5, 1018.5, 2502.15, 2056.63, 1771.31, 2337.96, 0,
             0, 0, 0],  # Y9
            [2371.2, 2371.2, 2371.2, 2496, 2519.4, 2519.4, 2532.4, 2537.6, 2535, 2498.6, 2532.4, 4791.8, 0, 0, 0, 0],  # Y11_AG1
            [4167.80, 3873.45, 4020.62, 4306.57, 3734.67, 3318.00, 4496.46, 3769.50, 4188.10, 3065.83, 3914.40,
             4189.85, 0, 0, 0, 0],  # Y15
            [3592, 3592, 4373, 3590, 3606, 4636, 6488, 3801, 4626, 3919, 3872, 4780, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0],  # Y24
            [3896, 3896, 3896, 3896, 3896, 3896, 3896, 3896, 3896, 3756, 3756, 7192, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0],  # Y25
            [4525, 29955, 4310, 4310, 4310, 4570, 4570, 4570, 4570, 4570, 4720, 8815, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0],  # Y26
            [5322, 5322, 5322, 5322, 5322, 5322, 5322, 5451.2, 5648.2, 5635.8, 5995.4, 11213.6, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],  # Y27
            [5629.6, 5629.6, 5629.6, 5629.6, 5629.6, 5629.6, 5629.6, 5629.6, 5629.6, 5304, 5304, 10073.4, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0],  # Y28
            [7248, 7248, 7248, 7248, 7248, 7248, 9553, 9609, 9521, 9107, 9063, 9133, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0],  # Y29
            [0, 6942.86, 10956.54, 9936.89, 12000, 8699.32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Y31
            [0, 0, 0, 0, 8310, 9577.5, 9324, 8901.5, 8310, 9408.5, 8648, 9746.5, 9239.5, 34733.5, 8922, 0, 0, 0, 0,
             0, 0, 0, 0],  # Y32
            [5347.5, 23332.5, 5452.2, 5302.8, 5004, 5452.2, 5601.6, 5352.6, 5004, 5651.4, 5203.2, 10474.85,
             4181.92, 13373.37, 0, 0, 0, 0, 0, 0, 0, 0],  # Y33
            [4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 0, 397.5, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],  # Y35
            [4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 0,
             381, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Y36
            [4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 0, 27180, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],  # Y37
            [5820, 22513.34, 5666.67, 5666.67, 5666.67, 5666.67, 5666.67, 5666.67, 5666.67, 5666.67, 5666.67,
             5666.67, 0, 25200, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Y38
            [3960, 3960, 3960, 9002, 4137, 4107.4, 4132.8, 4132.8, 4132.8, 4132.8, 4132.8, 7892.4, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0],  # Y39
            [4525, 4525, 4525, 4525, 4525, 5335, 5637.4, 5090.8, 5090.8, 5070.8, 5090.8, 9644.4, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],  # Y42
        ]
        create_dump_name = '9_y'
        create_dump_name = False
        xml_name_to_save = '9_y_test.xml'

        self.run_process_ag5_full_test(
            user_demo2, journal_qst, bank, year, test_transmitter, delete_gui_stat, raise_error_for_check_xml,
            salary_totals, year_id, xml_name_to_save, create_dump_name)

        self.env.cr.commit()

        # delete db and create new from backup (*_b)
        self.restore_backup_db()
