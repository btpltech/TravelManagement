{
"name":'Custom Package Booking Module',
"version":'0.0.8',
"category":'Tools',
"complexity":"easy",
"description":"""Book Your Travel Package Here""",
"author":'Madhav Agarwal',
"website":'http://www.traveloore.com/',
"depends":['travel_package','account','purchase'],
"init_xml":[],
"data":['edi/custom_hotel_line_action_data.xml',
        'edi/custom_booking_action_data.xml',
        'custom_booking_workflow.xml',
        'custom_booking_view.xml'],
"demo_xml":[],
"installable":True,
"auto_install":True,
}