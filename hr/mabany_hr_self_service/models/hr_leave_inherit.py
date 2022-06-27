from odoo import models, fields, api, _
from odoo.exceptions import UserError


class hr_leave_inherit(models.Model):
    _inherit = 'hr.leave'


    my_manager = fields.Boolean(string='Current user is my_manager',
                                              compute='_compute_my_manager')


    #button will appear for manager of the employee
    def _compute_my_manager(self):
        if self.sudo().employee_id.parent_id.user_id.id == self.env.user.id:
            self.my_manager = True
        else:
            self.my_manager = False


    def first_approve(self):
        for rec in self:
            if rec.filtered(lambda holiday: holiday.state != 'draft'):
                raise UserError(_('Time off request must be in Draft state ("To Submit") in order to confirm it.'))
            rec.write({'state': 'confirm'})



    def second_approve(self):
        for rec in self:
            if rec.filtered(lambda holiday: holiday.state != 'confirm'):
                raise UserError(_('Time off request must be in Confirm state ("To Approve") in order to validate it.'))

            rec.action_validate()




