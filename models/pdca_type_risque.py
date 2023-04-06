from odoo import fields,models
class TypeAction(models.Model):
    _name = "pdca.type_risque"
    _description="les type des risque"

    name = fields.Char(string="Type du risque")