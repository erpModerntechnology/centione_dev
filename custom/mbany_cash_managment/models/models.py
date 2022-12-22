from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class mbany_move_managment(models.Model):
    _inherit = 'account.move'
    def all_approves(self):
        for r in self.invoice_line_ids:
            r.approved = True

class mbany_check_managment(models.Model):
    _inherit = 'account.move.line'

    approved = fields.Boolean(default=False, string='Approved',copy=False)
    approve_journal_id = fields.Many2one('account.journal', domain=[('type', 'in', ('bank', 'cash'))])
    approve_ids = fields.Many2many('payment.approves')

    def approve(self):
        # if self.approve_journal_id:
            self.approved = True
        # else:
        #     raise ValidationError("Must Select Approve Journal")

    diff_amount = fields.Float(string='Change Of Amount',copy=False,store=True,compute='calc_diff_amount')
    @api.depends('price_total','move_id.move_type')
    def calc_diff_amount(self):
        for r in self:
            if r.move_id.move_type in ('in_invoice', 'in_refund'):
                r.diff_amount = r.price_total
            else:
                r.diff_amount = 0


class PaymentInherit(models.Model):
    _inherit = 'account.payment'

    item_approve = fields.One2many('payment.approves', 'payment_approve_id')
    balance_journal = fields.Float(related='journal_id.default_account_id.current_balance', string='Balance Journal')

    @api.constrains('item_approve','amount')
    def cons_payment_amount(self):
        amount = 0
        if self.item_approve:
            for r in self.item_approve:
                amount += r.amount
            if self.amount != amount:
                raise ValidationError("Must amount Of Payment Equal Total Paid Of Items")
    def action_post(self):
        # inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        res = super(PaymentInherit, self).action_post()
        if self.payment_method_id.name != 'Checks':
            for r in self.item_approve:
                r.item_id.diff_amount -= r.amount
        return res
    def action_draft(self):
        # inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        res = super(PaymentInherit, self).action_draft()
        if (self.payment_method_id.name != 'Checks' and self.state_check == 'posted') or (self.payment_method_id.name == 'Checks' and self.state_check == 'collected'):
            for r in self.item_approve:
                r.item_id.diff_amount += r.amount
        return res
    def post(self):
        # inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        res = super(PaymentInherit, self).post()
        if self.state_check == 'collected':
            for r in self.item_approve:
                r.item_id.diff_amount -= r.amount
        return res





class PaymentApprove(models.Model):
    _name = 'payment.approves'

    payment_approve_id = fields.Many2one('account.payment',)
    item_id = fields.Many2one(comodel_name='account.move.line', string='Item',required=True)
    amount = fields.Float()
    journal_id = fields.Many2one('account.journal',compute='calc_journal_id',inverse='inv_journal_id',store=True)
    @api.depends('item_id.approve_journal_id')
    def calc_journal_id(self):
        for r in self:
            r.journal_id = r.item_id.approve_journal_id.id
    def inv_journal_id(self):
        for r in self:
            r.item_id.approve_journal_id = r.journal_id.id


    @api.constrains('amount')
    def constrains_amount(self):
        if self.item_id.diff_amount - self.amount >= 0 :
            pass
        else:
            raise ValidationError("Can't Paid More Than Amount Of Item")

    @api.model
    def create(self, vals):
        res = super(PaymentApprove, self).create(vals)
        res.item_id.approve_ids = [(4, res.id)]
        return res







