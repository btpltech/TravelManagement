# -*- coding: utf-*-
import datetime
import time
import urllib
import base64
from urllib import urlencode
from urlparse import urljoin
from osv import fields, osv

class travel_hotel_room(osv.osv):    
    _name="travel.hotel.room"
    _description="Table contains the list of the regions of the travel agent."    
    _columns={           
          'hotel_id':fields.char('Hotel Id',size=254,required=True,readonly=True),
          'bill_contact':fields.many2one('res.partner','Billing Contact',size=254,required=True),
          'hotel_name':fields.char('Hotel Name',size=254,required=True, select=True),
          'city_name':fields.many2one('city', 'City Name',size=254, required=True),
          'address':fields.char('address',size=254,required=True),
          'stars':fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7')],'Stars',required=True),
          'room_lines':fields.one2many('room.types', 'room_id', help="Room Types in a Hotel"),
          'meal_lines':fields.one2many('meals', 'meal_id', help="meals provided in hotels"),
          'amenity_lines': fields.one2many('amenity', 'amenity_id', help="Amenity details."),
           }
    _defaults = {
                  'hotel_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'travel.hotel.room'),
                }
    _order='hotel_name'

travel_hotel_room()

class stay_travel_hotel(osv.osv):
    _name="stay.travel.hotel"
    _description="Table contains the list of the regions of the travel agent."
    _columns={ 
          'possible_hotel':fields.many2one('travel.stay'),
          'hotel_id':fields.char('Hotel Id',size=254,readonly=True),
          'hotel_name':fields.many2one('travel.hotel.room', 'Hotel Name', select=True),
          'city_name':fields.many2one('city', 'City Name',size=254, required=True),
          'address':fields.char('address',size=254,required=True),
          'stars':fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7')],'Stars',required=True),
          'room_line':fields.one2many('hotel.room','room', help="Room Types in a Hotel"),
          'meal_line':fields.one2many('hotel.meal', 'meal', help="meals provided in hotels"),
          'amenity_line': fields.one2many('hotel.amenity', 'amen', help="Amenity details."),
           }
    def on_change_hotel(self, cr, uid, ids, hotel_name, context=None):
        result = {}
        values = {}
        if hotel_name:
          partner = self.pool.get('travel.hotel.room').browse(cr, uid, hotel_name, context=context)
          values = {
                    'city_name' : partner.city_name.id,
                    'address' : partner.address,
                    'stars' : partner.stars,
                    }          
        return {'value' : values}
    
travel_hotel_room()

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'isroom':fields.boolean('Is Room'),
        'isamenityid':fields.boolean('Is categ id'),
        'ismeal':fields.boolean('Is Service id'),
    }


class room_types(osv.osv):
  _name="room.types"
  _description="contains the list of room types in the Hotel."
  _columns={
                'room_id':fields.many2one('travel.hotel.room', 'Room Id'),
                'roomtype_name':fields.many2one('product.product', 'Room Type Name', size=254, required=True, select=True),
                'price':fields.float('Price',size=254, required=True),
                'isroom':fields.boolean('Is Room'),
                }
  _defaults = {
        'isroom': 1,
    }
  _order='roomtype_name'

room_types()

class amenity(osv.osv):
  _name="amenity"
  _description="Amenities Provided in the Hotel Room."
  _columns={
            'amenity_id':fields.many2one('travel.hotel.room'),
            'amenity_name':fields.many2one('product.product', 'Amenity Name', size=254, required=True, select=True),
            'description':fields.text('Description',size=254),
            'amount':fields.float('Price', size=254, required=True),
            'isamenityid':fields.boolean('Is amenity id'),
            }
  _defaults = {
        'isamenityid': 1,
    }
  _order='amenity_name'

amenity()

class meals(osv.osv):
  _name="meals"
  _description="List of Meals provided in the Hotel."
  _columns={
                'meal_id':fields.many2one('travel.hotel.room'),
                'mealtype_name':fields.many2one('product.product', 'Meal Type', size=254, required=True, select=True),
                'price_unit':fields.float('Price', size=254, required= True),
                'ismeal':fields.boolean('Is Meal id'),
                }
  _defaults = {
        'ismeal': 1,
    }
  _order='mealtype_name'

meals()

class hotel_room(osv.osv):
  _name="hotel.room"
  _description="contains the list of room types in the Hotel."
  _order = 'roomtype_name'
  _columns={
                'room':fields.many2one('stay.travel.hotel', 'Room Id'),
                'room_id':fields.many2one('travel.hotel.room', 'Room Id'),
                'roomtype_name':fields.many2one('room.types', 'Room Type Name', size=254, required=True),
                'price':fields.float('Price',size=254, required=True),
                }
  def on_change_room(self, cr, uid, ids, roomtype_name, context=None):
        result = {}
        values = {}
        if roomtype_name:
          partner = self.pool.get('room.types').browse(cr, uid, roomtype_name, context=context)
          values = {
                    'price' : partner.price,
                    }          
        return {'value' : values}

hotel_room()

class hotel_amenity(osv.osv):
  _name="hotel.amenity"
  _description="Amenities Provided in the Hotel Room."
  _columns={
            'amen':fields.many2one('stay.travel.hotel', 'Amenity Id'),
            'amenity_id':fields.many2one('travel.hotel.room'),
            'amenity_name':fields.many2one('amenity', 'Amenity Name', size=254, required=True),
            'description':fields.text('Description',size=254),
            'amount':fields.float('Price', size=254, required=True),
            }
  def on_change_amenity(self, cr, uid, ids, amenity_name, context=None):
        result = {}
        values = {}
        if amenity_name:
          partner = self.pool.get('amenity').browse(cr, uid, amenity_name, context=context)
          values = {
                    'description':partner.description,
                    'amount' : partner.amount,
                    }          
        return {'value' : values}

