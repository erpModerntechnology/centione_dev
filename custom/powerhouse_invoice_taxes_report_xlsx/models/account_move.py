from odoo import fields, models, api


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    taxes_ids = fields.Many2many('account.tax', compute='get_lines_taxes', store=True)
    total_before_dic = fields.Float(compute='get_disc_amount', store=True)

    @api.depends('invoice_line_ids.tax_ids')
    def get_lines_taxes(self):
        for rec in self:
            tax_ids = []
            for line in rec.invoice_line_ids:
                for tax in line.tax_ids:
                    tax_ids.append(tax.id)
            rec.taxes_ids = [(6, 0, tax_ids)]

    @api.depends('invoice_line_ids.quantity', 'invoice_line_ids.price_unit')
    def get_disc_amount(self):
        for rec in self:
            total = 0
            for line in rec.invoice_line_ids:
                total += line.quantity * line.price_unit
            rec.total_before_dic = total
