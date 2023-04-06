from odoo import fields,models
class TypeConstat(models.Model):
    _name = "pdca.type_constat"
    _description="les type de constats"

    name = fields.Char(string="Type de constat")