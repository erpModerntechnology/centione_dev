# -*- encoding: utf-8 -*-
# Baamtu, 2017
# GNU Affero General Public License <http://www.gnu.org/licenses/>
{
    "name" : "Mabany multi levels approval",
    "version" : "10.3",
    'license': 'AGPL-3',
    "author" : "Baamtu Senegal",
    "category": "Generic Modules/Human Resources",
    'website': 'http://www.baamtu.com/',
    'images': ['static/description/banner.jpg'],
    'depends' : ['hr', 'hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee.xml',
        'views/hr_leave.xml'
        ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False
}

