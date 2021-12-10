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

        # This is only to run the tests to compare xml's for BERN (monthly)
        run_only = tuple(set(['_1M_qst5','_7M_qst5','_9M_qst5','_11_1M_qst5','_15M_qst5','_24M_qst5','_25M_qst5','_26M_qst5','_27M_qst5','_28M_qst5','_29M_qst5','_31M_qst5','_32M_qst5','_33M_qst5','_35M_qst5','_36M_qst5','_37M_qst5','_38M_qst5','_39M_qst5','_42M_qst5']))
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
        # test XML's monthly
        salary_totals = [
            [2880, 2880, 6840, 2880, 2880, 7942, 2880, 2880, 5922.8, 2880, 2880, 9372.5, 0, 0, 0, 0],  # M1
            [3843, 3843, 3843, 3843, 3843, 3843, 3843, 3843, 3843, 3843, 3843, 6966, 0, 0, 0, 0],  # M7
            [1018.5, 1018.5, 1018.5, 1018.5, 1018.5, 1018.5, 1018.5, 1018.5, 2446.5, 2041.97, 1754.83, 2320.99, 0,
             0, 0, 0],  # M9
            [2371.2, 2371.2, 2371.2, 2511.6, 2511.6, 2511.6, 2511.6, 2511.6, 2511.6, 2511.6, 2511.6, 4685.2, 0, 0,
             0, 0],  # M11_AG1
            [4167.80, 3880.80, 4020.62, 4304.47, 3735.20, 3304.00, 4463.90, 3771.42, 4195.10, 3042.90, 3914.40,
             4195.10, 0, 0, 0, 0],  # M15
            [3592, 3592, 4365, 3592, 3592, 4635, 6307, 3804, 4635, 3896, 3896, 4795, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0],  # M24
            [3896, 3896, 3896, 3896, 3896, 3896, 3896, 3896, 3896, 3756, 3756, 6896, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0],  # M25
            [4525, 24465, 4525, 4525, 4525, 4795, 4795, 4795, 4795, 4795, 4900, 9050, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0],  # M26
            [5322, 5322, 5322, 5322, 5322, 5322, 5322, 5480.8, 5629.6, 5629.6, 5983, 10650.6, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0],  # M27
            [5629.6, 5629.6, 5629.6, 5629.6, 5629.6, 5629.6, 5629.6, 5629.6, 5629.6, 5322, 5322, 9864, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0],  # M28
            [7248, 7248, 7248, 7248, 7248, 7248, 9493, 9493, 9493, 9163, 9163, 9163, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0],  # M29
            [0, 6942.86, 10968.6, 9937.2, 12000, 8571.03, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            # # M31
            [0, 0, 0, 0, 8310, 9577.5, 9324, 8901.5, 8310, 9408.5, 8648, 9746.5, 9239.5, 31836.25, 9070.5, 0, 0, 0,
             0, 0, 0, 0, 0],  # M32
            [5347.5, 21613.5, 5521.5, 5391, 5130, 5521.5, 5652, 5434.5, 5130, 5695.5, 5304, 10532.8, 3988.58,
             12199.12, 0, 0, 0, 0, 0, 0, 0, 0],  # M33
            [4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 0, 387.5, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],  # M35
            [4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 0,
             387.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # M36
            [4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 4922.5, 0, 21300, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],  # M37
            [5820, 19226.67, 5820, 5820, 5820, 5820, 5820, 5820, 5820, 5820, 5820, 5820, 0, 20880, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0],  # M38
            [3960, 3960, 3960, 8418, 4145.4, 4145.4, 4145.4, 4145.4, 4145.4, 4145.4, 4145.4, 7626, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0],  # M39
            [4525, 4525, 4525, 4525, 4525, 5335, 5664.4, 5085.6, 5085.6, 5085.6, 5085.6, 9190.2, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],  # M42
        ]
        create_dump_name = '9_m'
        create_dump_name = False
        xml_name_to_save = '9_m_test.xml'

        self.run_process_ag5_full_test(
            user_demo2, journal_qst, bank, year, test_transmitter, delete_gui_stat, raise_error_for_check_xml,
            salary_totals, year_id, xml_name_to_save, create_dump_name)

        self.env.cr.commit()

        # delete db and create new from backup (*_b)
        self.restore_backup_db()
