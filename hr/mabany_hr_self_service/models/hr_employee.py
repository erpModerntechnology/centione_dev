from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    number_excuse_per_month = fields.Float()
    max_excuse_period = fields.Float()

    @api.model
    def create(self, vals):
        if vals.get('parent_id', False):
            vals['leave_manager_id'] = False
        res = super(HrEmployee, self).create(vals)
        return res

    def write(self, values):
        if values.get('leave_manager_id', False):
            values.pop('leave_manager_id')
        res = super(HrEmployee, self).write(values)
        return res
