##############################################################################
# Copyright (c) 2020 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

from .common import TestBTSwissdec
from odoo import fields


class TestCompanySetBTSwissdecFlag(TestBTSwissdec):

    def setUp(self):
        super(TestCompanySetBTSwissdecFlag, self).setUp()

        # Create a second company
        self.second_company = self.env['res.company'].create({
            'name': 'New BT Swissdec Company',
            'chart_template_id': self.ref('l10n_ch.l10nch_chart_template'),
        })

        # Values taken from bt_swissdec/data/company_years_data.xml
        self.year_template = self.env['res.company.year.template'].create({
            'name': str(fields.Datetime.today().year),
            'ahv_freigrenze_monat': 1400,
            'ahv_alv_untergrenze_jahr': 2300,
            'beginn_ahv': 18,
            'beginn_rentenalter_m': 65,
            'beginn_rentenalter_f': 64,
            'ahv_arbeitnehmer_beitrag': 5.275,
            'alv_hoechstlohn_monat': 12350,
            'alv_arbeitnehmer_beitrag': 1.10,
            'alvz_hoechstlohn_monat': 999999999,
            'alvz_arbeitnehmer_beitrag': 0.50,
        })

    def test_set_bt_swissdec_flag_company(self):
        self.assertFalse(
            self.second_company.company_used_for_bt_swissdec,
            'The company created has already the flag "This company is used for bt_swissdec" set!',
        )

        wizard = self.env['bt_swissdec.company_set_bt_swissdec_flag.wizard'].create({
            'company_id': self.second_company.id,
            'salary_contact_name': 'Second company contact',
            'salary_contact_email': 'second_company_contact@second_company.com',
            'salary_contact_phone': '123456789',
            'yearlyholidays_company': 21.5,
            'year': self.year_template.name,
            'chart_template_id': self.ref('l10n_ch.l10nch_chart_template'),
        })

        wizard.set_bt_swissdec_flag()

        self.assertTrue(
            self.second_company.company_used_for_bt_swissdec,
            'The company created should have the flag "This company is used for bt_swissdec" already set!',
        )

        self.assertTrue(
            self.second_company.country_id.code == 'CH',
            'The country of the company created should be Switzerland!'
        )

        self.assertTrue(
            len(self.second_company.year_ids) == 1,
            'The company created should have a year already set!'
        )

        main_company = self.env.ref("base.main_company")

        for f_tuple in [
            ('category_bvg_id', 'Lohnart BVG-Beitrag'),
            ('category_ahv_id', 'Lohnart AHV-Beitrag'),
            ('category_alv_id', 'Lohnart ALV-Beitrag'),
            ('category_alvz_id', 'Lohnart ALVZ-Beitrag'),
            ('category_qst_id', 'Lohnart QST-Beitrag'),
            ('category_qst_correction_id', 'Lohnart QST-Korrektur'),
            ('category_uvg_nbuv_id', 'Lohnart UVG-Beitrag (NBUV)'),
            ('category_nettolohnausgleich_id', 'Lohnart Nettolohnausgleich'),
            ('category_kizu_id', 'Lohnart Kinderzulage'),
            ('category_ausbzu_id', 'Lohnart Ausbildungszulage'),
            ('category_famzu_id', 'Lohnart Familienzulage'),
            ('category_hauszu_id', 'Lohnart Haushaltszulage'),
            ('category_gebzu_id', 'Lohnart Geburtszulage'),
            ('category_heiratzu_id', 'Lohnart Heiratszulage'),
            ('category_betreuungzu_id', 'Lohnart Betreuungszulage'),
        ]:
            self.assertTrue(
                self.second_company[f_tuple[0]],
                'The company created should have a "%s" already set!' % f_tuple[1]
            )
            self.assertEqual(self.second_company[f_tuple[0]].matrix_nr, main_company[f_tuple[0]].matrix_nr)

        # Testing Editable Allowance Deduction Caregories
        main_company_adcs_numbers = main_company.adc_ids.mapped('matrix_nr')
        self.assertTrue(
            len(self.second_company.adc_ids) == len(main_company_adcs_numbers),
            'The company created should have %s "Allowance deduction categories" '
            '(as the main company)!' % len(main_company_adcs_numbers)
        )

        for adc in self.second_company.adc_ids:
            self.assertTrue(
                adc.matrix_nr in main_company_adcs_numbers,
                'There should be one "Allowance deduction category" '
                'with Nr. %s for the main company!' % adc.matrix_nr
            )

        # Testing Allowance Deduction Categories must be linked to children
        main_company_adcs_numbers = main_company.adc_child_link_ids.mapped('matrix_nr')
        self.assertTrue(
            len(self.second_company.adc_child_link_ids) == len(main_company_adcs_numbers),
            'The company created should have %s "Allowance Deduction Categories must be linked to children" '
            '(as the main company)!' % len(main_company_adcs_numbers)
        )

        for adc in self.second_company.adc_child_link_ids:
            self.assertTrue(
                adc.matrix_nr in main_company_adcs_numbers,
                'There should be one "Allowance Deduction Categories must be linked to children" '
                'with Nr. %s for the main company!' % adc.matrix_nr
            )
