update hr_adc_history set valid_from = '2012-01-01';
update hr_adc_history set new_value = '5700' where name = 'Initial value for field matrix_buchhaltung for category UVGZ-Beitrag M1';
update hr_adc_history set new_value = '5700' where name = 'Initial value for field matrix_buchhaltung for category UVGZ-Beitrag M2';
update hr_adc_history set new_value = '5700' where name = 'Initial value for field matrix_buchhaltung for category KTG-Beitrag M1';
update hr_adc_history set new_value = '5700' where name = 'Initial value for field matrix_buchhaltung for category KTG-Beitrag M2';
update hr_adc_history set new_value = '5000' where name like 'Initial value for field matrix_buchhaltung for category %' and new_value in ('5040','2999','5004','5035','5030','5032','5721','5722','5034','5320');
update hr_adc_history set new_value = '5700' where new_value like '57%' and name like '%matrix_buchhaltung%';
update hr_adc_history set new_value = '5000' where new_value like '50%' and name like '%matrix_buchhaltung%';
update hr_adc_history set new_value = '5800' where new_value in ('5830','5831','5832','5820','5601') and name like '%matrix_buchhaltung%';
update hr_adc_history set new_value = '2500' where new_value in ('2990','2999') and name like '%matrix_buchhaltung%';
update hr_allounce_deduction_categoty set base_changed_ok = True where name like 'UVGZ-Beitrag M%';
update res_users set odoobot_state = 'disabled';
update ir_property set value_reference = (select 'account.account,' || id from account_account where company_id = (select id from res_company where name = 'MUSTER AG') and code = '1021') where name like 'property_bank_account%' and company_id = (select id from res_company where name = 'MUSTER AG');
update ir_property set value_reference = (select 'account.account,' || id from account_account where company_id = (select id from res_company where name = 'MUSTER AG') and code = '5800') where name like 'employee_account%' and company_id = (select id from res_company where name = 'MUSTER AG');
update ir_property set value_reference = (select 'account.account,' || id from account_account where company_id = (select id from res_company where name = 'PROCESS AG') and code = '1021') where name like 'property_bank_account%' and company_id = (select id from res_company where name = 'PROCESS AG');
update ir_property set value_reference = (select 'account.account,' || id from account_account where company_id = (select id from res_company where name = 'PROCESS AG') and code = '5800') where name like 'employee_account%' and company_id = (select id from res_company where name = 'PROCESS AG');
update ir_property set value_reference = (select 'account.account,' || id from account_account where company_id = (select id from res_company where name = 'PROCESS_5 AG') and code = '1021') where name like 'property_bank_account%' and company_id = (select id from res_company where name = 'PROCESS_5 AG');
update ir_property set value_reference = (select 'account.account,' || id from account_account where company_id = (select id from res_company where name = 'PROCESS_5 AG') and code = '5800') where name like 'employee_account%' and company_id = (select id from res_company where name = 'PROCESS_5 AG');
-- update hr_payslip_grosswage_line set account_id = (select CAST(nullif(new_value, '') AS integer) from hr_adc_history where field_id = (select id from ir_model_fields where name = 'matrix_buchhaltung_account' and model = 'hr.allounce.deduction.categoty') and adc_id = hr_payslip_grosswage_line.category_adc_id);
update hr_allounce_deduction_categoty set uom_id = null;
update hr_allounce_deduction_categoty set uom_id = (select id from uom_uom where name = 'Hours') where matrix_nr = '1000';
update res_company set default_journal_id = (select id from account_journal where code = 'PA' and company_id = 1) where id = 1;
update res_company set default_payment_journal_id = (select id from account_journal where name = 'Bank' and company_id = 1) where id = 1;
update res_company set default_journal_id = (select id from account_journal where code = 'PA' and company_id = 2) where id = 2;
update res_company set default_payment_journal_id = (select id from account_journal where name = 'Bank' and company_id = 2) where id = 2;
update hr_employee_calculationparameter_qst set marital_qst_partner_data_required_related = True where marital_code in (select id from hr_employee_marital_status where qst_partner_data_required = True) and residence_category not in (select id from res_company_bfs_residence_category where code in ('settled-C','Swiss'));
update ir_ui_view set arch_db = replace(arch_db, '5060', '5061') where arch_db like '%5060%';
update res_company_year set qst_tarif_import_done = True;
INSERT INTO ir_config_parameter(value, key) VALUES ('java -Xms128m -Xmx512m -XX:CompressedClassSpaceSize=10m', 'swissdec_java_key_path_viewgen') ON CONFLICT DO NOTHING;
INSERT INTO ir_config_parameter(value, key) VALUES ('java -Xms128m -Xmx512m -XX:CompressedClassSpaceSize=10m', 'swissdec_java_key_path') ON CONFLICT DO NOTHING;