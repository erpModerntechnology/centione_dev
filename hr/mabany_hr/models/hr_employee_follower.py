from odoo import models, fields, api, _


class HrEmployeeFollower(models.Model):
    _name = 'hr.employee.follower'

    name = fields.Char()
    employee_id = fields.Many2one('hr.employee')
    birth_date = fields.Date()
