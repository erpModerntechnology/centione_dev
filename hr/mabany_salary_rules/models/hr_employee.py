# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    def get_unpaid_day(self, payslip, contract):
        total_deduct = []
        emp = self.env['hr.leave'].search(
            [('employee_ids', '=', self.id), ('request_date_from', '>=', payslip.date_from),
             ('request_date_from', '<=', payslip.date_to)])
        for rec in emp:
            if rec.holiday_status_id.holiday_type == 'unpaid':
                total_wage_per_day = contract.wage / 30
                total_deduct.append(total_wage_per_day)
        total_wage_deduct = sum(total_deduct)
        return total_wage_deduct

    def sick_leave_deduct(self):
        total_dur = []
        sick = self.env['hr.leave'].search([('employee_ids', '=', self.id)])
        if sick:
            for rec in sick:
                if rec.holiday_status_id.holiday_type == 'sick':
                    date = abs(rec.request_date_from - rec.request_date_to)
                    diff = date.days
                    print(date)
                    total_dur.append(diff)
            if 90 > sum(total_dur):
                if sum(total_dur) < 30:
                    return 0
                if sum(total_dur) == 30:
                    return 0
                if sum(total_dur) > 30:
                    total_deduct = self.contract_id.wage * 0.25
                    return total_deduct
            if sum(total_dur) >= 90:
                total_deduct = self.contract_id.wage * 0.15
                return total_deduct

    def get_sick_leave(self, payslip):
        emp = self.env['hr.leave'].search(
            [('employee_ids', '=', self.id), ('request_date_from', '>=', payslip.date_from),
             ('request_date_from', '<=', payslip.date_to)])
        if emp:
            total_deduct_sick = self.sick_leave_deduct()
            return total_deduct_sick
        else:
            return 0
