from odoo import models, fields, api,_


class masria_real_state_build(models.Model):
    _name = 'res.build'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char('Building No.',)
    build_liscence = fields.Char('Building Licence',)
    build_desc = fields.Char('Building Description',)
    no_level = fields.Float('No. Of Levels',)
    no_units = fields.Float('No. Of Units',)
    phase_id = fields.Many2one('project.phase','Phase',)
    project_id = fields.Many2one('project.project','Project',)
    categ = fields.Many2one('product.category','Units type')
    units = fields.One2many('product.product','build_id',compute='calc_units',store=True,inverse='inverse_units')
    select_all = fields.Boolean('Select All')
    sellable_area = fields.Float(string="Sellable Area",  required=False, )
    sellable_price = fields.Float(string="Sellable Price",  required=False, )
    net_area = fields.Float(string="Net Area",  required=False, )
    is_garage = fields.Boolean(string="Is Garage ?", )
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company,readonly=True)


    def update_unit(self):
        for line in self.units:
            # line.price_m = self.net_area
            line.sellable = self.sellable_area
            line.price_m = self.sellable_price
            line.is_garage = self.is_garage







    def calc_units(self):
        line_ids = []
        property = self.env['product.product'].search([('build_id','=',self.id)])
        for line in property:
            line_ids.append(line.id.id)
                # line.write({'payslip_id': self.id})

            self.units = [(6, 0, line_ids)]
        else:
            self.units = [(5, 0, 0)]

    def inverse_units(self):
        pass
