from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class PaymentTerm(models.Model):
    _name = 'payment.term'

    @api.onchange('amount', 'period', 'no_install', 'first_install_date', 'journal_id', 'bank_name', 'cheque')
    def _domain_install_type(self):
        domain = []
        if self.reservation_id.final_unit_price_rem <= 0:
            domain.append(('deposite', '=', False))
            domain.append(('installment', '=', False))
        if self.reservation_id.maintenance_rem <= 0:
            domain.append(('maintenance', '=', False))
        if self.reservation_id.utility_fees_rem <= 0:
            domain.append(('utility_fees', '=', False))
        if self.reservation_id.finishing_penalty_rem <= 0:
            domain.append(('finishing_penalty', '=', False))
        return {
            'domain': {
                'install_type': domain
            }
        }

    install_type = fields.Many2one('install.type', string="Type")
    amount = fields.Float('Amount')
    period = fields.Selection(
        [('once', 'Once'), ('monthly', 'Monthly'), ('quarter', 'Quarter'), ('semiannual', 'Semiannual'),
         ('annual', 'Annual')])
    no_install = fields.Integer('No.Of Installment')
    first_install_date = fields.Date('First Install Date')
    end_install_date = fields.Date('End Install Date', compute='_calc_end_install_date', store=True)
    total_amount = fields.Float('Total Amount', compute='_calc_total_amount', store=True)
    reservation_id = fields.Many2one('res.reservation')
    journal_id = fields.Many2one('account.journal', _('Journal'))
    bank_name = fields.Many2one('payment.bank', _("Bank Name"))
    cheque = fields.Integer(_("Cheque Number"))
    notes_receviable = fields.Boolean('Notes Receivable', related='journal_id.is_notes_receivable', store=True)

    @api.depends('no_install', 'amount')
    def _calc_total_amount(self):
        for r in self:
            r.total_amount = r.no_install * r.amount

    @api.depends('first_install_date', 'period', 'no_install')
    def _calc_end_install_date(self):
        for r in self:
            if r.period == 'monthly' and r.first_install_date:
                r.end_install_date = r.first_install_date + relativedelta(months=r.no_install - 1)
            elif r.period == 'quarter' and r.first_install_date:
                r.end_install_date = r.first_install_date + relativedelta(months=3 * r.no_install - 3)
            elif r.period == 'once' and r.first_install_date:
                r.end_install_date = r.first_install_date
            elif r.period == 'semiannual' and r.first_install_date:
                r.end_install_date = r.first_install_date + relativedelta(months=6 * r.no_install - 6)
            elif r.period == 'annual' and r.first_install_date:
                r.end_install_date = r.first_install_date + relativedelta(months=12 * r.no_install - 12)
            else:
                r.end_install_date = False
