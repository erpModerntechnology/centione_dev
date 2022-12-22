from odoo import fields, models, api


class ItemCode(models.Model):
    _name = 'item.code'


    name = fields.Char(compute='calc_name',store=True)
    item_code = fields.Char(required=True)
    desc = fields.Char(string='Describtion',required=True)

    @api.depends('item_code','desc')
    def calc_name(self):
        for rec in self:
            rec.name = rec.item_code + '-' + rec.desc



