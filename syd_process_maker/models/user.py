
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResUsersExt(models.Model):
    _inherit = 'res.users'

    pm_user_id = fields.Integer('PM User ID')