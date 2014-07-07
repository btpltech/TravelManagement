from openerp.osv import osv, fields
from openerp.addons.edi import EDIMixin
from openerp import tools
from openerp.tools.translate import _

class booking_hotel_room(osv.osv, EDIMixin):
    _name = booking.hotel.room
    _inherit = ['booking.hotel.room']

booking_hotel_room()