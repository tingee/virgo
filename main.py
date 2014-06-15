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
        , "/booking" , "booking"
        , "/personal_page", "personal_page"
        , "/admin", "admin"
        , "/balance", "balance"
        , "/order_commit", "order_commit"
        , "/order_details", "order_details"
        , "/topup_details", "topup_details"
        )

login_form = form.Form(
                  form.Textbox('user_name', description="rtx account")
                  ,form.Password('password')
                  ,form.Button("submit", type="submit", description="submit")
    )

web.config.debug = False
app = web.application(urls, globals())
render = web.template.render('templates/')

session = web.session.Session(app, web.session.DiskStore('sessions'),initializer={'status':0, 'user_id':'','privilege':0}) 
 
'''
register page
'''
class register :
    def GET(self):
        if is_login() :
            raise web.seeother("/personal_page")
        
        form = login_form()
        return render.register(form)
    def POST(self):
        if is_login() :
            raise web.seeother("/personal_page")
        input = web.input()
        user_name = web.net.websafe(input.user_name)
        password = web.net.websafe(input.password)
        
        user_id = 0
        try :
            user_id = db.insert("user_info", user_name=user_name, password = hashlib.md5(password).hexdigest().upper(), balance = 0 )
            print "user_id="+str(user_id)
        except :
            return render.msg( "用户已存在!", "register")
        
        result = db.select('user_info', where="id=%d" % user_id)
        
        if result :
            user_info = result[0]
            session.user_id = user_info.id
            session.privilege = user_info.privilege 
            session.status = 1  
            print "register user_name=" + user_info.user_name
        raise web.seeother("/personal_page")
            
'''
 login page
 '''   
class login:
    def GET(self):
        form = login_form()  
        if not is_login() :
            return render.login(form)
        
        raise web.seeother("/personal_page")
            
    def POST(self):
        if not is_login() :
            input = web.input()
            user_name = web.net.websafe(input.user_name)
            password = web.net.websafe(input.password)
            
            result = identify_user_info(user_name, password) 
            if result :
                user_info = result[0]
                session.user_id = user_info.id
                session.privilege = user_info.privilege 
                session.status = 1  
            
        raise web.seeother("/personal_page")

'''
 logout page
 '''
class logout:
    def GET(self):
        session.stauts = 0
        session.kill() 
        raise web.seeother("/login")

class personal_page:
    def GET(self):
        check_login()
        
        user_info = get_current_user_info()
        return render.personal_page(user_info.user_name, str(user_info.balance), user_info.privilege )
                            
class restaurant_info :
    def GET(self):
        check_login()
        
        return render.restaurant_info( get_restaurant_info() )

    def POST(self):
        check_login()
        
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
        error_msg = []        
        check_login()
                
        input = web.input()
        restaurant_id = web.net.websafe(input.restaurant_id)
        restaurant_name = web.net.websafe(input.restaurant_name)             
        #print 'restaurant_id type=' + str(type(restaurant_id))
        
        dish_info = get_dish_info(restaurant_id)
        if not dish_info :
            error_msg.append( "cannot find dish info!" )
         
        return render.dish_info( restaurant_name, restaurant_id, dish_info,  self.get_user_order_info(session.user_id), error_msg )
        
    def POST(self):
        check_login()
        error_msg = []
      
        
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
        
        raise web.seeother('dish_info?restaurant_id=%s&restaurant_name=%s' % (restaurant_id, restaurant_name ) )
             
#        dish_info = get_dish_info(restaurant_id)
#        if not dish_info :
#            error_msg.append( "cannot find dish info!" )            
#        return render.dish_info( restaurant_name, restaurant_id, dish_info,  get_user_order_info(session.user_id), error_msg )
    def get_user_order_info(self,user_id):
        var = dict(user_id=user_id)
        sqlcmd = '''
         SELECT restaurant_info.id as restaurant_id, restaurant_info.name as restaurant_name, 
                     dish_info.dish_name as dish_name,dish_info.price as price, dish_info.note as note,
                     booking_info.booking_time as time, booking_info.id as booking_id
         FROM booking_info, dish_info, restaurant_info 
         WHERE booking_info.user_id=$user_id 
         AND dish_info.id = booking_info.dish_id
         AND dish_info.restaurant_id=restaurant_info.id
         AND booking_info.status=0
         order by booking_info.booking_time DESC
        '''
        return db.query(sqlcmd,var)
    
