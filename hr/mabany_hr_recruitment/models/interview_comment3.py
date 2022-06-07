# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class interview_comment3(models.Model):
    _name = 'interview.comment3'
    _rec_name = 'stage_name'

    stage_name = fields.Many2one('hr.recruitment.stage',string='Stage Name',compute='get_current_stage',store=True)
    recruiter = fields.Many2one('res.users', "Interviewer", readonly=True, default=lambda self: self.env.uid,
                                store=True)
    date=fields.Date('Interview Date',required=True, default=lambda self: fields.Date.context_today(self))
    comment=fields.Text('Comment')
    application_id=fields.Many2one('hr.applicant',readonly=True)

    @api.depends('application_id')
    def get_current_stage(self):
        for rec in self:
            rec.stage_name=rec.application_id.stage_id.id


    @api.model
    def unlink(self):
        if self.recruiter.id != self.env.uid:
            raise ValidationError(_('You can not delete a comment of others!'))

        return super(interview_comment3, self).unlink()

    @api.model
    def write(self,vals):
        if self.recruiter.id != self.env.uid:
            raise ValidationError(_('You can not edit a comment of others!'))

        return super(interview_comment3, self).write(vals)






