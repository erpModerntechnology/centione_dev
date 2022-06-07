# -*- coding:utf-8 -*-

from odoo import models, fields, api
from collections import namedtuple

from datetime import datetime, time
from pytz import timezone, UTC

from odoo import api, fields, models
from odoo.addons.base.models.res_partner import _tz_get
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _



class Holidays(models.Model):
    _inherit = "hr.leave"

    
    def _default_approver(self):
        employee = self._default_employee()
        if type(employee) is int:
            employee_obj = self.env['hr.employee'].browse(employee)
        else:
            employee_obj = employee
        if employee_obj.holidays_approvers:
            return employee_obj.holidays_approvers[0].approver.id

    pending_approver = fields.Many2one('hr.employee', string="Pending Approver")
    pending_approver_rel = fields.Char(string="Pending Approver",
                                       related='pending_approver.name', readonly=True)
    pending_approver_user = fields.Many2one('res.users', string='Pending approver user',
                                            related='pending_approver.user_id', related_sudo=True, store=True,
                                            readonly=True)
    current_user_is_approver = fields.Boolean(string='Current user is approver',
                                              compute='_compute_current_user_is_approver')
    current_user_is_refusers = fields.Boolean(string='Current user is refuser',
                                              compute='_compute_current_user_is_refuser')
    approbations = fields.One2many('hr.employee.holidays.approbation', 'holidays', string='Approvals', readonly=True)
    pending_transfered_approver_user = fields.Many2one('res.users', string='Pending transfered approver user',
                                                       compute="_compute_pending_transfered_approver_user",
                                                       search='_search_pending_transfered_approver_user')

    # @api.multi
    def action_confirm(self):
        super(Holidays, self).action_confirm()
        for holiday in self:
            if holiday.employee_id.holidays_approvers:
                app_0day = holiday.employee_id.holidays_approvers.filtered(lambda d: d.max_allow_days == 0).sorted(
                    key=lambda x: x.sequence)
                if app_0day:
                    holiday.pending_approver = app_0day[0].approver
                else:
                    app_days = holiday.employee_id.holidays_approvers.filtered(
                        lambda d: d.max_allow_days != 0 and d.max_allow_days < holiday.number_of_days_temp).sorted(key=lambda x: x.max_allow_days)
                    if app_days:
                        holiday.pending_approver = app_days[0].approver.id

    # @api.multi
    def action_approve(self):
        for holiday in self:
            is_last_approbation = False
            sequence = 0
            next_approver = None

            approvers_0day = holiday.employee_id.holidays_approvers.filtered(lambda d: d.max_allow_days == 0).sorted(
                key=lambda x: x.sequence)
            approvers_days = holiday.employee_id.holidays_approvers.filtered(
                lambda d: d.max_allow_days != 0 and d.max_allow_days < holiday.number_of_days_temp).sorted(
                key=lambda x: x.max_allow_days)

            if approvers_0day:
                for index, appr in enumerate(approvers_0day):
                    if holiday.pending_approver.id == appr.approver.id:
                        if index == len(approvers_0day) - 1:
                            if approvers_days:
                                next_approver = approvers_days[0].approver
                            else:

                                is_last_approbation = True
                        else:
                            next_approver = approvers_0day[index + 1].approver

                for indexes, apprs in enumerate(approvers_days):
                    if holiday.pending_approver.id == apprs.approver.id:
                        if indexes == len(approvers_days) - 1:
                            is_last_approbation = True
                        else:
                            next_approver = approvers_days[indexes + 1].approver

            elif approvers_days:
                for indexess, apprss in enumerate(approvers_days):
                    if holiday.pending_approver.id == apprss.approver.id:
                        if indexess == len(approvers_days) - 1:
                            is_last_approbation = True
                        else:
                            next_approver = approvers_days[indexess + 1].approver

            holiday = holiday.sudo()
            if is_last_approbation:
                holiday.action_validate()
            else:
                holiday.write({'state': 'confirm', 'pending_approver': next_approver and next_approver.id or False})
                self.env['hr.employee.holidays.approbation'].create(
                    {'holidays': holiday.id, 'approver': self.env.uid, 'sequence': sequence,
                     'date': fields.Datetime.now()})

    # @api.multi
    def action_validate(self):
        self.write({'pending_approver': None})
        for holiday in self:
            self.env['hr.employee.holidays.approbation'].create(
                {'holidays': holiday.id, 'approver': self.env.uid, 'date': fields.Datetime.now()})
        super(Holidays, self).action_validate()


    def _compute_current_user_is_approver(self):
        if self.sudo().pending_approver.user_id.id == self.env.user.id:
            self.current_user_is_approver = True
        else:
            self.current_user_is_approver = False

    def _compute_current_user_is_refuser(self):
        if self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            self.current_user_is_refusers = True
        else:
            self.current_user_is_refusers = False

    @api.onchange('employee_id')
    def _onchange_employee(self):
        for holiday in self:
            if holiday.employee_id and holiday.employee_id.holidays_approvers:
                app_0day = holiday.employee_id.holidays_approvers.filtered(lambda d: d.max_allow_days == 0).sorted(
                    key=lambda x: x.sequence)
                if app_0day:
                    holiday.pending_approver = app_0day[0].approver.id
                else:
                    app_days = holiday.employee_id.holidays_approvers.filtered(
                        lambda d: d.max_allow_days != 0 and d.max_allow_days < holiday.number_of_days_temp).sorted(key=lambda x: x.max_allow_days)
                    if app_days:
                        holiday.pending_approver = app_days[0].approver.id
            else:
                holiday.pending_approver = False

    # @api.one
    def _compute_pending_transfered_approver_user(self):
        self.pending_transfered_approver_user = self.pending_approver.transfer_holidays_approvals_to_user

    def _search_pending_transfered_approver_user(self, operator, value):
        replaced_employees = self.env['hr.employee'].search([('transfer_holidays_approvals_to_user', operator, value)])
        employees_ids = []
        for employee in replaced_employees:
            employees_ids.append(employee.id)
        return [('pending_approver', 'in', employees_ids)]

    # @api.multi
    def action_refuse(self):
        self_sudo = self.sudo()
        super(Holidays,self_sudo).action_refuse()
        self_sudo._onchange_employee()
        return True
