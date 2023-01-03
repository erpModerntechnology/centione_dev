from odoo import fields, models, api,_



class ResPartner(models.Model):
        _inherit = 'res.partner'

        is_broker = fields.Boolean(_('Broker'))
        organization = fields.Char(_('Organization'))
        nationality = fields.Char(string="Nationality", required=False, )
        id_def = fields.Char(string="ID", required=False, )
        social_status = fields.Selection(string="Social Status",
                                         selection=[('married', 'Married'), ('single', 'Single'), ], required=False, )
        job_loctaion = fields.Char('Job Location')
        id_date = fields.Date('ID Date')
        id_place = fields.Char('ID Place')
        is_sale = fields.Boolean(string="Salesman")
        company_team_id = fields.Many2one(
            'company.team', "User's company Team",
            help='Company Team the user is member of. Used to compute the members of a Company Team through the inverse one2many')


class ResUsers(models.Model):
    _inherit = 'res.users'

    company_team_id = fields.Many2one(
        'company.team', "User's company Team",
        help='Company Team the user is member of. Used to compute the members of a Company Team through the inverse one2many')
