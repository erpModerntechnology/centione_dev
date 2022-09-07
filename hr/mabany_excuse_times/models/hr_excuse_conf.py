# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrExcuseConf(models.Model):
    _name = 'hr.excuse.conf'

    name = fields.Char(default="Hr Excuse Conf")
    hr_excuse_conf_lines = fields.One2many('hr.excuse.conf.lines','hr_excuse_conf_id')




