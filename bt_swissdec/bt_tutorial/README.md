# Braintec Tutorial Link

This module allows to create links to video's or url's and embeds them into odoo.

### Configuration
  
There will be a new menu "Tutorials" where video's or url's can be added. To add it to the form view (eg. as SmartButton) of the linked model you can add this part to the form view and define the related model in the context (eg. 'hr.employee'): 

    <div class="oe_button_box" name="button_box">
        <button name="%(bt_tutorial.action_tutorial_link_to_use_in_other_modules)d" class="oe_stat_button"
                icon="fa-youtube" string="Tutorials" type="action" context="{'model_name': 'hr.employee'}"/>
    </div>
