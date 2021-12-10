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


class TestMusterAGConsolidatedSalaryBookings(TestBTSwissdec):

    def test_consolidated_salary(self):
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
        # set year
        company_year = self.env['res.company'].browse(1)
        company_year.create_year() # 2014
        # employees : Nuenz Maria, Lusser Pia, Estermann Michael, Egli Anna,Combertaldi Renato
        # Employees: Egli Anna, Lusser Pia, Ott Hans
        self.env.cr.execute("update hr_contract set date_end = '2013-12-31', state = 'close' "
                            "where id not in ('24','35','39') "
                            "and company_id in (select id from res_company where name = 'MUSTER AG')")
        self.env.cr.execute("update hr_payslip_grosswage_line set date_to = '2015-12-31' "
                            "where employee_id in ('40','28','36') and date_to = '2014-12-31'")
        self.env.cr.execute("update res_company_year set salary_consolidated_lines = true "
                            "where company_name = 'MUSTER AG' and name = '2014'")
        self.env.cr.execute("delete from account_move where id = 1")

        # create 2014
        payroll_register_form = Form(self.env['hr.payroll.register'])
        payroll_register_form.name = 'test_2014'
        payroll_register_form.date = '2014-1-1'
        payroll_register_form.journal_id = journal
        payroll_register_form.payment_journal_id = bank
        payroll_register = payroll_register_form.save()
        payroll_register.compute_sheet_check_wizard()
        # compute
        payroll_register.approval2()
        payroll_register.verify_sheet()
        payroll_register.final_verify_sheet()
        payroll_register.process_sheet()
        # consolidation
        move_salary_transfer_wizard = self.env['account.move.salary.transfer.wizard'].create({
            'date_from': '2014-1-1',
            'date_to': '2014-1-31',
            'date_posting': '2014-1-1'})
        move_salary_transfer_wizard.transfer_account_move()
        # create 2015
        company_year.create_year() # 2015
        payroll_register_form = Form(self.env['hr.payroll.register'])
        payroll_register_form.name = 'test_2015'
        payroll_register_form.date = '2015-1-1'
        payroll_register_form.journal_id = journal
        payroll_register_form.payment_journal_id = bank
        payroll_register = payroll_register_form.save()
        payroll_register.compute_sheet_check_wizard()
        # compute
        payroll_register.approval2()
        payroll_register.verify_sheet()
        payroll_register.final_verify_sheet()
        payroll_register.process_sheet()

        account_moves_14 = sum(move.amount_total for move in self.env['account.move'].search([('date', '=', '2014-1-1')]))
        account_moves_15 = sum(move.amount_total for move in self.env['account.move'].search([('date', '=', '2015-1-1')]))
        self.assertTrue(
            round(account_moves_14, 2) == round(account_moves_15, 2),
            'The consolidated lines (%s) and the directly booked lines (%s) '
            'have not the same total.' % (account_moves_14,account_moves_15)
        )
        # account.move tests
        different_journals = self.env['account.move'].read_group(['|',
                                                                 ('date', '=', '2015-1-1'),
                                                                 ('date', '=', '2014-1-1')],
                                                                 fields=['journal_id'], groupby=['journal_id'])
        for journal in different_journals:
            account_moves_journal_14 = \
                sum(move.amount_total for move in self.env['account.move'].search([('date', '=', '2014-1-1'),
                                                     ('journal_id', '=', journal['journal_id'][0])]))
            account_moves_journal_15 = \
                sum(move.amount_total for move in self.env['account.move'].search([('date', '=', '2015-1-1'),
                                                     ('journal_id', '=', journal['journal_id'][0])]))
            self.assertTrue(round(account_moves_journal_14, 2) == round(account_moves_journal_15, 2),
                'The consolidated lines (%s) and the directly booked lines (%s) from the same journal (%s) '
                'have not the same total.' % (account_moves_journal_14, account_moves_journal_15, journal['journal_id'])
            )
        # account.move.line test
        distinct_transfer_accounts_line = self.env['account.move.line'].read_group(
            ['|',
             ('date', '=', '2015-1-1'),
             ('date', '=', '2014-1-1')],
            fields=['account_id'], groupby=['account_id'])
        for account in distinct_transfer_accounts_line:
            different_journals = self.env['account.move.line'].read_group(
                [('account_id', '=', account['account_id'][0]),
                 '|',
                 ('date', '=', '2015-1-1'),
                 ('date', '=', '2014-1-1')],
                fields=['journal_id'],
                groupby=['journal_id'])
            for journal in different_journals:
                account_moves_lines_deb_14 = \
                    sum(move.debit for move in self.env['account.move.line'].search([
                        ('date', '=', '2014-1-1'),
                        ('journal_id', '=', journal['journal_id'][0]),
                        ('account_id', '=', account['account_id'][0])]))
                account_moves__lines_deb_15 = \
                    sum(move.debit for move in self.env['account.move.line'].search([
                        ('date', '=', '2015-1-1'),
                        ('journal_id', '=', journal['journal_id'][0]),
                        ('account_id', '=', account['account_id'][0])]))
                account_moves_lines_cred_14 = \
                    sum(move.credit for move in self.env['account.move.line'].search([
                        ('date', '=', '2014-1-1'),
                        ('journal_id', '=', journal['journal_id'][0]),
                        ('account_id', '=', account['account_id'][0])]))
                account_moves__lines_cred_15 = \
                    sum(move.credit for move in self.env['account.move.line'].search([
                        ('date', '=', '2015-1-1'),
                        ('journal_id', '=', journal['journal_id'][0]),
                        ('account_id', '=', account['account_id'][0])]))
                self.assertTrue(round(account_moves_lines_deb_14, 2) == round(account_moves__lines_deb_15, 2),
                                'The consolidated lines (%s) and the directly booked lines (%s) '
                                'from the same journal (%s) and account (%s) '
                                'have not the same total.' %
                                (account_moves_journal_14, account_moves_journal_15,
                                 journal['journal_id'], account['account_id']))
                self.assertTrue(round(account_moves_lines_cred_14, 2) == round(account_moves__lines_cred_15,2),
                                'The consolidated lines (%s) and the directly booked lines (%s) '
                                'from the same journal (%s) and account (%s) '
                                'have not the same total.' %
                                (account_moves_journal_14, account_moves_journal_15,
                                 journal['journal_id'], account['account_id']))