class booking :
    def GET(self):
        error_msg = []
        check_login() 
        
        input = web.input()
        restaurant_id = web.net.websafe(input.restaurant_id)    
        restaurant_name = web.net.websafe(input.restaurant_name)
        
        if web.config.booking_status == False :
            return render.msg("the dinner booking is not available right now!" , 'dish_info?restaurant_id=%s&restaurant_name=%s' % (restaurant_id, restaurant_name ) )
        
        action = int( web.net.websafe(input.action) )
        if action is 0 : # means to add a booking/order
            self.add_booking(input)
        
        if action is 1: #means to cancel a booking/order
            if not self.cancel_booking(input) :
                error_msg.append("cannot cancel the order! the order may have been committed or deleted!")        
        
        restaurant_id = web.net.websafe(input.restaurant_id)    
        restaurant_name = web.net.websafe(input.restaurant_name)    
        raise web.seeother('dish_info?restaurant_id=%s&restaurant_name=%s' % (restaurant_id, restaurant_name ) )
    
#        dish_info = get_dish_info(restaurant_id)
#        if not dish_info :
#            error_msg.append("cannot find dish info!")    
#        return render.dish_info( restaurant_name, restaurant_id, dish_info , get_user_order_info(session.user_id), error_msg )
    
    def add_booking(self, input):
        dish_id = web.net.websafe(input.dish_id)
        user_id = session.user_id
        payment = float(web.net.websafe(input.price))
        payment = 0 - abs(payment)    
        
        booking_id = db.insert('booking_info'
                               , dish_id=dish_id
                               , user_id=user_id
                               , payment=payment
                               , booking_time=datetime.datetime.now() )
        print "booking_id="+ str(booking_id)         
        
        
    def cancel_booking(self, input):
        booking_id = web.net.websafe(input.booking_id)
        effect_rows = 0 
        effect_rows += db.delete('booking_info', where="status=0 and id=%s" % (booking_id)  )
        effect_rows += db.delete('transaction_journal', where="transaction_type=1 and associate_id=%s" % (booking_id)  )
        print "effect_rows=" + str(effect_rows)
        return effect_rows == 2 

class order_details:
    def GET(self):
        check_login() 
        input = web.input()
        user_id = web.net.websafe(input.user_id)
        
        return render.order_details( self.get_order_details(user_id))
    
    def get_order_details(self, user_id):
        sqlcmd = '''
        SELECT user_info.user_name as user_name
                    ,restaurant_info.name as restaurant_name
                    ,dish_info.dish_name as dish_name
                    ,booking_info.booking_time as time, booking_info.payment as payment
        FROM user_info ,restaurant_info ,dish_info, booking_info
        WHERE booking_info.user_id=%s
        AND booking_info.user_id=user_info.id
        AND booking_info.dish_id=dish_info.id
        AND dish_info.restaurant_id=restaurant_info.id
        ORDER BY booking_info.booking_time DESC
        ''' % (user_id)
        return db.query(sqlcmd)

class topup_details:
    def GET(self):
        check_login()
        input = web.input()
        user_id = web.net.websafe(input.user_id)
        
        return render.topup_details( self.get_topup_details(user_id) )
     
    def get_topup_details(self, user_id):
        sqlcmd = '''
        SELECT user_info.user_name as user_name
                    ,transaction_journal.transaction_amount as amount, transaction_journal.transaction_time as time
        FROM user_info, transaction_journal
        WHERE transaction_journal.transaction_type=0 
        AND transaction_journal.user_id=user_info.id
        AND transaction_journal.user_id=%s
        ORDER BY transaction_journal.transaction_time DESC
        ''' % (user_id)
        return db.query(sqlcmd)
'''
admin pages
'''
class admin :
    def GET(self):
        check_login()
        check_admin()
        
        return render.admin( db.select('user_info') ) 
                     
class topup :
    def POST(self):
        check_login()
        check_admin()

        input = web.input()
        user_id = web.net.websafe(input.user_id) 
        amount = float(web.net.websafe(input.amount) ) 
        amount = abs(amount)
        
        self.topup_money(user_id, amount)
        
        result = db.select('user_info', where='id='+user_id)[0]
        
        msg = '''dear %s, your balance is %f '''  % (result.user_name, result.balance)
        return render.msg(msg, "admin")
        
    def topup_money(self, user_id, amount):
        var = dict(user_id=user_id, amount=amount)
        topup_id = db.insert('topup_info'
                       , user_id=user_id
                       , payment=amount
                       , topup_time=datetime.datetime.now() )
        print "topup_id=" + str(topup_id)
        
        transaction_id = transaction_record(0, topup_id,user_id,amount)
        print "transaction_id=" + str(transaction_id)
        
        rows = db.query('update user_info set balance=balance+$amount where id=$user_id', var)
        print "effect rows=" + str(rows)   

