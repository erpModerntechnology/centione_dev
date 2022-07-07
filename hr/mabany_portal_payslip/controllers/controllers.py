# -*- coding: utf-8 -*-
import math
from odoo import exceptions

from werkzeug import urls

from odoo import fields as odoo_fields, tools, _
from odoo.exceptions import ValidationError
from odoo.http import Controller, request, route, Response
from datetime import datetime, timedelta
from odoo.exceptions import UserError, AccessError, ValidationError


class PayslipPortal(Controller):

    # payslip list page
    @route(['/my/payslips'], type='http', auth="user", website=True)
    def myPayslips(self, **kw):
        def convert_datetime_to_date(date):
            if date:
                return str(date).split(' ')[0]
            else:
                return False

        get_class_state_dict = {'cancel': 'label label-danger', 'closed': 'label label-danger',
                                'approved': 'label label-info',
                                'draft': 'label label-warning',
                                'sent': 'label label-success'}
        get_description_state_dict = {'draft': 'Draft', 'approved': 'Approved',
                                      'cancel': 'Cancelled', 'sent': 'Sent', 'closed': 'Closed', }
        vals = {}
        vals['convert_datetime_to_date'] = convert_datetime_to_date
        vals['get_description_state_dict'] = get_description_state_dict
        vals['get_class_state_dict'] = get_class_state_dict

        # get payslip has the current user as related user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)])

        # get payslip types
        payslips = {}

        # get payslips for these payslip types
        if employee_id:
            payslips = request.env['hr.payslip'].sudo().search(
                [('employee_id', '=', employee_id.id)
                 ])
        vals['payslips'] = payslips

        return request.render("mabany_portal_payslip.my_payslips", vals)


    # specific payslip page
    @route(['/my/payslip/<int:payslip_id>'], type='http', auth="user", website=True)
    def myPayslip(self, payslip_id=0, **kw):
        def convert_datetime_to_date(date):
            if date:
                date = datetime.strptime(str(date).split(' ')[0], '%Y-%m-%d')
                return date.strftime("%Y-%m-%d")
            else:
                return False

        vals = {}
        vals['error'] = {}
        vals['convert_datetime_to_date'] = convert_datetime_to_date

        if payslip_id > 0:
            vals['payslip'] = request.env['hr.payslip'].sudo().browse(payslip_id)
        return request.render("mabany_portal_payslip.my_payslip", vals)


    @route(['/my/payslip/update'], type='http', auth="user", website=True)
    def myPayslipUpdate(self, payslip_id, **post):
        if payslip_id != '':
            payslip_id = int(payslip_id)
            if payslip_id > 0:
                payslip_id = request.env['hr.payslip'].sudo().browse(payslip_id)
                if payslip_id and post.get('to_delete') == "on":
                    # payslip_id.unlink()
                    pass
                elif payslip_id:
                    pass
                    # payslip_id.update(post)
        else:
            # post['payslip_id'] = request.env['hr.payslip'].sudo().search([('user_id', '=', request.env.uid)]).id
            try:
                # payslip_id = request.env['hr.payslip'].sudo().create(post)
                pass


            except Exception as exc:
                request._cr.rollback()
                post['error_message'] = "Error " + str(exc) + ' '
                return self.myPayslipsCreate(post)
        return request.redirect('/my/payslips')

    @route(['/my/payslip/delete'], type='http', auth="user", website=True)
    def myPayslipDelete(self, **post):
        for key, value in post.items():
            if key.isdigit():
                payslip_id = int(key)
                payslip_id = request.env['hr.payslip'].sudo().browse(payslip_id)
                if payslip_id:
                    pass
                    # payslip_id.sudo().unlink()
        return request.redirect('/my/payslips')
