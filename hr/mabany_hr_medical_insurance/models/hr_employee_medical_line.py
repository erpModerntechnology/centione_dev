from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEmployeeMedicalLine(models.Model):
    _name = 'hr.employee.medical.line'

    employee_id = fields.Many2one('hr.employee')
    medical_id = fields.Many2one('hr.medical.insurance', domain=[('state', '=', 'open')])
    medical_grade_id = fields.Many2one('hr.medical.insurance.lines', domain=[('medical_id', '=', False)])
    date_from = fields.Date(related='medical_id.date_from')
    date_to = fields.Date(related='medical_id.date_to')
    follower_ids = fields.Many2many('hr.employee.follower', domain="[('employee_id', '=', employee_id)]")
    employee_cost = fields.Float(compute='_compute_emp_cost')
    company_cost = fields.Float(compute='_compute_comp_cost')

    @api.onchange('medical_id')
    def _onchange_medical_id(self):
        domain = {'medical_grade_id': [('medical_id', '=', -1)]}
        if self.medical_id:
            domain = {'medical_grade_id': [('id', 'in', [line.id for line in self.medical_id.line_ids])]}
            self.medical_grade_id = False
        return {'domain': domain}

    @api.constrains('follower_ids')
    def _update_number_subscribers(self):
        self.medical_id._compute_number_of_subscribers()

    @api.depends('medical_grade_id', 'follower_ids')
    def _compute_emp_cost(self):
        for rec in self:
            spouse_lis = []
            child_lis = []
            employee_cost = rec.medical_grade_id.total_employee_share
            number = 0
            for fam in rec.medical_grade_id:
                for m in fam.medical_id.family_grade_ids:
                    if m.grade_id.name == rec.medical_grade_id.name:
                        spouse_lis.append(m.spouse)
                        child_lis.append(m.child)
            print('aaaaaaaaaa',rec.follower_ids)
            for m in rec.follower_ids:
                if m.name in ['spouse','Spouse']:
                    number +=   spouse_lis[0] if spouse_lis else 0
                if m.name in ['child','Child']:
                    number +=  child_lis[0] if child_lis else 0
            if rec.follower_ids:
                rec.employee_cost = number + employee_cost
            else:
                rec.employee_cost = employee_cost
    @api.depends('medical_grade_id', 'follower_ids')
    def _compute_comp_cost(self):
        # employee_cost = self.medical_grade_id.total_employee_share
        company_share = self.medical_grade_id.get_company_share()
        self.company_cost = company_share
