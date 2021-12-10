##############################################################################
# Copyright (c) 2019 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################
{
    'name': 'BT-Tutorial',
    'version': '14.0.1.0.0',
    'category': 'Tools',
    'summary': "This module allows to create links to video's or url's and embeds them into odoo",
    'author': "brain-tec AG",
    'website': 'https://braintec-group.com',
    'license': 'OPL-1',
    'depends': [],
    'data': [
        'views/tutorial_link.xml',
        'wizard/open_url_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
