#!/bin/bash
rm ~/Downloads/*.xml
dropdb odoo8_january_ready
createdb odoo8_january_ready -T odoo8_january_ready$1
