from odoo import models, fields, api, _


class HrEmployeeLifeLine(models.Model):
    _name = 'hr.employee.life.line'

    employee_id = fields.Many2one('hr.employee')
    life_id = fields.Many2one('hr.life.insurance', domain=[('state', '=', 'open')])
    life_grade_id = fields.Many2one('hr.life.insurance.lines', domain=[('life_id', '=', False)])
    date_from = fields.Date(related='life_id.date_from')
    date_to = fields.Date(related='life_id.date_to')
    follower_ids = fields.Many2many('hr.employee.follower', domain="[('employee_id', '=', employee_id)]")
    cost = fields.Float(compute='_compute_cost')

    @api.onchange('life_id')
    def _onchange_life_id(self):
        domain = {'life_grade_id': [('life_id', '=', -1)]}
        if self.life_id:
            domain = {'life_grade_id': [('id', 'in', [line.id for line in self.life_id.line_ids])]}
            self.life_grade_id = False
        return {'domain': domain}

    @api.depends('life_grade_id', 'follower_ids')
    def _compute_cost(self):
        employee_cost = self.life_grade_id.total_employee_share
        self.cost = employee_cost + employee_cost * len(self.follower_ids)