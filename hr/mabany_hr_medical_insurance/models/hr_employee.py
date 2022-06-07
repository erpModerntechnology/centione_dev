from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    medical_line_ids = fields.One2many('hr.employee.medical.line', 'employee_id')
    life_line_ids = fields.One2many('hr.employee.life.line', 'employee_id')

    def get_medical_cost(self, payslip):
        payslip_date_from = payslip.dict.date_from
        payslip_date_to = payslip.dict.date_to
        medical_lines = self.medical_line_ids
        cost = 0
        for medical in medical_lines:
            if medical.date_from <= payslip_date_from <= medical.date_to:
                cost += medical.employee_cost
        return -1 * cost

    def get_comp_medical_cost(self, payslip):
        payslip_date_from = payslip.dict.date_from
        payslip_date_to = payslip.dict.date_to
        medical_lines = self.medical_line_ids
        cost = 0
        for medical in medical_lines:
            if medical.date_from <= payslip_date_from <= medical.date_to:
                cost += medical.company_cost
        return -1 * cost

    def get_life_cost(self, payslip):
        payslip_date_from = payslip.dict.date_from
        payslip_date_to = payslip.dict.date_to
        if self.life_line_ids:
            life_lines = self.life_line_ids[-1]
            cost = 0
            for life in life_lines:
                if life.date_from <= payslip_date_from <= life.date_to:
                    cost += life.cost
            return -1 * cost
        else:
            return 0
