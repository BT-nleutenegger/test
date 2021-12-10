##############################################################################
#
#    Copyright (c) 2016 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################

from . import arg_spec_patch
from . import transmitter_types

from odoo import api, SUPERUSER_ID
from logging import getLogger
_logger = getLogger(__name__)


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    if not env['res.lang'].search([('code', '=', 'de_CH'), ('active', '=', True)], count=True, limit=1):
        env["base.language.install"].create({'lang': 'de_CH', 'overwrite': True}).lang_install()


def post_init(cr, registry):
    _logger.info('bt_swissdec_pre -> post_init(%s, %s)' % (cr, registry))

    # create ir_config_parameter "bt_swissdec_do_migration_updates"
    cr.execute("INSERT INTO ir_config_parameter (key, value) VALUES ('bt_swissdec_do_migration_updates', '1');")

    cr.execute("""update transmitter_configuration set state_default = 'default' where name = '[brain-tec] PRODUCTIVE-T';""")
    cr.execute("""update hr_monthly_reports set year = (select id from res_company_year where name = '2013') where year= '2013';""")
    cr.execute("""update hr_monthly_reports set year = (select id from res_company_year where name = '2012') where year= '2012';""")
    cr.execute("""delete from hr_link_payslip_to_register;""")
    cr.execute("""delete from hr_link_payslip_to_register_line;""")

    cr.execute("""INSERT INTO "public"."ir_model_data" ("create_uid", "create_date", "write_date", "write_uid", "noupdate", "date_init", "date_update", "module", "model", "res_id", "name") VALUES ('1', '2012-10-30 10:23:42.263277', NULL, NULL, 't', '2012-10-30 10:23:42', '2012-10-30 10:23:42', 'bt_swissdec', 'res.country', '255', 'ss');""")

    cr.execute("""delete from ir_ui_view where name like 'hr.payroll.advice.form.bt';""")
    cr.execute("""delete from ir_ui_view where name like 'hr.payroll.register.inherit.tree';""")
    cr.execute("""delete from ir_ui_view where name like 'hr.payroll.register.form.bt';""")
    cr.execute("""delete from ir_ui_view where name like 'hr.payroll.register.inherit.form';""")

    cr.execute("""delete from ir_ui_view where name like '"sett_view_holiday_simple_ext"';""")

    # after this query bt_swissdec must be directly updated!!!!!
    cr.execute("""delete from ir_model_data where model = 'ir.ui.menu' and "module" = 'bt_swissdec';""")

    # create category_adc_id column for all the objects where this column was changed from category_id to category_adc_id
    cr.execute("""ALTER TABLE hr_payslip_line ADD COLUMN "category_adc_id" int4;""")
    cr.execute("""ALTER TABLE hr_allowance_deduction_other_category ADD COLUMN "category_adc_id" int4;""")
    cr.execute("""ALTER TABLE company_contribution ADD COLUMN "category_adc_id" int4;""")
    cr.execute("""ALTER TABLE hr_payslip_line_employer ADD COLUMN "category_adc_id" int4;""")
    cr.execute("""ALTER TABLE hr_payslip_grosswage_line ADD COLUMN "category_adc_id" int4;""")
    cr.execute("""ALTER TABLE hr_payslip_calculation_line ADD COLUMN "category_adc_id" int4;""")

    # update hr_payslip_line - set correct category_adc_id from category_id_bak
    cr.execute("""update hr_payslip_line set category_adc_id = category_id_bak;""")
    # update other tables - set correct category_adc_id from category_id
    cr.execute("""update hr_allowance_deduction_other_category set category_adc_id = category_id;""")
    cr.execute("""update company_contribution set category_adc_id = category_id;""")
    cr.execute("""update hr_payslip_line_employer set category_adc_id = category_id;""")
    cr.execute("""update hr_payslip_grosswage_line set category_adc_id = category_id;""")
    cr.execute("""update hr_payslip_calculation_line set category_adc_id = category_id;""")

    # some updates
    cr.execute("""ALTER TABLE res_country ADD COLUMN "swiss_payroll_is_switzerland" bool;""")
    cr.execute("""update res_country set swiss_payroll_is_switzerland = True where code = 'CH';""")
    cr.execute("""update hr_payslip_line set active = True;""")
    cr.execute(
        """delete from ir_ui_menu where parent_id in (406);""")
    cr.execute("""delete from ir_ui_menu where id in (405,409,406,401,400,419,415,410,411,418,413,412,402,408,1785,1786,1788,1849,1848,1879,1877,1878,1876,1933,1952,1951,1950,2121,2280,2286);""")
    cr.execute("""delete from ir_ui_menu where id in (select res_id from ir_model_data where model = 'ir.ui.menu' and module = 'bt_swissdec');""")
    cr.execute("""delete from ir_ui_menu where parent_id in (407,417);""")
    cr.execute("""delete from ir_ui_menu where id in (407,417);""")
    cr.execute("""delete from ir_model_data where model = 'ir.ui.menu' and module = 'bt_swissdec';""")

    # updates bfs data
    cr.execute("""update ir_model_data set noupdate = False where model = 'res.company.bfs.residence.category';""")
    cr.execute("""update ir_model_data set noupdate = False where model = 'res.company.bfs.education';""")
    cr.execute("""update ir_model_data set noupdate = False where model = 'res.company.bfs.position';""")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
