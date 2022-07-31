# -*- coding: utf-8 -*-

from datetime import datetime,date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = "hr.employee"


    @api.model
    def create(self,vals):
        res = super(HrEmployee, self).create(vals)
        emps_values = []
        emps = self.env['hr.employee'].search([]).mapped('zk_emp_id')
        for i in emps:
            if i != False:
                if i.isdigit():
                    emps_values.append(int(i))
                else:
                    emps_values.append(0)
            else:
                emps_values.append(0)
        # emps_values = [int(i) for i in emps]
        maxed_emps = max(emps_values)
        maxed = maxed_emps + 1
        res.zk_emp_id = str(maxed)
        return res
