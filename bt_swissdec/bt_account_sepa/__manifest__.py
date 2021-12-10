##############################################################################
# Copyright (c) 2020 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

{
    "name": "BT CH Localization - Account Sepa Extension",
    "version": "14.0.1.0.0",
    "author": "brain-tec AG",
    "license": "OPL-1",
    "summary": "Extends account_sepa by the Swiss localization",
    "category": "Localization",
    "website": "http://www.braintec-group.com",
    "depends": [
        "account",
        "account_sepa",
    ],
    "data": [
        "view/account_journal.xml",
        "view/account_batch_payment_views.xml",
    ],
    "installable": True,
}
