# -*- coding: utf-*-

import time
import datetime
from osv import fields, osv

class travel_custompackage(osv.osv):
    _name="travel.custompackage"
    _description="Table of the Request Packages made by the customer."
    _columns={ 
          'cp_id':fields.char('Custom Package Id',size=254,required=True),
          'package_name':fields.char('Package Name',size=254,required=False),
          'date_travel':fields.char('Date of Travel',size=254,required=True),
          'no_adults':fields.selection([('1','1'),('2','2'),('3','3'),('4','4')],'Number of Adults',required=True),
          'no_children':fields.selection([('0','0'),('1','1'),('2','2'),('3','3'),('4','4')],'Number of Children',required=False),
          'hotelstay_lines': fields.one2many('custom.hotel', 'hotelstay', help="Stay itenary details."),
          'intercity_lines': fields.one2many('tranportation', 'intercity', help=" Intercity Travel Itenary Details."),
          'intracity_lines': fields.one2many('intracity.travel', 'intracity', help="Intracity Travel Itenary Details."),
             }
    # _defaults = {
    #               'cp_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'travel.custompack'),
    #             } 
travel_custompackage()

class custom_hotel(osv.osv):

    _name="custom.hotel"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description="List of hotels chosen by customer."
    _columns={
                  'hotelstay':fields.many2one('travel.custompackage',readonly=True),
                  'checkin':fields.datetime('Check-in Date', required=True),
                  'checkout':fields.datetime('Check-out Date', required=True),
                  'no_night':fields.selection([('1','1'),('2','2'),('3','3'),('4','4')],'Nights',required=True),
                  'city':fields.char('City',size=254, required=True),
                  'hotel':fields.many2one('res.partner', 'Hotel Name', size=254, required=True),
                  'room_lines':fields.one2many('custom.room','roomtype_id',required=True, help="Room Types in a Hotel"),
                  'meal_lines':fields.one2many('custom.meal','mealtype_id',required=True, help="meals provided in hotels"),
                  'amenity_lines': fields.one2many('custom.amenities', 'amenity_id',required=True, help="Amenity details."),
                  }
custom_hotel()

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'isroom':fields.boolean('Is Room'),
        'isamenityid':fields.boolean('Is categ id'),
        'ismeal':fields.boolean('Is Service id'),
    }

class custom_room(osv.osv):
      _name="custom.room"
      _description="contains the list of room types in the Hotel."
      _columns={
                'roomtype_id':fields.many2one('custom.hotel', 'Room Type Id'),
                'roomtype_name':fields.many2one('product.product', 'Room Type Name', required=True, size=254),
                'isroom':fields.boolean('Is Room'),
                }
      _defaults = {
                  'isroom': 1,
                  }
custom_room()

class custom_amenities(osv.osv):
  _name="custom.amenities"
  _description="Amenities Provided in the Hotel Room."
  _columns={
            'amenity_id':fields.many2one('custom.hotel', 'Amenity Id'),
            'amenity_name':fields.many2one('product.product', 'Amenity Name', size=254, required=True),
            'description':fields.text('Description',size=254),
            'isamenityid':fields.boolean('Is amenity id'),
            }
  _defaults = {
              'isamenityid': 1,
              }            
custom_amenities()

class custom_meal(osv.osv):
      _name="custom.meal"
      _description="List of Meals provided in the Hotel."
      _columns={
                'mealtype_id':fields.many2one('custom.hotel', 'Meal Type Id'),
                'mealtype_name':fields.many2one('product.product', 'Meal Type Name', size=254, required=True),
                'ismeal':fields.boolean('Is Meal id'),
                }
      _defaults = {
              'ismeal': 1,
              }
custom_meal()

class tranportation(osv.osv):
    _name="tranportation"
    _description="List contains the Intercity Transport Medium."
    _columns={
              'intercity':fields.many2one('travel.custompackage', readonly=True),
              'travel_id':fields.char('Travel Id', size=254, required=True),
              'tm_name':fields.char('Travel Mode Name',size=254, required=True),
              's_city':fields.char('Source City',size=254, required=True),
              'd_city':fields.char('Destnation City',size=254, required=True),
              }
tranportation()

class intracity_travel(osv.osv):
    _name="intracity.travel"
    _description="List of Intracity Travel Mode."
    _columns={
             'intracity':fields.many2one('travel.custompackage', readonly=True),
             'tm_name':fields.char('Travel Mode Name', size=254, required=True), 
             'city':fields.char('City',size=254, required= True),
            }

intracity_travel()      