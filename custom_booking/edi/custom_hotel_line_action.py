from openerp.osv import osv, fields
from openerp.addons.edi import EDIMixin
from openerp import tools
from openerp.tools.translate import _

class custom_hotel_line_action(osv.osv, EDIMixin):
    _name = custom.hotel.line.action
    _inherit = ['custom.hotel.line']

    _columns = {
    			'room':fields.many2one('custom.booking.room'),
    			}
custom_hotel()