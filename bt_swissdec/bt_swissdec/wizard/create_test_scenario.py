##############################################################################
#
#    Copyright (c) 2016 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################
from odoo import models, fields, api, exceptions, _
from datetime import date
from odoo.tools import ustr

SET_OF_MODELS = ['gui_tax_at_source_transmission',
                 'gui_tax_at_source_transmission_line',
                 'qst_history_recapitulation_per_month',
                 'qst_mutation_table']
class create_test_scenario(models.TransientModel):
    _module = "bt_swissdec"
    _name ='create_test_scenario'
    _description = 'Create test scenario'
    def default_year(self):
        if self.env.company and self.env.company.year_ids:
            current_year = self.env.context.get('year_name', date.today().year)
            cry = False
            for year in self.env.company.year_ids:
                if not cry:
                    cry = year
                else:
                    diff1 = int(cry.name) - int(current_year) # 2012 - 2014
                    diff2 = int(year.name) - int(current_year) # 2012 - 2014
                    if diff2 <= 0 and diff2 > diff1:
                        cry = year
                if ustr(year.name) == ustr(current_year):
                    return year
            return cry
        return False

    name = fields.Char('Name of the scenario')
    state = fields.Selection([('create_new_scenario', 'Create new scenario'),
                              ('load_scenario', 'Load scenario')],
                             string="Action",
                             required=True,
                             default='create_new_scenario')
    test_scenario_id = fields.Many2one('test_scenario',
                                       string="Scenario to load",
                                       # ondelete="cascade" # HACK: 02.06.17 15:20: jool1: do not set ondelete="cascade"
                                       )
    employee_ids = fields.Many2many(comodel_name='hr.employee', relation='employee_create_test_scenario_rel')
    year_id = fields.Many2one('res.company.year',
                              "Year",
                              default=default_year)
    company_id = fields.Many2one('res.company', related='year_id.company_id')

    def set_active_to_false(self):
        test_scenario_ids_to_remove_from_calculationparameter_qst = []
        for model in SET_OF_MODELS:
            objs = self.env[model].search([('test_case', '=', True), ('test_scenario_id.employee_ids', '=', False)])
            objs.write({'active': False})
            # get distinct test_scenario_id's
            for obj in objs:
                if obj.test_scenario_id.id not in test_scenario_ids_to_remove_from_calculationparameter_qst:
                    test_scenario_ids_to_remove_from_calculationparameter_qst.append(obj.test_scenario_id.id)
            # remove test_scenario_id for all existing hr.employee.calculationparameter.qst entries in order to be able to cancel a payslip and recalculation still works
        calculationparameter_qst_ids_to_remove_test_scenario_id = self.env[
            'hr.employee.calculationparameter.qst'].search(
            [('test_scenario_id', 'in', test_scenario_ids_to_remove_from_calculationparameter_qst)])
        calculationparameter_qst_ids_to_remove_test_scenario_id.write({'test_scenario_id': False})

    def set_active_to_false_test_employee_ids(self):
        test_scenario_ids_to_remove_from_calculationparameter_qst = []
        for model in SET_OF_MODELS:
            objs = self.env[model].search([('test_case', '=', True), ('test_scenario_id.employee_ids', '!=', False)])
            objs.write({'active': False})
            #get distinct test_scenario_id's
            for obj in objs:
                if obj.test_scenario_id.id not in test_scenario_ids_to_remove_from_calculationparameter_qst:
                    test_scenario_ids_to_remove_from_calculationparameter_qst.append(obj.test_scenario_id.id)
        #remove test_scenario_id for all existing hr.employee.calculationparameter.qst entries in order to be able to cancel a payslip and recalculation still works
        calculationparameter_qst_ids_to_remove_test_scenario_id = self.env['hr.employee.calculationparameter.qst'].search([('test_scenario_id', 'in', test_scenario_ids_to_remove_from_calculationparameter_qst)])
        if calculationparameter_qst_ids_to_remove_test_scenario_id:
            calculationparameter_qst_ids_to_remove_test_scenario_id.write({'test_scenario_id': False})

    def activate_scenario(self):
        for model in SET_OF_MODELS:
            objs = self.env[model].search([('active', '=', False), ('test_case', '=', True), ('test_scenario_id', '=', self.test_scenario_id.id)])
            objs.write({'active': True})


    def action_next(self):
        self.ensure_one()
        employee_ids = self.employee_ids.ids
        if self.state == 'load_scenario':
            employee_ids = self.test_scenario_id.employee_ids
        if not employee_ids:
            self.set_active_to_false()
        else:
            self.set_active_to_false_test_employee_ids()
        if self.state == 'create_new_scenario':
            # Here you can specify False or a list of employee IDs
            # If a list of IDs is provided, the test scenario created will only have data for those employees
            # BT - QST TEST EMPLOYEE IDS
            # employee_ids = self.employee_ids.ids
            if not employee_ids:
                test = self.env['test_scenario'].create({'name': self.name})
            else:
                test = self.env['test_scenario'].create({'name': self.name, 'employee_ids': [(4, tuple(employee_ids))]})
            # set year_id
            test.year_id = self.year_id

            # HACK: 30.06.17 10:58: jool1: should be ok, because we only use the test_scenario in hr_payslip and there we check default and employee_ids = False
            if not employee_ids:
                test.action_state_default()
            else:
                test.action_state_default_employee_ids()

            #
            # A) gui_tax_at_source_transmission
            #
            if employee_ids:
                gui_obj = self.env['gui_tax_at_source_transmission'].with_context(bt_swissdec_create_test_scenario_for_emp_ids=employee_ids)
            else:
                gui_obj = self.env['gui_tax_at_source_transmission']

            guis = gui_obj.search([('test_case', '=', False), ('year_id', '=', self.year_id.id)])
            for gui in guis:
                gui.copy({'test_scenario_id': test.id,
                          'test_case': True,
                          'state': gui.state})
            #
            # B) qst_history_recapitulation_per_month
            #
            qst_history_search = [('test_case', '=', False)]

            if employee_ids:
                q = '''
                    SELECT q.id 
                    FROM hr_employee_calculationparameter_qst q LEFT JOIN 
                         hr_employee_year y ON (q.year_id=y.id)
                    WHERE y.employee_id IN %s and company_year_id = %s'''
                self.env.cr.execute(q, (tuple(employee_ids), self.year_id.id, ))
            else:
                q = '''
                    SELECT q.id 
                    FROM hr_employee_calculationparameter_qst q LEFT JOIN 
                         hr_employee_year y ON (q.year_id=y.id)
                    WHERE company_year_id = %s'''
                self.env.cr.execute(q, (self.year_id.id,))

            qst_ids = [x[0] for x in self.env.cr.fetchall()]

            if not qst_ids:
                qst_ids = [-1]

            qst_history_search += [('hr_employee_calculationparameter_qst_id', 'in', qst_ids)]

            qst_histories = self.env['qst_history_recapitulation_per_month'].search(qst_history_search)
            for qst_history in qst_histories:
                qst_history.copy({'test_scenario_id': test.id,
                                  'test_case': True})
            #
            # C) qst_mutation_table
            #
            # HACK: 02.06.17 15:21: jool1: only get the qst_mutation_table entries where the state is not 'sent'
            qst_mutation_search = [('automatic_generated', '=', True),
                                   ('test_case', '=', False),
                                   ('state', '!=', 'sent')]

            if employee_ids:
                qst_mutation_search += [('employee_id', 'in', employee_ids)]

            qst_mutation_table_ids = self.env['qst_mutation_table'].search(qst_mutation_search)
            for qst_mutation in qst_mutation_table_ids:
                qst_mutation.copy({'test_case': True,
                                   'test_scenario_id': test.id})


        elif self.state == 'load_scenario':
            self.activate_scenario()
            if not employee_ids:
                self.test_scenario_id.action_state_default()
            else:
                self.test_scenario_id.action_state_default_employee_ids()
