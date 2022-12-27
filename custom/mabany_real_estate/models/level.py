from odoo import models, fields, api,_


class masria_real_state_level(models.Model):
    _name = 'res.level'

    name = fields.Char(required=True)
    ground_level = fields.Boolean('Ground Level')
    under_ground_level = fields.Boolean('Under Ground Level')
