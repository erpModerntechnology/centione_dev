from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request


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


    def notify_second_approvers(self):
        # send notification to approvers
        for leave in self:
            #
            approvers = request.env.ref('mabany_hr_self_service.group_second_approve_leave').sudo().users
            approvers = approvers

            for user in approvers:
                approver_partner = user.partner_id.id
                self.sudo().send_notification(approver_partner, leave.employee_id.name, self.sudo().leave_page())

    def first_approve(self):
        for rec in self:
            if rec.filtered(lambda holiday: holiday.state != 'draft'):
                raise UserError(_('Time off request must be in Draft state ("To Submit") in order to confirm it.'))
            rec.write({'state': 'confirm'})

            #send notification to second approve group to approve
            self.notify_second_approvers()



    def second_approve(self):
        for rec in self:
            if rec.filtered(lambda holiday: holiday.state != 'confirm'):
                raise UserError(_('Time off request must be in Confirm state ("To Approve") in order to validate it.'))

            rec.action_validate()




