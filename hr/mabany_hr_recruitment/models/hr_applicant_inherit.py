# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError


from datetime import date


class hr_applicant_inherit(models.Model):
    _inherit = 'hr.applicant'
    stage_sequence= fields.Integer(related='stage_id.sequence')
    is_closed = fields.Boolean()
    closed_date = fields.Date('Closed Date',default=date.today())
    comment_interview1=fields.One2many('interview.comment1','application_id',string='Interview(1) Comment',limit=1)
    comment_interview2=fields.One2many('interview.comment2','application_id',string='Interview(2) Comment',limit=1)
    comment_interview3=fields.One2many('interview.comment3','application_id',string='Interview(3) Comment',limit=1)
    comment_interview4=fields.One2many('interview.comment4','application_id',string='Interview(4) Comment',limit=1)
    notice_period = fields.Date('Notice Period')


    @api.onchange('department_id')
    def onchange_interviewer(self):
        return {'domain': {'user_id': [('department_id', '=', self.department_id.id)]}}






    def create_employee_from_applicant(self):
        self.is_closed = True
        return super(hr_applicant_inherit, self).create_employee_from_applicant()

