from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

from datetime import datetime,timedelta
import calendar


class HrExcuse(models.Model):
    _name = 'hr.excuse'
    _inherit = ['hr.self.service', 'mail.thread', 'mail.activity.mixin']

    start_date = fields.Datetime()
    end_date = fields.Datetime()
    period = fields.Float(compute='_compute_period', store=True)

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
        if self.end_date and self.start_date:
            self.period = (self.end_date - self.start_date).total_seconds() / 3600.0
            if self.period < 1:
                self.period = 1

    def validate_all(self):
        for rec in self:
            rec.validate()

    def refuse(self):
        #delete if created before a record in calendar leaves
        found=self.env['resource.calendar.leaves'].search([('excuse_id','=',self.id)])
        if found:
            found.unlink()

        super(HrExcuse, self).refuse()



    def validate(self):
        super(HrExcuse, self).validate()
        #delete if created before a record in calendar leaves
        found=self.env['resource.calendar.leaves'].search([('excuse_id','=',self.id)])
        if found:
            found.unlink()

        self.env['resource.calendar.leaves'].create({
            'excuse_id': self.id,
            'name': 'HR Excuse: %s' % (self.comment if self.comment else ''),
            'resource_id': self.employee_id.resource_id.id,
            'calendar_id': self.employee_id.resource_calendar_id.id,
            'date_from': self.start_date,
            'date_to': self.end_date
        })


    def first_approve(self):
        for rec in self:
            if rec.filtered(lambda holiday: holiday.state != 'draft'):
                raise UserError(_('Excuse request must be in Draft state in order to Approve it.'))
            rec.write({'state': 'approve'})



    def second_approve(self):
        for rec in self:
            if rec.filtered(lambda holiday: holiday.state != 'approve'):
                raise UserError(_('Excuse request must be in Approved state in order to validate it.'))

            rec.validate()


