from odoo import fields, models, api,_
from odoo.exceptions import UserError



class VendorWizard(models.TransientModel):
    _name = 'vendor.wizard'

    vendor = fields.Many2one('res.partner',required=True,domain=[('supplier_rank','>',0)])

    def done(self):
        request = self.env['purchase.request'].browse(self.env.context.get('active_id'))
        lines = []
        for s in request.line_ids:
                if s.check:

                    lines.append((0, 0, {
                            'product_id': s.product_id.id,
                            'product_qty': s.product_qty,
                            'item_id': s.item_id.id,
                            'price_unit': s.unit_price,
                            'price_subtotal':s.subtotal,
                            'name': s.product_id.display_name
                        }))
                    s.done = True
                    s.check=False
        if lines:
            purchase = self.env['purchase.order'].create({
                "partner_id": self.vendor.id,
                "origin": request.name,
                "order_line":lines
            })
        else:
            raise UserError(_(
                "Must Select Line.",
            ))
        if request.done == True:
            request.state = 'done'
class VendorWizard(models.TransientModel):
    _name = 'rfq.wizard'

    purchase = fields.Many2one('purchase.order',required=True,domain="[('state', '=', 'draft')]")

    def done(self):
        request = self.env['purchase.request'].browse(self.env.context.get('active_id'))
        lines = []
        for s in request.line_ids:
                if s.check:

                    lines.append((0, 0, {
                            'product_id': s.product_id.id,
                            'item_id': s.item_id.id,
                            'product_qty': s.product_qty,
                            'price_unit': s.unit_price,
                            'price_subtotal':s.subtotal,
                            'name': s.product_id.display_name
                        }))
                    s.done = True
                    s.check=False
        if lines:
            self.purchase.write({
                "origin": request.name,
                "order_line":lines
            })
        else:
            raise UserError(_(
                "Must Select Line.",
            ))
        if request.done == True:
            request.state = 'done'





