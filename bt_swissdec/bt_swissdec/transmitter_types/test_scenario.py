##############################################################################
#
#    Copyright (c) 2016 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################
import time
from datetime import date
from datetime import timedelta, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import models, fields, api, exceptions, _
from odoo.addons.bt_swissdec.bt_tools.general_tools import pattern_date
from odoo.addons.bt_swissdec.hr import mutation_generic


class test_scenario(models.Model):
    _module = "bt_swissdec"
    _inherit = ['mail.thread']
    _name = 'test_scenario'
    _description = 'Test Scenario'

    name = fields.Char('Name', required=True)
    gui_tax_at_source_transmission_ids = fields.One2many('gui_tax_at_source_transmission',
                                                         'test_scenario_id',
                                                         string="Gui tax at source transmission")

    state = fields.Selection([('no_default', 'No Default'),
                                      ('default', 'Default')
                                      ],
                                     string="Internal State",
                                     required=True,
                                     default="no_default")

    employee_ids = fields.Many2many(comodel_name='hr.employee', relation='employee_test_scenario_rel')
    year_id = fields.Many2one('res.company.year', "Year")

    # @api.one
    def action_state_default(self):
        self.ensure_one()
        var_all = self.search([('employee_ids', '=', False)])
        for configuration in var_all:
            configuration.state = 'no_default'
        self.state = 'default'

    # @api.one
    def action_state_default_employee_ids(self):
        self.ensure_one()
        var_all = self.search([('employee_ids', '!=', False)])
        for configuration in var_all:
            configuration.state = 'no_default'
        self.state = 'default'