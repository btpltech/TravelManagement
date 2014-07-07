# -*- coding: utf-*-
import datetime
import time
from osv import fields, osv
from openerp import sql_db, tools
from openerp.tools.translate import _

class travel_booking(osv.osv):
  
  def _amount_bal(self, cr, uid, ids, field_name, arg, context=None):
      res = {}
      for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_balance': 0.0,
            }
            val = val1 = 0.0
            val1 += order.amount_total
            val += order.advance_amount
            res[order.id]['amount_balance'] = val1 - val
      return res

  def _check(self, cr, uid, ids, name, args, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            cr.execute('select * from travel_package where package_id=%s', (obj.package_id))
            res = cr.fetchall()
        return self.write(cr, uid, {
                                    'package_name': res.package_name,
                                    }, context=context)

  def _invoiced(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            res[sale.id] = True
            invoice_existence = False
            for invoice in sale.invoice_ids:
                if invoice.state!='cancel':
                    invoice_existence = True
                    if invoice.state != 'paid':
                        res[sale.id] = False
                        break
            if not invoice_existence or sale.state == 'manual':
                res[sale.id] = False
        return res

  _name = "travel.booking"
  _description = "Table contains the bookin details."
  _columns = {
              'book_no':fields.char('Booking Number', size=254, readonly=True),
              'date':fields.datetime('Booking Date', required=True, readonly=True, states={'New': [('readonly', False)]}),
              'start_date':fields.datetime('Start Date', required=False, readonly=True, states={'New': [('readonly', False)]}),
              'end_date':fields.datetime('End Date', required=False, readonly=True, states={'New': [('readonly', False)]}),
              'state':fields.selection([('New','New'),('open','Open'),('confirm','Confirmed'),('cancel','Cancelled')], 'Status', readonly=True, select=True),
              'advance_amount':fields.float('Advance Payment', size=254, readonly=True, states={'New': [('readonly', False)]}),
              'amount_total':fields.float('Amount Total', size=254, readonly=True, states={'New': [('readonly', False)]}),
              'amount_balance': fields.function(_amount_bal, string='Balance Amount', multi='sums'), 
              
              'customer_id':fields.char('Customer Id', size=254, required=True, readonly=True),
              'salutation':fields.selection([('Mr.','Mr.'),('Mrs.','Mrs.')], 'Salutation', required=False, readonly=True, states={'New': [('readonly', False)]}),
              'customer_name': fields.many2one('res.partner', 'Customer Name', required=True,readonly=True, states={'New': [('readonly', False)]}),
              'gender':fields.selection([('male','Male'),('female','Female')], 'Gender', size=254, readonly=True, states={'New': [('readonly', False)]}),
              'address':fields.char('Address', size=254, required=False, readonly=True, states={'New': [('readonly', False)]}),
              'city':fields.char('City', size=254, required=False, readonly=True, states={'New': [('readonly', False)]}),
              'state_name':fields.char('State', size=254, required=False, readonly=True, states={'New': [('readonly', False)]}),
              'country':fields.char('Country', size=254, required=False, readonly=True, states={'New': [('readonly', False)]}),
              'zipcode':fields.char('Zipcode', size=254, required=False, readonly=True, states={'New': [('readonly', False)]}),
              'm_no':fields.char('Mobile', size=254, required=False, readonly=True, states={'New': [('readonly', False)]}),
              'email':fields.char('Email', size=254, required=False, readonly=True, states={'New': [('readonly', False)]}),
              'id_type':fields.selection([('pan','Pan Card'),('passport','Passport')], 'ID Type', required=False, readonly=True, states={'New': [('readonly', False)]}),
              'id_num':fields.char('ID Number', size=254, required=False, readonly=True, states={'New': [('readonly', False)]}),
              

              'package_id':fields.many2one('travel.package', 'Package Id', size=60, required=True),
              'package_name':fields.char('Package Name', size=254, required=False, readonly=True, states={'New': [('readonly', False)]}),
              'adults':fields.char('Adults', required=False, readonly=True, states={'New': [('readonly', False)]}),
              'child':fields.char('Children', readonly=True, states={'New': [('readonly', False)]}),
              'desc':fields.text('Description', size=250, readonly=True, states={'New': [('readonly', False)]}),
              'traveller_line':fields.one2many('traveller.details', 'traveller', readonly=True, states={'New': [('readonly', False)]}),
              'stay_line':fields.one2many('travel.stay.line','stay', readonly=True, states={'New': [('readonly', False)], 'open': [('readonly', False)]}),
              'travel_line':fields.one2many('travel.line','itinerary_id', readonly=True, states={'New': [('readonly', False)], 'open': [('readonly', False)]}),
            
              'invoice_ids': fields.many2many('account.invoice', 'travel_booking_invoice_rel', 'order_id', 'book_no', 'Invoices'),
              'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position'),
              'payment_term_id': fields.many2one('account.payment.term', 'Payment Term'),
              'invoiced': fields.function(_invoiced, string='Paid', type='boolean'),
            }
  _defaults = {
                'book_no': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'travel.booking'),
                'customer_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'travel.booking'),
                'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
                'state': 'New',
                'invoiced': 0,
              }

  def on_change_package(self, cr, uid, ids, package_id, context=None):
        result = {}
        values = {}
        if package_id:
          partner = self.pool.get('travel.package').browse(cr, uid, package_id, context=context)
          values = {
                    'package_name' : partner.package_name,
                    'adults' : partner.no_adults,
                    'child' : partner.no_children,
                    'desc' : partner.discription,
                    }          
        return {'value' : values}

  def action_invoice_create(self, cr, uid, ids, context=None):
        """Generates invoice for given ids of purchase orders and links that invoice ID to purchase order.
        :param ids: list of ids of purchase orders.
        :return: ID of created invoice.
        :rtype: int
        """
        res = False

        journal_obj = self.pool.get('account.journal')
        inv_obj = self.pool.get('account.invoice')

        for order in self.browse(cr, uid, ids, context=context):
            journal_ids = journal_obj.search(cr, uid, [('type', '=','sale')], limit=1)
            if not journal_ids:
                raise osv.except_osv(_('Error!'),
                    _('Define purchase journal for this company.'))
            account_id = order.customer_name.property_account_receivable.id
            if not account_id:
                raise osv.except_osv(_('Error!'),
                    _('Define account id for this customer.'))

            # get invoice data and create invoice
            inv_data = {
                'name': order.desc,
                'reference': order.customer_name.ref,
                'account_id': order.customer_name.property_account_receivable.id,
                'type': 'out_invoice',
                'partner_id': order.customer_name.id,
                'journal_id': len(journal_ids) and journal_ids[0] or False,
                'origin': order.book_no,
                'fiscal_position': False,
                'payment_term': False,
                'company_id': order.customer_name.company_id.id,
                'amount_untaxed':order.amount_total,
                'amount_total':order.amount_total,
                'residual':order.amount_balance,
            }
            inv_id = inv_obj.create(cr, uid, inv_data, context=context)

            # Link this new invoice to related purchase order
            order.write({'invoice_ids': [(4, inv_id)], 'state':'confirm'}, context=context)
            res = inv_id
        return res

  def button_dummy(self, cr, uid, ids, context=None):
        return True

