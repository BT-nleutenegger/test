##############################################################################
# Copyright (c) 2020 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

{
    "name": "BT CH Localization - All cities",
    "version": "14.0.1.0.0",
    "author": "brain-tec AG",
    "license": "OPL-1",
    "summary": "Provides all swiss cities for auto-completion",
    "category": "Localization",
    "website": "http://www.braintec-group.com",
    "depends": [
        "base_address_city",
        "contacts",
        "bt_ch_state",
    ],
    "data": [
        "data/res.city.csv"
    ],
    "installable": True,
}
