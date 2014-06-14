#!/usr/bin/python2.7 
# -*- coding: utf-8 -*-  
'''
Created on 2014年6月14日

@author: ay
'''
import web, hashlib, datetime
from web import form


db = web.database(dbn='mysql', user='root', pw='123', db='launch_booking')

urls = (
        "/", "login"
        ,"/login", "login" 
        , "/register", "register" 
        , "/logout" , "logout"
        , "/restaurant_info" , "restaurant_info"
        , "/topup" , "topup"
        , "/dish_info" , "dish_info"
        , "/restaurant_info" , "restaurant_info"
        , "/booking" , "booking"
        )

login_form = form.Form(
                  form.Textbox('user_name', description="rtx account")
                  ,form.Password('password')
                  ,form.Button("submit", type="submit", description="submit")
    )

web.config.debug = False
app = web.application(urls, globals())
render = web.template.render('templates/')

session = web.session.Session(app, web.session.DiskStore('sessions'),initializer={'is_loggedin':0, 'user_id':'',}) 
 
'''
register page
'''
class register :
    def GET(self):
        if is_login() :
            return "you have logged"
        
        form = login_form()
        return render.register(form)
    def POST(self):
        if is_login() :
            return "you have logged"
        input = web.input()
        user_name = web.net.websafe(input.user_name)
        password = web.net.websafe(input.password)
        
        user_id = 0
        try :
            user_id = db.insert("user_info", user_name=user_name, password = hashlib.md5(password).hexdigest().upper(), balance = 0 )
        except :
            return "用户已存在!"
        
        result = db.select('user_info', where="user_name='%s'" % user_name)
        session.user_id = result[0].id 
        session.status = 1  
        return render.test_show(user_name, hashlib.md5(password).hexdigest().upper() )
            
'''
 login page
 '''   
class login:
    def GET(self):
        form = login_form()  
        if not is_login() :
            return render.login(form)
        
        return render.personal_page()
            
    def POST(self):
        if is_login() :
            return render.personal_page()
        
        input = web.input()
        user_name = web.net.websafe(input.user_name)
        password = web.net.websafe(input.password)
        
        user_info = identify_user_info(user_name, password) 
        if not user_info :
            #password or user name is incorrect
            return "invalid user name or password"
        
        session.user_id = user_info[0].id
        print 'user_id='+str(session.user_id)
        session.status = 1  
        
        return render.personal_page()

'''
 logout page
 '''
class logout:
    def GET(self):
        session.stauts = 0
        session.kill() 
        return "Logout success!"
    
class restaurant_info :
    def GET(self):
        form = login_form()  
        if not is_login() :
            return render.login(form)
        
        return render.restaurant_info( get_restaurant_info() )

    def POST(self):
        form = login_form()  
        if not is_login() :
            return render.login(form)
        
        input = web.input()
        restaurant_name = web.net.websafe(input.restaurant_name)
        restaurant_phone = web.net.websafe(input.restaurant_phone)        
        restaurant_note = web.net.websafe(input.restaurant_note)
                
        try:
            db.insert('restaurant_info', name=restaurant_name , phone=restaurant_phone, note=restaurant_note)
        except:
            return "Fail to add restaurant information, the restaurant name may conflict!"
            
        return render.restaurant_info( get_restaurant_info() )
    
class dish_info :
    def GET(self):
        form = login_form()  
        error_msg = []        
        if not is_login() :
            return render.login(form)
                
        input = web.input()
        restaurant_id = web.net.websafe(input.restaurant_id)
        restaurant_name = web.net.websafe(input.restaurant_name)             
        #print 'restaurant_id type=' + str(type(restaurant_id))
        
        dish_info = get_dish_info(restaurant_id)
        if not dish_info :
            error_msg.append( "cannot find dish info!" )
         
        return render.dish_info( restaurant_name, restaurant_id, dish_info,  get_user_order_info(session.user_id), error_msg )
        
    def POST(self):
        form = login_form()  
        error_msg = []
        if not is_login() :
            return render.login(form)        
        
        input = web.input()
        dish_name = web.net.websafe(input.dish_name)
        dish_price = web.net.websafe(input.dish_price)        
        dish_note = web.net.websafe(input.dish_note)
        restaurant_id = web.net.websafe(input.restaurant_id)
        restaurant_name = web.net.websafe(input.restaurant_name)
                
        try:
            rows = db.insert('dish_info', restaurant_id=restaurant_id, dish_name=dish_name , price=float(dish_price), note=dish_note)
        except:
            error_msg.append( "Fail to add restaurant information, the restaurant name may conflict!" )
                 
        dish_info = get_dish_info(restaurant_id)
        if not dish_info :
            error_msg.append( "cannot find dish info!" )    
            
        return render.dish_info( restaurant_name, restaurant_id, dish_info,  get_user_order_info(session.user_id), error_msg )
    
