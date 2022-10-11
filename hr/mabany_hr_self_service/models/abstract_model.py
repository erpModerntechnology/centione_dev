from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AbstractModel(models.AbstractModel):
    _name = 'hr.self.service'

    def employee_domain(self):
        if self.env.user.has_group('mabany_hr_self_service.group_see_my_employees_self_service'):
            domain = ['|',('user_id','=',self.env.user.id),('parent_id.user_id', '=',
                self.env.user.id)]
            return domain

    employee_id = fields.Many2one('hr.employee',domain=employee_domain)
    start_date = fields.Date()
    end_date = fields.Date()
    comment = fields.Char()
    state = fields.Selection([('draft', 'Draft'), ('approve', 'approved'), ('validate', 'Validated'), ('refuse', 'Refused')],
                             default='draft')

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise UserError(_('End date can not be before Start date.'))

    def approve(self):
        self.state = 'approve'

    def validate(self):
        self.state = 'validate'

    def refuse(self):
        self.state = 'refuse'

    def draft(self):
        self.state = 'draft'