class balance:
    def GET(self):
        check_login()
        results = db.select('user_info')
        return render.balance( results )
    
class order_commit:
    def GET(self):
        check_login()
        check_admin()
        
        order_summary = self.get_order_table()
        order_detail = self.get_order_detail()
        
        return render.order_commit(order_summary, order_detail, web.config.booking_status)
                
    def POST(self):
        check_login()
        check_admin()
        
        input = web.input()
        if input.get('enable_booking') :
            web.config.booking_status = True    
        elif input.get('disable_booking') :
            web.config.booking_status = False    
        elif input.get('commit_order') :
            self.commit_order()
        else :
            return render.msg("invalid operation!", "order_commit")
    
        raise web.seeother("/order_commit") 
    
    def get_order_table(self):
        sqlcmd = '''
        SELECT restaurant_info.name as  restaurant_name, restaurant_info.phone as restaurant_phone,
        dish_info.dish_name as dish_name, count(dish_info.id) as count
        FROM restaurant_info, dish_info, booking_info
        where booking_info.dish_id=dish_info.id
        AND dish_info.restaurant_id=restaurant_info.id
        AND booking_info.status=0
        GROUP BY dish_info.id, restaurant_info.id
        ORDER BY restaurant_info.id
        '''
        return db.query(sqlcmd)
    
    def get_order_detail(self):
        sqlcmd = '''
        SELECT user_info.user_name as user_name, user_info.id as user_id 
                    ,restaurant_info.name as restaurant_name
                    ,dish_info.dish_name as dish_name, dish_info.price as price
                    ,booking_info.booking_time as booking_time, booking_info.id as booking_id, booking_info.payment as payment   
        FROM restaurant_info, dish_info, booking_info, user_info
        where booking_info.dish_id=dish_info.id
        AND dish_info.restaurant_id=restaurant_info.id
        AND booking_info.user_id=user_info.id
        AND booking_info.status=0
        ORDER BY booking_info.booking_time
        '''
        return db.query(sqlcmd)
       
    def commit_order(self):
        print "commiting oders!"
        order_detail = self.get_order_detail()
        for item in order_detail :
            # insert into transaction_record
            transaction_id = transaction_record(1, item.booking_id, item.user_id, item.payment )
            print "transaction_id =" + str(transaction_id )
            # update balance 
            rows = db.query('update user_info set balance=balance+%f where id=%s' % (item.payment, item.user_id) )   
            print "rows =" + str(rows )
            
        #commit all orders 
        effect_rows = db.update('booking_info', where='status=0', status=1 )
        print "effect_rows="+str(effect_rows)     

                
'''
function 
'''
def is_login() :
    if session.get('status') is None :
        return False 
    print "session.status: " + str(session.status) 
    return session.status == 1 

def check_login():
    if not is_login() :
        raise web.seeother("/login")    
    
def check_admin():
    if session.privilege == 0 :
        raise web.seeother("/personal_page")
        
def identify_user_info(user_name, password) :
    var = dict(user_name=user_name, password = hashlib.md5(password).hexdigest().upper() )
    return db.select('user_info', var, where='user_name=$user_name and password=$password')

def get_current_user_info() :
    var = dict(user_id=session.user_id)
    results = db.select('user_info', var, where='id=$user_id')
    if not results :
        return None
    return results[0]

def get_restaurant_info():
    return db.select('restaurant_info')

def get_dish_info(restaurant_id):
    return db.select('dish_info', where='restaurant_id='+str(restaurant_id) )

def transaction_record(transaction_type, associate_id, user_id, amount, transaction_time = None):
    if not transaction_time :
        transaction_time = datetime.datetime.now() 
        
    return db.insert('transaction_journal'
                     , transaction_type=transaction_type
                     , associate_id=associate_id
                     , user_id=user_id
                     , transaction_amount=amount
                     , transaction_time=transaction_time )

if __name__ == "__main__":
    #web.internalerror = web.debugerror
    web.config.booking_status = False    
    app.run()