class booking :
    def GET(self):
        form = login_form()  
        error_msg = []
        if not is_login() :
            return render.login(form)
        
        input = web.input()
        action = int( web.net.websafe(input.action) )
        if action is 0 : # means to add a booking/order
            self.add_booking(input)
        
        if action is 1: #means to cancel a booking/order
            if not self.cancel_booking(input) :
                error_msg.append("cannot cancel the order! the order may have been committed or deleted!")        
        
        restaurant_id = web.net.websafe(input.restaurant_id)    
        restaurant_name = web.net.websafe(input.restaurant_name)    
        dish_info = get_dish_info(restaurant_id)
        if not dish_info :
            error_msg.append("cannot find dish info!")
        
        #print error_msg
        return render.dish_info( restaurant_name, restaurant_id, dish_info , get_user_order_info(session.user_id), error_msg )
    
    def add_booking(self, input):
        dish_id = web.net.websafe(input.dish_id)
        user_id = session.user_id
        payment = web.net.websafe(input.price)    
        
        booking_id = db.insert('booking_info'
                               , dish_id=dish_id
                               , user_id=user_id
                               , payment=payment
                               , booking_time=datetime.datetime.now() )
        print booking_id         
        transaction_record(1, booking_id, user_id, payment)
        
    def cancel_booking(self, input):
        booking_id = web.net.websafe(input.booking_id)
        effect_rows = 0 
        effect_rows += db.delete('booking_info', where="status=0 and id=%s" % (booking_id)  )
        effect_rows += db.delete('transaction_journal', where="transaction_type=1 and associate_id=%s" % (booking_id)  )
        print "effect_rows=" + str(effect_rows)
        return effect_rows == 2 
            
class topup :
    def GET(self):
        form = login_form()  
        if not is_login() :
            return render.login(form)        
        pass
    def POST(self):
        form = login_form()  
        if not is_login() :
            return render.login(form)
                
        pass        

'''
function 
'''
def is_login() :
    if session.get('status') is None :
        return False 
    print "session.status: " + str(session.status) 
    return session.status == 1 

def identify_user_info(user_name, password) :
    var = dict(user_name=user_name, password = hashlib.md5(password).hexdigest().upper() )
    results = db.select('user_info', var, where='user_name=$user_name and password=$password')
    
    return results

def get_restaurant_info():
    return db.select('restaurant_info')

def get_dish_info(restaurant_id):
    return db.select('dish_info', where='restaurant_id='+str(restaurant_id) )

def transaction_record(transaction_type, associate_id, user_id, amount):
    return db.insert('transaction_journal'
                     , transaction_type=transaction_type
                     , associate_id=associate_id
                     , user_id=user_id
                     , transaction_amount=amount
                     , transaction_time=datetime.datetime.now() )

def get_user_order_info(user_id):
    var = dict(user_id=user_id)
    sqlcmd = '''
     SELECT restaurant_info.id as restaurant_id, restaurant_info.name as restaurant_name, 
                 dish_info.dish_name as dish_name,dish_info.price as price, dish_info.note as note,
                 booking_info.booking_time as time, booking_info.id as booking_id
     FROM booking_info, dish_info, restaurant_info 
     WHERE booking_info.user_id=$user_id 
     AND dish_info.id = booking_info.dish_id
     AND dish_info.restaurant_id=restaurant_info.id
     AND DATE(booking_info.booking_time)=DATE(now()) 
     AND booking_info.status=0
     order by booking_info.booking_time DESC
    '''
    return db.query(sqlcmd,var)

if __name__ == "__main__":
    #web.internalerror = web.debugerror
    app.run()


