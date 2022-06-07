from odoo import models, api, fields, _





class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    follower_ids = fields.One2many('hr.employee.follower', 'employee_id')
    attendance_id = fields.Char(string="Attendance ID")

    _sql_constraints = [('attendance_id', 'unique(attendance_id)', 'Attendance Id must be unique!'), ]

    def _is_name(self, name):
        return not any(char.isdigit() for char in name)

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    attendance_id = fields.Char(string="Attendance ID")