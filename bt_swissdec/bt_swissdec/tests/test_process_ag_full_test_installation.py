##############################################################################
# Copyright (c) 2020 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from logging import getLogger

from .common import TestBTSwissdec
from odoo.tests.common import Form

_logger = getLogger(__name__)


class TestProcessAGFullTestInstallation(TestBTSwissdec):

    def test_001_full_test_installation(self):
        _logger.info('OKTOBER 2013 - Auszuführen vor Lohn Oktober 2013')

        # The following write can be executed as sudo
        contract_ids = [
            self.ref('bt_swissdec.hr_contract_1'),
            self.ref('bt_swissdec.hr_contract_2'),
            self.ref('bt_swissdec.hr_contract_3'),
            self.ref('bt_swissdec.hr_contract_5'),
            self.ref('bt_swissdec.hr_contract_6'),
            self.ref('bt_swissdec.hr_contract_7'),
            self.ref('bt_swissdec.hr_contract_8'),
            self.ref('bt_swissdec.hr_contract_9'),
            self.ref('bt_swissdec.hr_contract_10'),
            self.ref('bt_swissdec.hr_contract_11'),
            self.ref('bt_swissdec.hr_contract_13'),
            self.ref('bt_swissdec.hr_contract_15'),
        ]
        # install_mode is needed to ignore constraints
        self.env['hr.contract'].sudo().browse(contract_ids).with_context(install_mode=True).write({
            'date_start': '2014-01-01',
        })

        # All the test is executed as demo
        user_demo2 = self.demo2.id

        _logger.info('OKTOBER 2013 - Create Lohn Oktober 2013')
        # 'Personalaufwand Lohn QST'
        journal_qst = self.browse_ref('bt_swissdec.account_journal_personalaufwandlohn0_qst')
        # 'Bank'
        bank = self.env['account.journal'].with_user(user_demo2).search([('name', '=', 'Bank')])
        payslip = self.create_payslip(
            user_demo2, self.browse_ref('bt_swissdec.hr_employee14_qst'), journal_qst, bank, '2013-10-01', False
        )

        # In selenium, it was needed to delete a record. Unit tests do not need it
        # _logger.info('OKTOBER 2013 - '
        #              'Delete payslip - strange error related to session_id which I could not find out')
        # payslip.unlink()
        # _logger.info('OKTOBER 2013 - Create Lohn Oktober 2013')
        # payslip = self.create_payslip(
        #     user_demo2, self.browse_ref('bt_swissdec.hr_employee14_qst'), journal_qst, bank, '2013-10-01', False
        # )
        line = payslip.line_ids.filtered(
            lambda l: l.category_adc_id.display_name == '5060 - Quellensteuerabzug'
        )
        self.assertEqual(len(line), 1)
        line_form = Form(line.with_user(user_demo2))
        line.amount = 9
        line_form.save()

        payroll_register = self.create_payroll_register(
            user_demo2,
            'Oktober 2013',
            '2013-10-01',
            journal_qst,
            bank,
        )
        self.compute_payroll_register(payroll_register, 66632.00)

        # install_mode is needed to ignore constraints
        contract_ids_20130101 = [
            self.ref('bt_swissdec.hr_contract_1'),
            self.ref('bt_swissdec.hr_contract_2'),
            self.ref('bt_swissdec.hr_contract_3'),
            self.ref('bt_swissdec.hr_contract_7'),
            self.ref('bt_swissdec.hr_contract_8'),
            self.ref('bt_swissdec.hr_contract_9'),
            self.ref('bt_swissdec.hr_contract_10'),
            self.ref('bt_swissdec.hr_contract_11'),
            self.ref('bt_swissdec.hr_contract_15'),
        ]
        contract_ids_20130501 = [
            self.ref('bt_swissdec.hr_contract_5'),
        ]
        contract_ids_20130601 = [
            self.ref('bt_swissdec.hr_contract_6'),
        ]
        contract_ids_20131001 = [
            self.ref('bt_swissdec.hr_contract_13'),
        ]

        self.env['hr.contract'].sudo().browse(contract_ids_20130101).with_context(install_mode=True).write({
            'date_start': '2013-01-01',
        })
        self.env['hr.contract'].sudo().browse(contract_ids_20130501).with_context(install_mode=True).write({
            'date_start': '2013-05-01',
        })
        self.env['hr.contract'].sudo().browse(contract_ids_20130601).with_context(install_mode=True).write({
            'date_start': '2013-06-01',
        })
        self.env['hr.contract'].sudo().browse(contract_ids_20131001).with_context(install_mode=True).write({
            'date_start': '2013-10-01',
        })

        _logger.info('Set Entry Date for Oberli Christine')
        emp_form = Form(self.browse_ref('bt_swissdec.hr_employee12_qst').with_user(user_demo2))
        emp_form.new_entry_date_start = '2014-01-16'
        emp_form.save()

        _logger.info('JANUAR 2014 - Create Lohn Januar 2014')
        self.create_payslip(
            user_demo2, self.browse_ref('bt_swissdec.hr_employee14_qst'), journal_qst, bank, '2014-01-01', True,
            zahlung_nach_austritt_qst_separate_sb=True
        )
        payroll_register = self.create_payroll_register(
            user_demo2,
            'Januar 2014',
            '2014-01-01',
            journal_qst,
            bank,
        )
        self.compute_payroll_register(payroll_register, 59786.25)

        _logger.info('Configure Transmitter')
        test_transmitter = self.env.ref('bt_swissdec.transmitter_configuration_0003_qst').with_user(user_demo2)
        test_transmitter.action_next_next_state()
        test_transmitter.sudo().write({
            'group': 'identification_id_bt',
        })
        test_transmitter.action_state_default()

        _logger.info('Create QST Januar 2014 and delete it')
        gui_tax_at_source_transmission_form = Form(
            self.env['gui_tax_at_source_transmission'].with_user(user_demo2)
        )
        gui_tax_at_source_transmission_form.name = 'Januar2014'
        gui_tax_at_source_transmission_form.transmitter_configuration_id = test_transmitter
        gui_tax_at_source_transmission_form.qst_month_id = self.browse_ref('bt_swissdec.qst_month_1')
        gui_tax_at_source_transmission = gui_tax_at_source_transmission_form.save()
        gui_tax_at_source_transmission.action_print_data_review()
        gui_tax_at_source_transmission.unlink()

        _logger.info('Create QST Januar 2014')
        gui_tax_at_source_transmission_form = Form(
            self.env['gui_tax_at_source_transmission'].with_user(user_demo2)
        )
        gui_tax_at_source_transmission_form.name = 'Januar2014'
        gui_tax_at_source_transmission_form.qst_month_id = self.browse_ref('bt_swissdec.qst_month_1')
        gui_tax_at_source_transmission = gui_tax_at_source_transmission_form.save()
        gui_tax_at_source_transmission.action_print_data_review()
        gui_tax_at_source_transmission.action_send_declaration()
        _logger.info('Test Compare XML')
        compare_xml = self.compare_xml('Januar 2014', 'gui_tax_at_source_transmission', 'jan')
        _logger.info(compare_xml)
        self.assertTrue(compare_xml == 0, 'The comparison with the XML went wrong: Files are different')

        self.env['gui_stat'].sudo().write({
            'advance_mode': True,
        })

        gui_tax_at_source_transmission.action_get_status()
        gui_tax_at_source_transmission.all_get_all_information()
        gui_tax_at_source_transmission.do_next()

        _logger.info('Change February - Change canton for Maldini Fabio')
        # https://github.com/brain-tec/bt-swissdec-testing/blob/13.0/bt_swissdec_testing/selenium_tests/swissdec_PROCESS_AG_full_test_installation.robot#L268
