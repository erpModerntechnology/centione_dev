# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class HrExcuseConfLines(models.Model):
    _name = 'hr.excuse.conf.lines'
    _order = "start_date desc"

    name = fields.Char(default="Hr Excuse Conf Lines")
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    hr_excuse_conf_id = fields.Many2one('hr.excuse.conf')

    @api.constrains('start_date', 'end_date')
    def check_date(self):
        for rec in self:
            records = rec.env['hr.excuse.conf.lines'].search(
                [('id', '!=', rec.id), '|', '|', '&', ('start_date', '>=', rec.start_date),
                 ('end_date', '<=', rec.end_date), '&',
                 ('start_date', '<=', rec.start_date), ('end_date', '>=', rec.start_date), '&',
                 ('start_date', '<=', rec.end_date), ('end_date', '>=', rec.end_date)])
            if records:
                raise ValidationError(_("Date Is Already Existed"))
