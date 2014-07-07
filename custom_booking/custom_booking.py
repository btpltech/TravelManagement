# -*- coding: utf-*-
import datetime
import time
from osv import fields, osv
from openerp import sql_db, tools
from openerp.tools.translate import _

class custom_booking(osv.osv):
  
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

  def _get_db(self, cr, uid, ids, _fieldname, _args, context=None):
        result = dict.fromkeys(ids, '')
        data = cr.dbname
        for this in self.browse(cr, uid, ids, context=context):
            result[this.id] = data
        return result

  _name = "custom.booking"
  _description = "Table contains the bookin details."
  _inherit = ['mail.thread', 'ir.needaction_mixin']
  _columns = {
              'date':fields.datetime('Booking Date', required=True, readonly=True, states={'New': [('readonly', False)]}),
              'start_date':fields.datetime('Start Date', required=False, readonly=True, states={'New': [('readonly', False)]}),
              'end_date':fields.datetime('End Date', required=False, readonly=True, states={'New': [('readonly', False)]}),
              'state':fields.selection([('New','New'),('open','Open'),('confirm','Confirmed'),('cancel','Cancelled'),('invoiced','Invoiced')], 'Status', readonly=True, select=True),
              'advance_amount':fields.float('Discount', size=254, readonly=True, states={'New': [('readonly', False)]}),
              'amount_total':fields.float('Price', size=254, readonly=True, states={'New': [('readonly', False)]}),
              'amount_balance': fields.function(_amount_bal, string='Total Amount', multi='sums'), 
              
              'dt': fields.function(_get_db, type='char', string='Database'),
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

              'package_id':fields.many2one('travel.custompackage', 'Package Id', size=60, required=True),
              'package_name':fields.char('Package Name', size=254, required=False, readonly=True, states={'New': [('readonly', False)]}),
              'adults':fields.char('Adults', required=False, readonly=True, states={'New': [('readonly', False)]}),
              'child':fields.char('Children', readonly=True, states={'New': [('readonly', False)]}),
              'traveller_line':fields.one2many('custom.traveller.details', 'traveller', readonly=True, states={'New': [('readonly', False)]}),
              'hotel_line':fields.one2many('custom.hotel.line','hotelstay', readonly=True, states={'New': [('readonly', False)], 'open': [('readonly', False)]}),
              'intercity_lines': fields.one2many('book.tranportation', 'intercity', readonly=True, states={'New': [('readonly', False)], 'open': [('readonly', False)]}, help=" Intercity Travel Itenary Details."),
              'intracity_lines': fields.one2many('book.intracity.travel', 'intracity', readonly=True, states={'New': [('readonly', False)], 'open': [('readonly', False)]}, help="Intracity Travel Itenary Details."),
            
              'invoice_ids': fields.many2many('account.invoice', 'custom_booking_invoice_rel', 'order_id', 'book_no', 'Invoices'),
              'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position'),
              'payment_term_id': fields.many2one('account.payment.term', 'Payment Term'),
              'invoiced': fields.function(_invoiced, string='Paid', type='boolean'),
            }
  _defaults = {
                'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
                'state': 'New',
                'invoiced': 0,
              }

  def on_change_package(self, cr, uid, ids, package_id, context=None):
        result = {}
        values = {}
        if package_id:
          partner = self.pool.get('travel.custompackage').browse(cr, uid, package_id, context=context)
          values = {
                    'package_name' : partner.package_name,
                    'adults' : partner.no_adults,
                    'child' : partner.no_children,
                    }          
        return {'value' : values}

  def send_quotation(self,cr,uid,ids=False, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'custom_booking', 'email_template_edi_custom_booking')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'custom.booking',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        self.write(cr, uid, ids, {'state':'open'})
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
                    _('Define sale journal for this company.'))
            account_id = order.customer_name.property_account_receivable.id
            if not account_id:
                raise osv.except_osv(_('Error!'),
                    _('Define account id for this customer.'))

            # get invoice data and create invoice
            inv_data = {
                'name': order.package_name,
                'reference': order.customer_name.ref,
                'account_id': order.customer_name.property_account_receivable.id,
                'type': 'out_invoice',
                'partner_id': order.customer_name.id,
                'journal_id': len(journal_ids) and journal_ids[0] or False,
                'origin': order.package_id.id,
                'fiscal_position': False,
                'payment_term': False,
                'company_id': order.customer_name.company_id.id,
                'amount_untaxed':order.amount_balance,
                'amount_total':order.amount_balance,
                'residual':order.amount_balance,
            }
            inv_id = inv_obj.create(cr, uid, inv_data, context=context)

            # Link this new invoice to related purchase order
            order.write({'invoice_ids': [(4, inv_id)], 'state':'invoiced'}, context=context)
            res = inv_id
        return res

  def confirm_button(self, cr, uid, ids=False, context=None):
          self.write(cr, uid, ids, {'state':'confirm'})

  def cancel_booking(self, cr, uid, ids=False, context=None):
          self.write(cr, uid, ids, {'state':'cancel'})

  def button_dummy(self, cr, uid, ids, context=None):
        return True

