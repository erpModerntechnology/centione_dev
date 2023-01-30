from odoo import fields, models, api


class ResLog(models.Model):
    _name = 'res.log'

    user_id = fields.Many2one('res.users')
    time = fields.Datetime()
    state = fields.Char('State')
    res_id = fields.Many2one('res.reservation')
