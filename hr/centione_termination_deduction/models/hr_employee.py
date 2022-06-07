# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def get_terminated_wage(self, payslip, categories):
        for rec in self.slip_ids.struct_id.rule_ids:
            if rec.terminated == True:
                emp = self.env['hr.contract'].search(
                    [('employee_id', '=', self.id), ('date_start', '>=', payslip.date_from),
                     ('date_end', '<=', payslip.date_to), ('state', '=', 'cancel')])
                if emp:
                    wage_per_day = emp.wage / 30 / 8
                    wage_per_date = abs(emp.date_end - payslip.date_to)
                    total_wage = wage_per_day * wage_per_date.days
                    deduct_wage = categories.BASIC - total_wage
                return deduct_wage
