from odoo import fields,models
class TypeAction(models.Model):
    _name = "pdca.type_action"
    _description="les type des actions"

    name = fields.Char(string="Type d'action")