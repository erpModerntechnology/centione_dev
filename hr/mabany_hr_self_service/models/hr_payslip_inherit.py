from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.constrains('employee_id', 'date_from', 'date_to', 'struct_id')
    def no_duplicate_payslip_in_same_month(self):
        self = self.sudo()
        created_before = self.env['hr.payslip'].search([
            ('id', '!=', self.id),
            ('employee_id', '=', self.employee_id.id),
            ('struct_id', '=', self.struct_id.id),
            ('date_from', '=', self.date_from),
            ('date_to', '=', self.date_to),
        ])
        if created_before:
            raise UserError(_('Duplicated payslip in same month!'))

    def compute_sheet(self):
        for rec in self:
            leaves = self.env['resource.calendar.leaves'].search(
                ['|', '|', ('holiday_id.employee_id.id', '=', rec.employee_id.id),
                 ('excuse_id.employee_id.id', '=', rec.employee_id.id),
                 # added for get excuses
                 ('mission_id.employee_id.id', '=', rec.employee_id.id)
                 # added for get missions
                 ])
            for it in leaves:
                it.reset_consume_hours()
        res = super(HrPayslip, self).compute_sheet()
        ##todo if worked
        for rec in self:
            leaves = self.env['resource.calendar.leaves'].search(
                ['|', '|', ('holiday_id.employee_id.id', '=', rec.employee_id.id),
                 ('excuse_id.employee_id.id', '=', rec.employee_id.id),
                 # added for get excuses
                 ('mission_id.employee_id.id', '=', rec.employee_id.id)
                 # added for get missions
                 ])
            for it in leaves:
                it.reset_consume_hours()
        ##
        return res
