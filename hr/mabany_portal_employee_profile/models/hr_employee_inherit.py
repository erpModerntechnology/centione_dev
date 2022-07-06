# # -*- coding: utf-8 -*-
from odoo import models, fields, api , _

class hr_employee_inherit(models.Model):
    _inherit = "hr.employee"

    def create_portal_user(self):
        #for not set user_id ,create portal user
        for rec in self:
            if not rec.user_id:
                created_user=self.env['res.users'].create({
                    'name':rec.name,
                    'email':rec.work_email if rec.work_email else rec.zk_emp_id,
                    'login':rec.work_email if rec.work_email else rec.zk_emp_id,
                    'password':'123g',
                })
                portal_user_group = rec.env.ref('base.group_portal')
                public_user_group = rec.env.ref('base.group_public')
                internal_user_group = rec.env.ref('base.group_user')



                public_user_group.users = [(3, created_user.id)]
                internal_user_group.users = [(3, created_user.id)]

                portal_user_group.users = [(4, created_user.id)]

                rec.user_id=created_user.id


