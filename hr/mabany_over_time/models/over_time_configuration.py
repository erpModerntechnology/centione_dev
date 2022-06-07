# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import logging

LOGGER = logging.getLogger(__name__)


class OverTimeConfiguration(models.TransientModel):
    _name = 'over.time.configuration'

    morning_start_hour = fields.Integer(default=5, store=True)
    night_start_hour = fields.Integer(compute='_compute_night_start_hour', store=True)

    daily_rate = fields.Float(string="Morning Overtime Rate", required=False, )
    night_rate = fields.Float(string="Night Overtime Rate", required=False, )
    holiday_rate = fields.Float(string="Holiday Overtime Rate", required=False, )

    @api.depends('morning_start_hour')
    def _compute_night_start_hour(self):
        self.night_start_hour = (self.morning_start_hour + 12) % 24

    def act_execute(self):
        self.env['ir.config_parameter'].set_param('daily_rate', (self.daily_rate or 1), )
        self.env['ir.config_parameter'].set_param('night_rate', (self.night_rate or 1), )
        self.env['ir.config_parameter'].set_param('holiday_rate', (self.holiday_rate or 1), )
        self.env['ir.config_parameter'].set_param('morning_start_hour', (self.morning_start_hour or 5), )
        self.env['ir.config_parameter'].set_param('night_start_hour', (self.night_start_hour or 17), )

    @api.model
    def default_get(self, fields):
        res = super(OverTimeConfiguration, self).default_get(fields)
        daily_rate = float(self.env['ir.config_parameter'].get_param('daily_rate', default=1))
        night_rate = float(self.env['ir.config_parameter'].get_param('night_rate', default=1))
        holiday_rate = float(self.env['ir.config_parameter'].get_param('holiday_rate', default=1))

        morning_start_hour = int(self.env['ir.config_parameter'].get_param('morning_start_hour', default=5))
        night_start_hour = int(self.env['ir.config_parameter'].get_param('night_start_hour', default=17))

        res2 = dict(daily_rate=daily_rate,
                    night_rate=night_rate,
                    holiday_rate=holiday_rate,
                    morning_start_hour=morning_start_hour,
                    night_start_hour=night_start_hour)
        res.update(res2)
        return res

