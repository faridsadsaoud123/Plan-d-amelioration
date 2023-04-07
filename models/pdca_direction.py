from odoo import fields, models

class Direction(models.Model):
    _name = "pdca.direction"
    _description = "les directions"

    name = fields.Char('Nom Direction:', required=True)
    cree_le = fields.Date('Date de creation') 
    directeur = fields.Many2one('res.users','Directeur')
    unite_ids=fields.One2many('pdca.unite','direction','Unites',domain="[('direction','=',name)]")
    
    