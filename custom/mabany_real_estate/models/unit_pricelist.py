from odoo import fields, models, api,_
from odoo.exceptions import ValidationError, UserError



class UnitPriclist(models.Model):
    _name = 'unit.pricelist'

    product_id = fields.Many2one('product.product')
    date_from = fields.Date()
    date_to = fields.Date()
    no_unit = fields.Integer('NO. Of Unit Target')
    new_salesprice = fields.Float()

    @api.constrains('date_from','date_to')
    def constrain_intervals(self):
        rec = self.search([('product_id','=',self.product_id.id)]) - self
        for r in rec:
            if self.date_from >= r.date_from and self.date_from <= r.date_to:
                raise ValidationError(_("Can't Select Date already exsist"))
            if self.date_to >= r.date_from and self.date_to <= r.date_to:
                raise ValidationError(_("Can't Select Date already exsist"))

