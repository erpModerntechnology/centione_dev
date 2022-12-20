from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    item_id = fields.Many2one('item.code')
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    item_id = fields.Many2one('item.code')
    def _prepare_analytic_line(self):
        vals = super(AccountMoveLine, self)._prepare_analytic_line()
        vals[0]['item_id'] = self.item_id.id
        print('vals>>>',vals)
        # vals["item_id"] = self.item_id.id
        return vals

class PurchaseMove(models.Model):
    _inherit = 'purchase.order'

    item_id = fields.Many2one('item.code')
class PurchaseMoveLine(models.Model):
    _inherit = 'purchase.order.line'

    item_id = fields.Many2one('item.code')
    def _prepare_account_move_line(self, move=False):
        vals = super(PurchaseMoveLine, self)._prepare_account_move_line(move)
        vals["item_id"] = self.item_id.id
        return vals

class AnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    item_id = fields.Many2one('item.code')
class AccountPayment(models.Model):
    _inherit = 'account.payment'

    item_id = fields.Many2one('item.code')