hotel_amenity()

class hotel_meal(osv.osv):
  _name="hotel.meal"
  _description="List of Meals provided in the Hotel."
  _columns={
                'meal':fields.many2one('stay.travel.hotel', 'Meal Id'),
                'meal_id':fields.many2one('travel.hotel.room'),
                'mealtype_name':fields.many2one('meals', 'Meal Type', size=254, required=True),
                'price_unit':fields.float('Price', size=254, required= True),
                }
  def on_change_meal(self, cr, uid, ids, mealtype_name, context=None):
        result = {}
        values = {}
        if mealtype_name:
          partner = self.pool.get('meals').browse(cr, uid, mealtype_name, context=context)
          values = {
                    'price_unit' : partner.price_unit,
                    }          
        return {'value' : values}
hotel_meal()

class travel_package(osv.osv):

    _name="travel.package"
    _description="Table contains the information of the packages created."    
    _columns={
              'package_id':fields.char('Package Id', size=254, readonly=True),
              'img': fields.binary("Image"),
              'package_name':fields.char('Package Name',size=254,required=True),
              'no_adults':fields.selection([('1','1'),('2','2'),('3','3'),('4','4')],'Adults',required=True),
              'no_children':fields.selection([('0','0'),('1','1'),('2','2'),('3','3'),('4','4')],'Children',required=True),
              'discription':fields.text('Description', size=254, required=True),
              'duration':fields.integer('Duration', size=254, required=True),
              'total_price':fields.float('Total Pice', size=254, required=True),
              'stay_lines': fields.one2many('travel.stay', 'stay', help="Stay itenary details."),
              'travel_lines': fields.one2many('travel.itenary', 'travel', help="Travel itenary details."),
              }  
    _defaults = {
                  'package_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'travel.package'),
                  'no_children':'0',
                } 
    _order = 'package_id'

    def get_upload_url(self, cr, uid, ids, fieldname, context=None):
        result = dict.fromkeys(ids, '')
        base_url = "http://traveloore.com/upload.php"
        data = cr.dbname
        for this in self.browse(cr, uid, ids, context=context):
            fragment = this.id
            result[this.id] = urljoin(base_url, "?%s&%s" % (data, fragment))
        return result

travel_package()

class travel_stay(osv.osv):
    _name = "travel.stay"
    _description = "Table contains the information of the city."
    _columns= {
              'stay':fields.many2one('travel.package',readonly=True),
              'stay_id':fields.char('Stay Id',size=254,readonly=True),
              'city_name':fields.many2one('city','City Name', required=True),
              'day_seq': fields.selection([('day1','Day-1'),('day2','Day-2'),('day3','Day-3'),('day4','Day-4'),('day5','Day-5'),('day6','Day-6'),('day7','Day-7'),('day8','Day-8'),('day9','Day-9'),('day10','Day-10')],'Day Sequence',required=True),
              'desc':fields.text('Description', size=250),
              'hotel_lines':fields.one2many('stay.travel.hotel','possible_hotel', 'Hotel Lines'),
              }
    _defaults = {
                  'stay_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'travel.stay'),
                }

travel_stay()

class travel_itenary(osv.osv):
    _name="travel.itenary"
    _description="Table contains the information of the travel itenary."
    _columns={
              'travel':fields.many2one('travel.package', readonly=True),
              'travel_id':fields.char('Travel Id', size=254, required=True,readonly=True),
              'tm_name':fields.many2one('incitytravel.mode','Travel Mode Name', required=True),
              'day_seq': fields.selection([('day1','Day-1'),('day2','Day-2'),('day3','Day-3'),('day4','Day-4'),('day5','Day-5'),('day6','Day-6'),('day7','Day-7'),('day8','Day-8'),('day9','Day-9'),('day10','Day-10')],'Day Sequence',required=True),
              's_city':fields.many2one('city','Source City', required=True),
              'd_city':fields.many2one('city','Destnation City', required=True),
              'price':fields.float('price',size=254, required=True),          
            }
    _defaults = {
                  'travel_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'travel.itenary'),
                } 

travel_itenary()


class incitytravel_mode(osv.osv):
    _name="incitytravel.mode"
    _description="Table contains Intracity travel modes List."
    _columns={
            'name':fields.char('Travel Mode Name', size=254, required=True, translate=True),
            'description':fields.text('Description', size=254),
              }
    _sql_constraints = [
        ('name_uniq', 'unique (tm_name)',
            'The travel mode name must be unique !'),
    ]
    
    _order='name'

incitytravel_mode()

class intracity_travel(osv.osv):
    _name="intracity.travel"
    _description="Table contains Intracity travel modes List."
    _columns={
            'name':fields.char('Travel Mode Name', size=254, required=True, translate=True),
            'des' :fields.text('Description', size=254),
              }
    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            'The travel mode name must be unique !'),
    ]
    
    _order='name'

intracity_travel()

class city(osv.osv):
    _name = 'city'
    _description = 'City'
    _columns = {
        'name': fields.char('City Name', size=64,
            help='The full name of the city.', required=True, translate=True),
        'code': fields.char('City Code', size=20,
            help='The ISO city code in two chars.\n'
            'You can use this field for quick search.'),
        
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            'The name of the city must be unique !'),
        ('code_uniq', 'unique (code)',
            'The code of the city must be unique !')
    ]
    
    _order='name'

city()