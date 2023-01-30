from odoo import models, fields, api, _


class masria_real_state_generate(models.Model):
    _name = 'generate.build'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    type_of_property_id = fields.Many2one('product.category', 'Unit Type')
    project_id = fields.Many2one('project.project', 'Project', required=True)
    phase_id = fields.Many2one('project.phase', _('Phase'), )
    no_of_building = fields.Integer('Number Of Buildings')
    no_of_level = fields.Integer('Number Of Levels')
    no_of_unit_per_level = fields.Integer('Number Of Units Per Level')
    name = fields.Char('Company Prefix', required=True)
    ground_level = fields.Integer('Ground Level')
    under_ground_level = fields.Integer('Under Ground Level')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)
    readonly_flag = fields.Boolean(copy=False)

    def generate(self):
        self.readonly_flag = True
        seq = 1
        seq_2 = 1
        seq_3 = 1
        seq_4 = 1
        for r in range(self.no_of_building):
            build = self.env['res.build'].create({
                'name': self.name + str(seq),
                'categ': self.type_of_property_id.id,
                'phase_id': self.phase_id.id,
                'project_id': self.project_id.id,
                'no_units': self.no_of_unit_per_level * self.no_of_level,
                'no_level': self.no_of_level,
            })
            seq_2 = 1
            for y in range(self.no_of_level):
                n = 1
                level = self.env['res.level'].search([('name', '=', seq_2)])
                print('level', level.name)
                for q in range(self.no_of_unit_per_level):
                    self.env['product.product'].sudo().create({
                        'name': build.name + " " + str(level.name) + '0' + str(n) if len(
                            str(n)) == 1 else build.name + " " + str(level.name) + str(n),
                        'property_code': build.name + " " + str(level.name) + '0' + str(n) if len(
                            str(n)) == 1 else build.name + " " + str(level.name) + str(n),
                        # 'cate_id': self.type_of_property_id.id,
                        'categ_id': self.type_of_property_id.id,
                        # 'type_of_property_id': self.type_of_property_id.id,
                        'is_property': True,
                        'phase_id': self.phase_id.id,
                        'project_id': self.project_id.id,
                        'type': 'service',
                        'detailed_type': 'service',
                        'level': level.id,
                        'build_id': build.id
                    })
                    n += 1

                seq_2 += 1
            seq_3 = 1
            for g in range(self.ground_level):
                ground_level = self.env['res.level'].sudo().search([('ground_level', '=', True)], limit=1)
                self.env['product.product'].create({
                    'name': build.name + " " + str(ground_level.name) + '0' + str(seq_3) if len(
                        str(seq_3)) == 1 else build.name + " " + str(ground_level.name) + str(seq_3),
                    'property_code': build.name + " " + str(ground_level.name) + '0' + str(seq_3) if len(
                        str(seq_3)) == 1 else build.name + " " + str(ground_level.name) + str(seq_3),
                    # 'cate_id': self.type_of_property_id.id,
                    'categ_id': self.type_of_property_id.id,
                    # 'type_of_property_id': self.type_of_property_id.id,
                    'phase_id': self.phase_id.id,
                    'project_id': self.project_id.id,
                    'is_property': True,
                    'type': 'service',
                    'detailed_type': 'service',
                    'level': ground_level.id,
                    'build_id': build.id

                })
                seq_3 += 1
            seq_4 = 1
            for x in range(self.under_ground_level):
                under_ground_level = self.env['res.level'].sudo().search([('under_ground_level', '=', True)], limit=1)
                self.env['product.product'].create({
                    'name': build.name + " " + str(under_ground_level.name) + '0' + str(seq_4) if len(
                        str(seq_4)) == 1 else build.name + " " + str(under_ground_level.name) + str(seq_4),
                    'property_code': build.name + " " + str(under_ground_level.name) + '0' + str(seq_4) if len(
                        str(seq_4)) == 1 else build.name + " " + str(under_ground_level.name) + str(seq_4),
                    # 'cate_id': self.type_of_property_id.id,
                    'categ_id': self.type_of_property_id.id,
                    # 'type_of_property_id': self.type_of_property_id.id,
                    'phase_id': self.phase_id.id,
                    'project_id': self.project_id.id,
                    'is_property': True,
                    'type': 'service',
                    'detailed_type': 'service',
                    'level': under_ground_level.id,
                    'build_id': build.id,

                })
                seq_4 += 1

            seq += 1
