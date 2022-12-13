from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class mbany_check_managment(models.Model):
    _inherit = 'account.move.line'

    approved = fields.Boolean(default=False, string='Approved',copy=False)
    approve_journal_id = fields.Many2one('account.journal', domain=[('type', 'in', ('bank', 'cash'))])

    def approve(self):
        if self.approve_journal_id:
            self.approved = True
        else:
            raise ValidationError("Must Select Approve Journal")

    diff_amount = fields.Float(string='Change Of Amount',copy=False,store=True,compute='calc_diff_amount')
    @api.depends('price_total')
    def calc_diff_amount(self):
        for r in self:
            r.diff_amount = r.price_total
    #
    # @api.onchange('payment_amount')
    # def cons_payment_amount(self):
    #     if self.payment_amount > self.diff_amount:
    #         raise ValidationError("Can't Pay More Price Of Item")


class PaymentInherit(models.Model):
    _inherit = 'account.payment'

    item_approve = fields.One2many('payment.approves', 'payment_approve_id')
    balance_journal = fields.Float(related='journal_id.default_account_id.current_balance', string='Balance Journal')
    # def action_draft(self):
    #     for r in self.item_approve:
    #         r.item_id.diff_amount += r.amount
    #     return super(PaymentInherit, self).action_draft()

    def unlink(self):
        for r in self:
            approves = self.env['payment.approves'].search([('id','in',r.item_approve.ids)])
            approves.unlink()
        return super(PaymentInherit, self).unlink()

    @api.constrains('item_approve','amount')
    def cons_payment_amount(self):
        amount = 0
        if self.item_approve:
            for r in self.item_approve:
                amount += r.amount
            if self.amount != amount:
                raise ValidationError("Must amount Of Payment Equal Total Paid Of Items")




class PaymentApprove(models.Model):
    _name = 'payment.approves'

    payment_approve_id = fields.Many2one('account.payment',)
    journal_line_id = fields.Many2one('account.journal',related='payment_approve_id.journal_id',store=True)
    item_id = fields.Many2one(comodel_name='account.move.line', string='Item',required=True)
    amount = fields.Float()
    operator = fields.Selection([
        ('-', '-'),
        ('+', '+'),
        ('=', '='),
        ('other', 'Other')
    ],default='=')

    @api.onchange('amount')
    def onchange_amount(self):
        print('ppp',self._origin.amount)
        print('now',self.amount)
        if self._origin.amount == self.amount:
            self.operator = '='
        elif self._origin.amount > self.amount:
            self.operator = '-'
        if self._origin.amount < self.amount:
            self.operator = '+'

    # and (self.payment_approve_id.state == 'posted' or (
    #             self.payment_approve_id.state_check == 'collected' and self.payment_approve_id.payment_method_id.name == 'Checks'))

    @api.constrains('amount','state_check','payment_method_id')
    def constrains_amount(self):
        if self.item_id.diff_amount - self.amount >= 0 :
            if self.operator == '+':
                self.item_id.diff_amount -= self.amount
            if self.operator == '-':
                self.item_id.diff_amount += self.amount
        else:
            raise ValidationError("Can't Paid More Than Amount Of Item")

    def unlink(self):
        for r in self:
            r.item_id.diff_amount += r.amount
        return super(PaymentApprove, self).unlink()






