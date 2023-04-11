from odoo import fields, models

class Direction(models.Model):
    _name = "pdca.direction"
    _description = "les directions"
    
    name = fields.Char('Nom Direction:', required=True)
    cree_le = fields.Date('Date de creation') 
    directeur = fields.Many2one('pdca.employe','Directeur',
        domain=[('direction_id','=',name)]
    )
    referent = fields.Many2one('pdca.employe','Referent',
        domain=[('direction_id','=',name)]
    )
    unite_ids=fields.One2many('pdca.unite','direction','Unites',domain="[('direction','=',name)]")
    
    