# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api


class HREmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    over_fifty = fields.Boolean(string='Over 50')
    years_insurance_ten = fields.Boolean(string='10 Years Insurance')

    def send_allocation(self):
        leave_annual = self.env['hr.leave.type'].search([('holiday_type', '=', 'annual')], limit=1)
        leave_casual = self.env['hr.leave.type'].search([('holiday_type', '=', 'casual')], limit=1)
        leave_annual_sum=(12 / 6) * (12 - self.hire_date.month)
        leave_casual_sum=(12 / 24) * (12 - self.hire_date.month)
        if self.over_fifty or self.over_fifty:
            self.env['hr.leave.allocation'].create({
                'employee_id': self.id,
                'holiday_status_id': leave_annual.id,
                'number_of_days': leave_annual_sum,
                'date_from': date.today(),
                'state': 'validate',
            })
            self.env['hr.leave.allocation'].create({
                'employee_id': self.id,
                'holiday_status_id': leave_casual.id,
                'number_of_days': leave_casual_sum,
                'date_from': date.today(),
                'state': 'validate',
            })
        else:
            self.env['hr.leave.allocation'].create({
                'employee_id': self.id,
                'holiday_status_id': leave_annual.id,
                'number_of_days': leave_annual_sum,
                'date_from': date.today(),
                'state': 'validate',
            })
            self.env['hr.leave.allocation'].create({
                'employee_id': self.id,
                'holiday_status_id': leave_casual.id,
                'number_of_days': leave_casual_sum,
                'date_from': date.today(),
                'state': 'validate',
            })