travel_booking()

class traveller_details(osv.osv):
  _name = "traveller.details"
  _description = "Table contains travellers information"
  _columns = {
              'traveller':fields.many2one('travel.booking', readonly=True),
              'traveller_id':fields.char('Traveller Id', size=254, required=True),
              't_salutation':fields.selection([('Mr.','Mr.'),('Mrs.','Mrs.')], 'Salutation', required=False),
              'traveller_name': fields.char('Traveller Name', required=False),
              't_gender':fields.selection([('male','Male'),('female','Female')], 'Gender', size=254),
              't_address':fields.char('Address', size=254, required=False),
              't_city_name':fields.char('City', size=254, required=False),
              't_state_name':fields.char('State', size=254, required=False),
              't_country':fields.char('Country', size=254, required=False),
              't_zipcode':fields.char('Zipcode', size=254, required=False),
              't_m_no':fields.char('Mobile', size=254, required=False),
              't_email':fields.char('Email', size=254, required=False),
              't_id_type':fields.selection([('pan','Pan Card'),('passport','Passport')], 'ID Type', required=False),
              't_id_num':fields.char('ID Number', size=254, required=False),
                }
  _defaults = {
                'traveller_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'traveller.details'),

                  }
traveller_details()

class travel_stay_line(osv.osv):
  _name = "travel.stay.line"
  _description = "This table contains the Stay itinerary."
  _columns = {
              'stay':fields.many2one('travel.booking'),
              'stay_id':fields.many2one('travel.stay', 'Stay Id', size=254, required=True),
              'city':fields.many2one('city', 'City Name'),
              'day_seq': fields.char('Day Sequence'),              
		          'desc':fields.text('Description', size=250),
              'hotel_lines':fields.one2many('booking.hotel.room', 'hotel', 'Hotel Lines'),
              'invoice_lines': fields.many2many('account.invoice.line', 'product_line_invoice_rel', 'stay_id', 'invoice_id', 'Invoice Lines', readonly=True),
              'invoiced': fields.boolean('Invoiced', readonly=True),
              }
  _defaults = {
              'invoiced': lambda *a: 0,              
              }
  def on_change_stay(self, cr, uid, ids, stay_id, context=None):
      vals = {}
      if stay_id:
        sl = self.pool.get('travel.stay').browse(cr, uid, stay_id, context=context)
        vals = {
                'city':sl.city_name.id,
                'day_seq':sl.day_seq,
                'desc':sl.desc,
              }
      return {'value' : vals}
