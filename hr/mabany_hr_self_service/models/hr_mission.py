from odoo import models, fields, api, _
from odoo.exceptions import UserError


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



    def second_approve(self):
        for rec in self:
            if rec.filtered(lambda holiday: holiday.state != 'approve'):
                raise UserError(_('Time off request must be in approved state in order to validate it.'))

            rec.validate()



