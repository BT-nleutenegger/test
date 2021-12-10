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


class TestMusterAGFullTestInstallation(TestBTSwissdec):

    def test_full_test_installation(self):
        _logger.info('OKTOBER 2012 - Auszuführen vor Lohn Oktober 2012')

        # The following write can be executed as sudo
        contract_ids = [
            self.ref('bt_swissdec.hr_contract_ganzedith0'),
            self.ref('bt_swissdec.hr_contract_paganinimaria0'),
            self.ref('bt_swissdec.hr_contract_otthans0'),
            self.ref('bt_swissdec.hr_contract_lusserpia0'),
            self.ref('bt_swissdec.hr_contract_kaiserbeat0'),
            self.ref('bt_swissdec.hr_contract_jungclaude0'),
            self.ref('bt_swissdec.hr_contract_ingleserosa0'),
            self.ref('bt_swissdec.hr_contract_herzmonica0'),
            self.ref('bt_swissdec.hr_contract_eglianna0'),
            self.ref('bt_swissdec.hr_contract_combertaldirenato0'),
            self.ref('bt_swissdec.hr_contract_dussregula0'),
        ]
        # install_mode is needed to ignore constraints
        self.env['hr.contract'].sudo().browse(contract_ids).with_context(install_mode=True).write({
            'date_start': '2013-01-01',
        })

        # All the test is executed as demo
        user_demo = self.ref('base.user_demo')

        _logger.info('Create Lohn Oktober 2012')
        # 'Personalaufwand Lohn'
        journal = self.browse_ref('bt_swissdec.account_journal_personalaufwandlohn0')
        # 'Bank'
        bank = self.env['account.journal'].with_user(user_demo).search([('name', '=', 'Bank')])
        self.assertTrue(len(bank) == 1, 'We expected to find an account journal named Bank')
        payroll_register = self.create_payroll_register(
            user_demo,
            'Oktober 2012',
            '2012-10-01',
            journal,
            bank,
        )

        _logger.info('Auszuführen nach Lohn Oktober 2012')
        payslips_to_remove_names = [
            'Lohnabrechnung von Bosshard Peter Oktober 2012',
            'Lohnabrechnung von Farine Corinne Oktober 2012',
            'Lohnabrechnung von Moser Johann Oktober 2012',
            'Lohnabrechnung von Racine Susette Oktober 2012',
        ]
        payslips_to_remove = self.env['hr.payslip'].sudo().search([('name', 'in', payslips_to_remove_names)])
        self.assertTrue(
            len(payslips_to_remove) == len(payslips_to_remove_names),
            'We expected to find %s payslip to remove but we found %s: %s' % (
                len(payslips_to_remove_names),
                len(payslips_to_remove),
                ', '.join(payslips_to_remove.mapped('display_name'))
            )
        )
        payslips_to_remove.unlink()
        self.env.ref('bt_swissdec.hr_contract_fankhausermarkus0').sudo().with_context(install_mode=True).write({
            'date_start': '1977-08-01',
        })
        self.env.ref('bt_swissdec.hr_contract_moserjohann0').sudo().with_context(install_mode=True).write({
            'date_start': '1972-03-01',
        })
        self.env.ref('bt_swissdec.hr_contract_racinesusette0').sudo().with_context(install_mode=True).write({
            'date_start': '1967-04-01',
        })
        self.env.ref('bt_swissdec.hr_contract_zahndanita0').sudo().with_context(install_mode=True).write({
            'date_start': '1992-02-01',
        })

        self.compute_payroll_register(payroll_register, 259014.15)
        _logger.info('LOHN OKTOBER 2012 booked')

        _logger.info('DEZEMBER 2012 - Create Lohn Dezember 2012')
        payroll_register = self.create_payroll_register(
            user_demo,
            'Dezember 2012',
            '2012-12-01',
            journal,
            bank,
        )

        _logger.info('Auszuführen nach Lohn Dezember 2012')
        payslips_to_remove_names = [
            'Lohnabrechnung von Bosshard Peter Dezember 2012',
            'Lohnabrechnung von Farine Corinne Dezember 2012',
        ]
        payslips_to_remove = self.env['hr.payslip'].sudo().search([('name', 'in', payslips_to_remove_names)])
        self.assertTrue(
            len(payslips_to_remove) == len(payslips_to_remove_names),
            'We expected to find %s payslip to remove but we found %s: %s' % (
                len(payslips_to_remove_names),
                len(payslips_to_remove),
                ', '.join(payslips_to_remove.mapped('display_name'))
            )
        )
        payslips_to_remove.unlink()
        self.env.ref('bt_swissdec.hr_contract_ganzedith0').sudo().with_context(install_mode=True).write({
            'date_start': '2011-06-01',
        })
        self.env.ref('bt_swissdec.hr_contract_paganinimaria0').sudo().with_context(install_mode=True).write({
            'date_start': '2010-06-01',
        })
        self.env.ref('bt_swissdec.hr_contract_otthans0').sudo().with_context(install_mode=True).write({
            'date_start': '2012-09-01',
        })
        self.env.ref('bt_swissdec.hr_contract_lusserpia0').sudo().with_context(install_mode=True).write({
            'date_start': '2012-08-01',
        })
        self.env.ref('bt_swissdec.hr_contract_kaiserbeat0').sudo().with_context(install_mode=True).write({
            'date_start': '2010-01-01',
        })
        self.env.ref('bt_swissdec.hr_contract_jungclaude0').sudo().with_context(install_mode=True).write({
            'date_start': '2012-10-01',
        })
        self.env.ref('bt_swissdec.hr_contract_ingleserosa0').sudo().with_context(install_mode=True).write({
            'date_start': '2012-10-01',
        })
        self.env.ref('bt_swissdec.hr_contract_herzmonica0').sudo().with_context(install_mode=True).write({
            'date_start': '2012-11-01',
        })
        self.env.ref('bt_swissdec.hr_contract_eglianna0').sudo().with_context(install_mode=True).write({
            'date_start': '2012-12-01',
        })
        self.env.ref('bt_swissdec.hr_contract_combertaldirenato0').sudo().with_context(install_mode=True).write({
            'date_start': '2011-06-01',
        })
        self.env.ref('bt_swissdec.hr_contract_dussregula0').sudo().with_context(install_mode=True).write({
            'date_start': '2012-05-01',
        })
        self.env.ref('bt_swissdec.hr_contract_farinecorinne0').sudo().with_context(install_mode=True).write({
            'date_start': '2011-08-01',
        })
        self.env.ref('bt_swissdec.hr_contract_bosshardpeter0').sudo().with_context(install_mode=True).write({
            'date_start': '2010-07-01',
        })

        self.compute_payroll_register(payroll_register, 501956.00)

        employees = [
            self.browse_ref('bt_swissdec.hr_employee25'),
            self.browse_ref('bt_swissdec.hr_employee24'),
            self.browse_ref('bt_swissdec.hr_employee22'),
            self.browse_ref('bt_swissdec.hr_employee29'),
            self.browse_ref('bt_swissdec.hr_employee28'),
            self.browse_ref('bt_swissdec.hr_employee23'),
            self.browse_ref('bt_swissdec.hr_employee27'),
        ]
        self.create_lohn(user_demo, 'Februar 2013', employees, journal, bank, '2013-02-01', True)

        _logger.info('February 2013')
        payroll_register = self.create_payroll_register(
            user_demo,
            'Februar 2013',
            '2013-02-01',
            journal,
            bank,
        )
        self.compute_payroll_register(payroll_register, 372287.70)

        employees = [
            self.browse_ref('bt_swissdec.hr_employee25'),
            self.browse_ref('bt_swissdec.hr_employee26'),
        ]
        self.create_lohn(user_demo, 'März 2013', employees, journal, bank, '2013-03-01', True)
        _logger.info('März 2013')
        payroll_register = self.create_payroll_register(
            user_demo,
            'März 2013',
            '2013-03-01',
            journal,
            bank,
        )
        self.compute_payroll_register(payroll_register, 354032.30)

        employees = [
            self.browse_ref('bt_swissdec.hr_employee21'),
            self.browse_ref('bt_swissdec.hr_employee11'),
        ]
        self.create_lohn(user_demo, 'Oktober 2013', employees, journal, bank, '2013-10-01', True)
        _logger.info('Oktober 2013')
        payroll_register = self.create_payroll_register(
            user_demo,
            'Oktober 2013',
            '2013-10-01',
            journal,
            bank,
        )
        self.compute_payroll_register(payroll_register, 379901.55)

        employees = [
            self.browse_ref('bt_swissdec.hr_employee5'),
            self.browse_ref('bt_swissdec.hr_employee10'),
            self.browse_ref('bt_swissdec.hr_employee13'),
        ]
        self.create_lohn(user_demo, 'Dezember 2013', employees, journal, bank, '2013-12-01', True)
        _logger.info('Dezember 2013')
        payroll_register = self.create_payroll_register(
            user_demo,
            'Dezember 2013',
            '2013-12-01',
            journal,
            bank,
        )
        self.compute_payroll_register(payroll_register, 499590.85)

        _logger.info('Auszuführen nach Lohn Dezember 2013 damit XML korrekt erstellt werden kann')
        self.env['hr.allounce.deduction.categoty'].sudo().search([('matrix_nr', '=', '1005')]).write({
            'uom_id': self.ref('uom.product_uom_hour'),
        })
        self.env['hr.allounce.deduction.categoty'].sudo().search([('matrix_nr', '=', '1006')]).write({
            'uom_id': self.ref('bt_swissdec.product_uom_lektion'),
        })
        self.env['hr.allounce.deduction.categoty'].sudo().search([('matrix_nr', '=', '1000')]).write({
            'uom_id': None,
        })

        _logger.info('Configure Transmitter')
        test_transmitter = self.env.ref('bt_swissdec.transmitter_configuration_0003').with_user(user_demo)
        test_transmitter.action_next_next_state()
        test_transmitter.sudo().write({
            'group': 'identification_id_bt',
        })
        test_transmitter.action_state_default()

        _logger.info('Create year 2014 Muster AG')
        muster_ag = self.env.ref('base.main_company').with_user(user_demo)
        muster_ag.create_year()

        _logger.info('Create Lohnmeldung 2013')
        gui_salary_declaration_form = Form(self.env['gui_salary_declaration'].with_user(user_demo))
        gui_salary_declaration_form.name = '2013'
        year = self.env['res.company.year'].with_user(user_demo).search([('name', '=', '2013')])
        self.assertTrue(len(year) == 1, 'We expected to find a year journal named "2013"')
        gui_salary_declaration_form.year_id = year
        gui_salary_declaration = gui_salary_declaration_form.save()
        gui_salary_declaration.select_all()
        with Form(gui_salary_declaration) as gui_salary_declaration_new:
            gui_salary_declaration_new.fak_with_detail = True
        gui_salary_declaration.action_send_salary_declaration()

        _logger.info('we can stop here, we just want to check if xml data is correct')

        _logger.info('Test Compare XML Lohnmeldung 2013')
        compare_xml = self.compare_xml('2013', 'gui_salary_declaration', 'muster_2013')
        _logger.info(compare_xml)
        self.assertTrue(compare_xml == 0, 'The comparison with the XML went wrong: Files are different')