custom_booking()

class custom_traveller_details(osv.osv):
  _name = "custom.traveller.details"
  _description = "Table contains travellers information"
  _columns = {
              'traveller':fields.many2one('custom.booking', readonly=True),
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
custom_traveller_details()

class custom_hotel_line(osv.osv):
    def _get_db(self, cr, uid, ids, _fieldname, _args, context=None):
        result = dict.fromkeys(ids, '')
        data = cr.dbname
        for this in self.browse(cr, uid, ids, context=context):
            result[this.id] = data
        return result

    _name="custom.hotel.line"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description="List of hotels chosen by customer."
    _columns={
                  'hotelstay':fields.many2one('custom.booking',readonly=True),
                  'hotel_id':fields.many2one('custom.hotel', 'Hotel Id', required=True),
                  'checkin':fields.datetime('Check-in Date', required=True),
                  'checkout':fields.datetime('Check-out Date', required=True),
                  'no_night':fields.selection([('1','1'),('2','2'),('3','3'),('4','4')],'Nights',required=True),
                  'city':fields.char('City',size=254, required=True),
                  'dt': fields.function(_get_db, type='char', string='Database'),
                  'hotel':fields.many2one('res.partner', 'Hotel Name', size=254, required=True),
                  'room':fields.many2one('custom.room'),
                  'room_lines':fields.one2many('custom.booking.room','roomtype_id',required=True, help="Room Types in a Hotel"),
                  'meal_lines':fields.one2many('custom.booking.meal','mealtype_id',required=True, help="meals provided in hotels"),
                  'amenity_lines': fields.one2many('custom.booking.amenities', 'amenity_id',required=True, help="Amenity details."),
                  'state':fields.selection([('open','Open'),('requested','Requested'),('confirmed','Confirmed'),('finalized','Finalized'),('cancel','Cancelled')],'State', readonly=True),
                  }
    _defaults = {                  
                    'state':'open',
                    }  
    def send_mail(self,cr,uid,ids=False, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'custom_booking', 'email_template_edi_custom_hotel')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'custom.hotel.line',
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
                                                                'partner_id':booking.hotel and booking.hotel.id,
                                                                'pricelist_id':booking.hotel.property_product_pricelist_purchase.id,
                                                                'currency_id':booking.hotel.property_product_pricelist_purchase.currency_id.id,
                                                                'order_line':[(0,0,{ 'product_id':line.roomtype_name.roomtype_name and line.roomtype_name.roomtype_name.id,
                                                                                     'name':line.roomtype_name.roomtype_name and line.roomtype_name.roomtype_name.id,
                                                                                     'price_unit':line.price or 0.00,
                                                                                     'product_uom':line.roomtype_name.roomtype_name.product_tmpl_id.uom_id.id, 
                                                                                    }),
                                                                              (0,0,{'product_id':li.amenity_name.amenity_name and li.amenity_name.amenity_name.id,
                                                                                    'name':li.amenity_name.amenity_name and li.amenity_name.amenity_name.id,
                                                                                    'price_unit':li.amount or 0.00,
                                                                                    'product_uom':li.amenity_name.amenity_name.product_tmpl_id.uom_id.id,
                                                                                }),
                                                                              (0,0,{'product_id':l.mealtype_name.mealtype_name and l.mealtype_name.mealtype_name.id,
                                                                                    'name':l.mealtype_name.mealtype_name and l.mealtype_name.mealtype_name.id,
                                                                                    'price_unit':l.price_unit or 0.00,
                                                                                    'product_uom':l.mealtype_name.mealtype_name.product_tmpl_id.uom_id.id,
                                                                                })],
                                                                }, context=context)
          self.write(cr, uid, ids, {'state':'finalized'})
      return True
    
    def on_change_hotel(self, cr, uid, ids, hotel_id, context=None):
      vals = {}
      if hotel_id:
        sl = self.pool.get('custom.hotel').browse(cr, uid, hotel_id, context=context)
        vals = {
                'checkin':sl.checkin,
                'checkout':sl.checkout,
                'no_night':sl.no_night,
                'city':sl.city,
                'hotel':sl.hotel.id,
              }
      return {'value' : vals}

