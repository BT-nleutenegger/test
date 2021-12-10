##############################################################################
#
#    Copyright (c) 2016 brain-tec AG (http://www.braintec-group.com)
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################
{
    "name": "brain-tec Odoo Salary (PRE)",
    "version": "14.0.2103.0",  # 1: version odoo, 2: version odoo, 3: version of swissdec (year and month -> yymm), 4: internal version of swissdec
    "author": "brain-tec AG",
    "category": "Generic Modules/Human Resources",
    "website": "http://www.braintec-group.com",
    "description": """
    Make the compatibility with previous installed modules.
    Module for human resource management. You can manage:\n
    * Employees and hierarchies : You can define your employee with User and display hierarchies\n
    * HR Departments\n
    * HR Jobs\n
    \n
    If you have any problems with "no module named pip.commands" execute following commands:\n
    - sudo apt-get install python-setuptools \n
    - sudo easy_install pip \n
    - sudo easy_install logilab-common \n
    """,
    'depends': [
        'base',
        'base_setup',
        'hr',
        'hr_contract',
        'hr_holidays',
        'hr_payroll',
        'hr_payroll_account',
        'account_accountant',
        'l10n_ch',
        'web',
        'bt_ch_state',
        'bt_ch_city',
    ],
    'css': ['static/src/css/message_align_left.css'],
    'data': [
        'data/transmitter_configuration.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'license': 'OPL-1',
    'pre_init_hook': 'pre_init_hook',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
