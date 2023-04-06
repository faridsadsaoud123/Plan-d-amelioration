from odoo import fields, models

class Origine(models.Model):
    _name = "pdca.origine"
    _description = "Origine d'un constat"
    _rec_name="name"
    
    name = fields.Char(string="Origine")
    