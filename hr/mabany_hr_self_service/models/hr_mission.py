from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request


class HrMission(models.Model):
    _name = 'hr.mission'
    # _inherit = 'hr.self.service'
    _inherit = ['hr.self.service', 'mail.thread', 'mail.activity.mixin']


    start_date = fields.Datetime()
    end_date = fields.Datetime()
    period = fields.Float(compute='_compute_period')



    my_manager = fields.Boolean(string='Current user is my_manager',
                                              compute='_compute_my_manager')


    #button will appear for manager of the employee
    def _compute_my_manager(self):
        if self.sudo().employee_id.parent_id.user_id.id == self.env.user.id:
            self.my_manager = True
        else:
            self.my_manager = False



    @api.depends('start_date', 'end_date')
    def _compute_period(self):
        for rec in self:
            rec.period = 0
            if rec.end_date and rec.start_date:
                rec.period = (rec.end_date - rec.start_date).total_seconds() / 3600.0

    def refuse(self):
        # delete if created before a record in calendar leaves
        found = self.env['resource.calendar.leaves'].search([('mission_id', '=', self.id)])
        if found:
            found.unlink()

        super(HrMission, self).refuse()

    def validate_all(self):
        for rec in self:
            rec.validate()


    def validate(self):
        super(HrMission, self).validate()

        #delete if created before a record in calendar leaves
        found=self.env['resource.calendar.leaves'].search([('mission_id','=',self.id)])
        if found:
            found.unlink()

        self.env['resource.calendar.leaves'].create({
            'mission_id':self.id,
            'name': 'HR Mission: %s' % (self.comment if self.comment else ''),
            'resource_id': self.employee_id.resource_id.id,
            'calendar_id': self.employee_id.resource_calendar_id.id,
            'date_from': self.start_date,
            'date_to': self.end_date
        })




    def first_approve(self):
        for rec in self:
            if rec.filtered(lambda holiday: holiday.state != 'draft'):
                raise UserError(_('Mission request must be in Draft state in order to approve it.'))
            rec.write({'state': 'approve'})
            rec.notify_second_approvers()


    def second_approve(self):
        for rec in self:
            if rec.filtered(lambda holiday: holiday.state != 'approve'):
                raise UserError(_('Time off request must be in approved state in order to validate it.'))

            rec.validate()




    # when create mission notify  manager of the employee

    def send_notification(self, partner_id, employee_name, leave_page_url):
        notification_ids = [(0, 0, {
            'res_partner_id': partner_id,
            'notification_type': 'inbox'
        })]
        self.message_post(record_name='Mission Request', body=""" Mission Request from employee: """ + employee_name + """
             <br> You can access Mission details from here: <br>""" + """<a href="%s">Link</a>""" % (
            leave_page_url)
                          , message_type="notification",
                          subtype_xmlid="mail.mt_comment",
                          author_id=self.env.user.partner_id.id,
                          notification_ids=notification_ids)

    def leave_page(self):
        menu_id = self.env.ref('hr_holidays.menu_hr_holidays_root')
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&amp;view_type=form&amp;model=%s' % (self.id, self._name)
        base_url += '&amp;menu_id=%d&amp;action=%s' % (menu_id.id, '')
        return base_url

    def notify_with_notification(self):
        # send notification to approvers
        for leave in self:
            if leave.employee_id.parent_id and leave.employee_id.parent_id.user_id:
                approver_partner = leave.employee_id.parent_id.user_id.partner_id.id
                self.sudo().send_notification(approver_partner, leave.employee_id.name, self.sudo().leave_page())

    def notify_approvers(self):
        self.sudo().notify_with_notification()

    @api.model
    def create(self, values):
        """ Override to avoid automatic logging of creation """
        leave = super(HrMission, self).create(values)
        leave.notify_approvers()
        return leave

    # notifiy group users
    def notify_second_approvers(self):
        # send notification to approvers
        for leave in self:
            #
            approvers = request.env.ref('mabany_hr_self_service.group_second_approve_leave').sudo().users
            approvers = approvers

            for user in approvers:
                approver_partner = user.partner_id.id
                self.sudo().send_notification(approver_partner, leave.employee_id.name, self.sudo().leave_page())


    #