travel_stay_line()

class booking_hotel_room(osv.osv):
    
    def _get_db(self, cr, uid, ids, _fieldname, _args, context=None):
        result = dict.fromkeys(ids, '')
        data = cr.dbname
        for this in self.browse(cr, uid, ids, context=context):
            result[this.id] = data
        return result

    _name="booking.hotel.room"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description="Table contains the list of the regions of the travel agent."
    _columns={ 
          'hotel':fields.many2one('travel.stay.line', readonly=True), 
          'hotel_id':fields.many2one('stay.travel.hotel','Hotel Id',size=254,required=True),
          'hotel_name':fields.many2one('res.partner','Hotel Name',required=True, size=254),
          'city_name':fields.many2one('city', 'City Name',size=254),
          'address':fields.char('address',size=254),
          'stars':fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7')],'Stars'),
          'dt': fields.function(_get_db, type='char', string='Database'),
          'room':fields.many2one('hotel.room'),
          'room_lines':fields.one2many('room.type','roomtype_id',required=True, help="Room Types in a Hotel"),
          'meal_lines':fields.one2many('meal','mealtype_id',required=True, help="meals provided in hotels"),
          'amenity_lines': fields.one2many('amenities', 'amenity_id',required=True, help="Amenity details."),
          'state':fields.selection([('open','Open'),('requested','Requested'),('confirmed','Confirmed'),('finalized','Finalized'),('cancel','Cancelled')],'State', readonly=True),
           }
    _defaults = {                  
                  'state':'open',
                }

    def on_change_hotel(self, cr, uid, ids, hotel_id, context=None):
      vals = {}
      if hotel_id:
        sl = self.pool.get('travel.hotel.room').browse(cr, uid, hotel_id, context=context)
        vals = {
                'hotel_name':sl.bill_contact.id,
                'city_name':sl.city_name.id,
                'address':sl.address,
                'stars':sl.stars,
              }
      return {'value' : vals}

    def send_mail(self,cr,uid,ids=False, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'travel_booking', 'email_template_edi_booking_hotel_room')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'booking.hotel.room',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        self.write(cr, uid, ids, {'state':'requested'})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def button_confirm(self,cr,uid,ids=False, context=None):
          self.write(cr, uid, ids, {'state':'confirmed'})

    def create_purchase_order(self, cr, uid, ids, context=None):
      for booking in self.browse(cr, uid, ids, context=context):
          for line in booking.room_lines:
            for li in booking.amenity_lines:
              for l in booking.meal_lines: 
                  po = self.pool.get('purchase.order').create(cr, uid, {
                                                                'partner_id':booking.hotel_name and booking.hotel_name.id,
                                                                'origin':booking.hotel_id,
                                                                'pricelist_id':booking.hotel_name.property_product_pricelist_purchase.id,
                                                                'currency_id':booking.hotel_name.property_product_pricelist_purchase.currency_id.id,
                                                                'order_line':[(0,0,{ 'product_id':line.roomtype_name.roomtype_name.roomtype_name and line.roomtype_name.roomtype_name.roomtype_name.id,
                                                                                     'name':line.roomtype_name.roomtype_name.roomtype_name and line.roomtype_name.roomtype_name.roomtype_name.id,
                                                                                     'price_unit':line['price'],
                                                                                     'product_uom':line.roomtype_name.roomtype_name.roomtype_name.product_tmpl_id.uom_id.id, 
                                                                                    }),
                                                                              (0,0,{'product_id':li.amenity_name.amenity_name.amenity_name and li.amenity_name.amenity_name.amenity_name.id,
                                                                                    'name':li.amenity_name.amenity_name.amenity_name and li.amenity_name.amenity_name.amenity_name.id,
                                                                                    'price_unit':li['amount'],
                                                                                    'product_uom':li.amenity_name.amenity_name.amenity_name.product_tmpl_id.uom_id.id,
                                                                                }),
                                                                              (0,0,{'product_id':l.mealtype_name.mealtype_name.mealtype_name and l.mealtype_name.mealtype_name.mealtype_name.id,
                                                                                    'name':l.mealtype_name.mealtype_name.mealtype_name and l.mealtype_name.mealtype_name.mealtype_name.id,
                                                                                    'price_unit':l['price_unit'],
                                                                                    'product_uom':l.mealtype_name.mealtype_name.mealtype_name.product_tmpl_id.uom_id.id,
                                                                                })],
                                                                }, context=context)
          self.write(cr, uid, ids, {'state':'finalized'})
      return True

booking_hotel_room()

class room_type(osv.osv):
      _name="room.type"
      _description="contains the list of room types in the Hotel."
      _columns={
                'roomtype_id':fields.many2one('booking.hotel.room', 'Room Type Id'),
                'roomtype_name':fields.many2one('hotel.room', 'Room Type Name', required=True, size=254),
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
room_type()

class amenities(osv.osv):
  _name="amenities"
  _description="Amenities Provided in the Hotel Room."
  _columns={
            'amenity_id':fields.many2one('booking.hotel.room', 'Amenity Id'),
            'amenity_name':fields.many2one('hotel.amenity', 'Amenity Name', size=254, required=True),
            'description':fields.text('Description',size=254, required=True),
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
amenities()

class meal(osv.osv):
      _name="meal"
      _description="List of Meals provided in the Hotel."
      _columns={
                'mealtype_id':fields.many2one('booking.hotel.room', 'Meal Type Id'),
                'mealtype_name':fields.many2one('hotel.meal', 'Meal Type Name', size=254, required=True),
                'price_unit':fields.float('Price', size=254, required=True),
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
meal()

class travel_line(osv.osv):
  _name = "travel.line"
  _description = "This table contains the travel itinerary."
  _columns = {
              'itinerary_id':fields.many2one('travel.booking', readonly=True),
              'travel_id':fields.many2one('travel.itenary', 'Travel Id', size=60),
              'mode':fields.many2one('incitytravel.mode', 'Travel Mode', size=60, required=True),
              'source':fields.many2one('city', 'Source City', size=60, required=True),
              'day_seq': fields.selection([('day1','Day-1'),('day2','Day-2'),('day3','Day-3'),('day4','Day-4'),('day5','Day-5'),('day6','Day-6'),('day7','Day-7'),('day8','Day-8'),('day9','Day-9'),('day10','Day-10')],'Day Sequence',required=True),
		          'destination':fields.many2one('city', 'Destination City', size=60, required=True),
              'price':fields.float('Price', size=20, required=True),
		          'invoice_lines': fields.many2many('account.invoice.line', 'travel_line_invoice_rel', 'travel_id', 'invoice_id', 'Invoice Lines', readonly=True),
              'invoiced': fields.boolean('Invoiced', readonly=True),
            }
  _defaults = {
                'invoiced': lambda *a: 0,
              }
  def on_change_travel(self, cr, uid, ids, travel_id, context=None):
      vals = {}
      if travel_id:
        sl = self.pool.get('travel.itenary').browse(cr, uid, travel_id, context=context)
        vals = {
                'mode':sl.tm_name.id,
                'source':sl.s_city.id,
                'destination':sl.d_city.id,
                'day_seq':sl.day_seq,
                'price':sl.price,
              }
      return {'value' : vals}

travel_line()