custom_hotel_line()

class custom_booking_room(osv.osv):
      _name="custom.booking.room"
      _description="contains the list of room types in the Hotel."
      _columns={
                'roomtype_id':fields.many2one('custom.hotel.line', 'Room Type Id'),
                'roomtype_name':fields.many2one('custom.room', 'Room Type Name', required=True, size=254),
                'price':fields.float('Price'),
                }
custom_booking_room()

class custom_booking_amenities(osv.osv):
  _name="custom.booking.amenities"
  _description="Amenities Provided in the Hotel Room."
  _columns={
            'amenity_id':fields.many2one('custom.hotel.line', 'Amenity Id'),
            'amenity_name':fields.many2one('custom.amenities', 'Amenity Name', size=254, required=True),
            'description':fields.text('Description',size=254),
            'amount':fields.float('Price'),
            }
  def on_change_amenity(self, cr, uid, ids, amenity_name, context=None):
        result = {}
        values = {}
        if amenity_name:
          partner = self.pool.get('custom.amenities').browse(cr, uid, amenity_name, context=context)
          values = {
                    'description':partner.description,
                    }          
        return {'value' : values}
custom_booking_amenities()

class custom_booking_meal(osv.osv):
      _name="custom.booking.meal"
      _description="List of Meals provided in the Hotel."
      _columns={
                'mealtype_id':fields.many2one('custom.hotel.line', 'Meal Type Id'),
                'mealtype_name':fields.many2one('custom.meal', 'Meal Type Name', size=254, required=True),
                'price_unit':fields.float('Price'),
                }
custom_booking_meal()

class book_tranportation(osv.osv):
    _name="book.tranportation"
    _description="List contains the Intercity Transport Medium."
    _columns={
              'intercity':fields.many2one('custom.booking', readonly=True),
              'travel_id':fields.many2one('tranportation', 'Travel Id', size=254, required=True),
              'tm_name':fields.char('Travel Mode Name',size=254, required=True),
              's_city':fields.char('Source City',size=254, required=True),
              'd_city':fields.char('Destnation City',size=254, required=True),
              }
    def on_change_trans(self, cr, uid, ids, travel_id, context=None):
      vals = {}
      if travel_id:
        sl = self.pool.get('tranportation').browse(cr, uid, travel_id, context=context)
        vals = {
                'tm_name':sl.tm_name,
                's_city':sl.s_city,
                'd_city':sl.d_city,
              }
      return {'value' : vals}

book_tranportation()

class book_intracity_travel(osv.osv):
    _name="book.intracity.travel"
    _description="List of Intracity Travel Mode."
    _columns={
             'intracity':fields.many2one('custom.booking', readonly=True),
             'tm_name':fields.many2one('intracity.travel', 'Travel Mode Name', size=254, required=True), 
             'city':fields.char('City',size=254, required= True), 
            }
    def on_change_travel(self, cr, uid, ids, tm_name, context=None):
      vals = {}
      if tm_name:
        sl = self.pool.get('intracity.travel').browse(cr, uid, tm_name, context=context)
        vals = {
                'city':sl.city,
              }
      return {'value' : vals}
book_intracity_travel()      