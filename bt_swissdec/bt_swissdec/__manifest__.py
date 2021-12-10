##############################################################################
#
#    Copyright (c) 2016 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################
{
    "name": "brain-tec Odoo Salary",
    "version": "14.0.2111.0",  # 1: version odoo, 2: version odoo, 3: version of swissdec (year and month -> yymm), 4: internal version of swissdec
    "author": "brain-tec AG",
    "category": "Generic Modules/Human Resources",
    "website": "http://www.braintec-group.com",
    "description": """
    Module for human resource management. You can manage:\n
    * Employees and hierarchies : You can define your employee with User and display hierarchies\n
    * HR Departments\n
    * HR Jobs\n
    \n
    If you have any problems with "no module named pip.commands" execute following commands:\n
    - sudo apt-get install python-setuptools \n
    - sudo easy_install pip \n
    - sudo easy_install logilab-common \n
    \n
    In order to send error mail directly to brain-tec you need to install this package: \n
    - sudo apt install p7zip-full \n
    \n
    In order to run the viewgen after version 'viewgen-java-2017.05' we need to have java8 installed. Therefore we have a new ir.config.parameter 'swissdec_java_key_path_viewgen' which has to be set \n
    """,
    'depends': [
        'base',
        'base_setup',
        'hr',
        'hr_contract',
        'hr_holidays',
        'hr_payroll',
        'hr_payroll_account',
        'hr_work_entry_contract',
        'bt_swissdec_pre',
        'account_accountant',
        'l10n_ch',
        'web',
        'bt_ch_state',
        'bt_ch_city',
        'bt_account_sepa',
        'bt_tutorial',
    ],
    'css': ['static/src/css/message_align_left.css'],
    'data': [
        'data/res_groups.xml',
        'data/report_paperformat.xml',
        'view/hr_paroll_report.xml',
        'view/pre_menu.xml',
        'security/hr/ir.model.access.csv',
        'security/hr_contract/ir.model.access.csv',
        'security/hr_payroll/ir.model.access.csv',
        'security/hr_payroll_account/ir.model.access.csv',
        'security/ir.model.access.csv',
        'wizard/create_test_scenario_view.xml',
        'wizard/companyyear_copy_wizard.xml',
        'view/test_scenario_view.xml',
        'view/bvg_import_data.xml',
        'view/message_align_left.xml',
        'view/transmitter_view.xml',
        'data/hr_employee_sequence.xml',
        'data/company_years_data.xml',
        'data/qst_month.xml',
        'data/hr_data.xml',
        'data/bfs_data.xml',
        'data/hr_contract_data.xml',
        'data/hr_payroll_data.xml',
        'data/hr_bvg_data.xml',
        'data/cron_jobs.xml',
        'data/email_template_send_to_braintec.xml',
        'data/email_template_send_qst_warnings_to_customer.xml',
        'data/qst_canton_defaults.xml',
        'wizard/create_year_employee_view.xml',
        'wizard/change_address_wizard_view.xml',
        'wizard/employee_configuration_progress_wizard_view.xml',
        'view/bt_swissdec_report_line_view.xml',
        'view/downloadable_binary_view.xml',
        # hr
        'view/hr_view.xml',
        'view/res_company_ext_view.xml',
        'view/qst_history_recapitulation_view.xml',
        'view/hr_employee_calculationparameter_bvg_view.xml',

        'view/hr_employee_calculationparameter_qst_view.xml',
        'view/gui_tax_at_source_transmission_line_current_view.xml',
        'view/gui_tax_at_source_transmission_line_recapitulation_view.xml',
        'view/gui_tax_at_source_transmission_line_children_view.xml',
        'view/gui_tax_at_source_additional_particulars_view.xml',
        'view/gui_tax_at_source_transmission_line_history.xml',
        'view/hr_employee_ext_view.xml',
        'view/hr_employee_public_ext_view.xml',
        'view/hr_employee_year_view.xml',
        'view/hr_employee_marital_status_view.xml',
        'view/res_company_ktg_code_view.xml',
        'view/res_company_uvgz_code_view.xml',
        'view/res_company_bvg_code_view.xml',
        'view/res_company_bvg_view.xml',
        'view/res_company_uvgz_view.xml',
        'view/res_company_ktg_view.xml',
        'view/res_company_swissdec_vers_view.xml',
        'view/res_company_bur_view.xml',
        'view/qst_mutation_table_view.xml',
        'view/hr_employee_family_status_view.xml',
        'view/log_corrections_view.xml',
        'view/res_company_year_view.xml',
        'view/gui_tax_at_source_transmission_line_view.xml',
        'view/qst_correction_difference_type_view.xml',
        'view/qst_correction_declaration_category_type_view.xml',

        'view/hr_qst_view.xml',
        # hr_conract
        'view/hr_contract_view.xml',
        'view/qst_correction_view.xml',
        # hr_payroll
        'view/hr_payroll_view.xml',
        'view/account_move_ext.xml',
        'wizard/hr_year_close_state.xml',
        'view/hr_bvg_basis_line_detail_view.xml',
        'view/hr_bvg_basis_line_view.xml',
        'view/hr_bvg_basis_view.xml',

        # Transmitter
        'view/transmitter_message_view.xml',
        'view/transmitter_messages_notification_view.xml',
        'view/hr_employee_calculationparamter_view.xml',
        'view/bt_swissdec_report_view.xml',
        'view/res_partner_ext_view.xml',
        'wizard/cancel_paid_payslips.xml',
        'wizard/hr_adc_modification_view.xml',
        'wizard/hr_adc_duplicate_view.xml',
        'wizard/hr_adc_linkaccount_view.xml',
        'wizard/hr_link_payslip_to_register.xml',
        # hr_swissdec
        'view/hr_adc_history_overview_view.xml',
        'wizard/hr_monthly_reports_view.xml',
        'wizard/import_qst_tarif9.xml',
        'view/transmitter_configuration.xml',
        'view/hr_swissdec_installer.xml',
        'wizard/company_set_bt_swissdec_flag_views.xml',
        'security/ir_rule.xml',
        'security/ir_rule_multicompany.xml',

        'view/res_country_state_view.xml',
        'view/ahv_mutation_table_view.xml',
        'view/transmitter_execution_view.xml',
        'view/transmitter_institution_view.xml',
        'view/transmitter_get_status_view.xml',
        'view/gui_ahv_mutations_view.xml',
        'wizard/single_gui_ahv_mutation.xml',
        'wizard/single_gui_ahv_mutation.xml',
        'view/gui_salary_declaration_view.xml',
        'view/gui_bvg_sc_view.xml',
        'view/gui_bvg_ds_view.xml',
        'view/gui_tax_at_source_transmission_view.xml',
        'view/account_move_line_salary_view.xml',
        'wizard/account_move_salary_transfer_wizard.xml',

        'view/menu.xml',
        'view/yes_no_popup.xml',
        'data/hr_payslip_recalculation.xml',
        'data/hr_payroll_register_recalculation.xml',
        'data/hr_employee_year_after_migration.xml',
        'data/hr_payslip_line_after_migration.xml',
        'view/report_payslip_templates.xml',
        'view/report_payslip_account_move_lines_templates.xml',
        'view/report_payslip_voucher_templates.xml',
        'view/report_register_statement_templates.xml',
        #HR Reports
        'view/report_hr_wagetypesrecap_templates.xml',
        'view/report_hr_matrix_templates.xml',
        'view/report_hr_yearlyrecap_templates.xml',
        'view/report_hr_recap_employees_per_wagetypes.xml',
        'view/report_hr_yearlyrecap_qst_templates.xml',
        'view/report_hr_company_templates.xml',
        'view/report_hr_employee_templates.xml',
        'view/report_bvg_declaration_templates.xml',
        'data/data_tutorial.xml',
        'view/webclient_templates.xml',
    ],
    'demo': [
        'demo/company_years_data_for_tests.xml',
        'demo/company.xml',
        'demo/company_qst.xml',
        'demo/company_qst5.xml',
        'demo/hr_payroll_data_qst.xml',
        'demo/hr_payroll_data_qst5.xml',
        'demo/res_users.xml',
        'demo/res_users_qst.xml',
        'demo/res_users_qst5.xml',
        'demo/res_company_group.xml',
        'demo/hr_contract.xml',
        'demo/hr_contract_qst.xml',
        'demo/hr_entry_withdrawal_ids_data_qst.xml',
        'demo/hr_employee_year.xml',
        'demo/qst_tarif_data.xml',
        'demo/qst_tarif_data5.xml',
        'demo/hr_employee_year_qst.xml',
        'demo/test_qst5_01.xml',
        'demo/test_qst5_01_1.xml',
        'demo/test_qst5_01_2.xml',
        'demo/test_qst5_01_3.xml',
        'demo/test_qst5_01_4.xml',
        'demo/test_qst5_02.xml',
        'demo/test_qst5_03.xml',
        'demo/test_qst5_04.xml',
        'demo/test_qst5_05.xml',
        'demo/test_qst5_06.xml',
        'demo/test_qst5_07.xml',
        'demo/test_qst5_07_1.xml',
        'demo/test_qst5_08.xml',
        'demo/test_qst5_09.xml',
        'demo/test_qst5_10.xml',
        'demo/test_qst5_11_1.xml',
        'demo/test_qst5_11_2.xml',
        'demo/test_qst5_14.xml',
        'demo/test_qst5_15.xml',
        # 'demo/test_qst5_16.xml',  # TODO: 23.09.20 12:52: jool1: nicht sicher ob wir diesen test durchführen
        'demo/test_qst5_17.xml',
        'demo/test_qst5_18.xml',
        'demo/test_qst5_19.xml',
        'demo/test_qst5_19_1.xml',
        'demo/test_qst5_20.xml',
        'demo/test_qst5_21.xml',
        'demo/test_qst5_22.xml',
        'demo/test_qst5_23.xml',
        'demo/test_qst5_24.xml',
        'demo/test_qst5_25.xml',
        'demo/test_qst5_26.xml',
        'demo/test_qst5_27.xml',
        'demo/test_qst5_27_1.xml',
        'demo/test_qst5_28.xml',
        'demo/test_qst5_29.xml',
        'demo/test_qst5_30_1.xml',
        'demo/test_qst5_30_2.xml',
        'demo/test_qst5_31.xml',
        'demo/test_qst5_32.xml',
        'demo/test_qst5_33.xml',
        'demo/test_qst5_33_1.xml',
        'demo/test_qst5_34.xml',
        'demo/test_qst5_35.xml',
        'demo/test_qst5_36.xml',
        'demo/test_qst5_37.xml',
        'demo/test_qst5_38.xml',
        'demo/test_qst5_38_1.xml',
        'demo/test_qst5_39.xml',
        'demo/test_qst5_40.xml',
        'demo/test_qst5_40_1.xml',
        # 'demo/test_qst5_41.xml',  # TODO: 14.10.20 13:08: jool1: momentan nicht möglich diesen test durchzuführen -> siehe todo "test 41" leider können wir keine korrektur für das vorjahr vornehmen. müssen wir dies doch noch implementieren?
        'demo/test_qst5_42.xml',
        'demo/test_qst5_43.xml',
        # 'demo/test_qst5_45.xml',  # TODO: 14.10.20 13:08: jool1: momentan nicht möglich diesen test durchzuführen -> wir können nicht im selben monat ein aus- und eintritt haben, da nur ein vertrag möglich...
        'demo/test_qst5_46.xml',
        'demo/test_qst5_47.xml',
        'demo/transmitter_configuration.xml',
        'demo/transmitter_configuration_qst.xml',
        'demo/transmitter_configuration_qst5.xml',
        'demo/updates_after_installation_for_swissdec_tests.sql',
        'demo/qst_tarif_data5_a0n.sql',
        'demo/qst_tarif_data5_b0n.sql',
        'demo/qst_tarif_data5_b1n.sql',
        'demo/qst_tarif_data5_c0n.sql',
        'demo/qst_tarif_data5_c1n.sql',
        'demo/qst_tarif_data5_h1n.sql',
        'demo/hr_adc_company_linking.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'license': 'OPL-1',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: