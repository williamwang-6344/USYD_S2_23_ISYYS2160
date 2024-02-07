import pandas as pd
import json
import hashlib
import numpy as np
import psycopg2
import psycopg2.extras
import json
import math
from sqlalchemy import create_engine
from sqlalchemy import text
import uuid
from cryptography.fernet import Fernet
# This class is a simple handler for all of our SQL database actions
# Practicing a good separation of concerns, we should only ever call 
# These functions from our models

# If you notice anything out of place here, consider it to your advantage and don't spoil the surprise
def hash_password (password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt
# ---------------------------------------------------------------------------------------------------------
def pgconnect(credential_filepath, db_schema="public"):
    with open(credential_filepath) as f:
        db_conn_dict = json.load(f)
        host       = db_conn_dict['host']
        db_user    = db_conn_dict['user']
        db_pw      = db_conn_dict['password']
        default_db = db_conn_dict['database']
        try:
            db = create_engine('postgresql+psycopg2://'+db_user+':'+db_pw+'@'+host+'/'+default_db, echo=False)
            conn = db.connect()
            print('Connected successfully.')
        except Exception as e:
            print("Unable to connect to the database.")
            print(e)
            db, conn = None, None
        return db,conn
#--------------------------------------------------------------------------------------------------------- 
def clean_sentense(sentence):
    answer=''
    
    new = sentence.split("'")
    for items in new:
        answer += items + "''"
    return answer.strip("''")
# -------------------------------------------------------------------------
class SQLDatabase():

    # Get the database running
    def __init__(self, credential_file_path):
       self.db, self.conn = pgconnect(credential_file_path)
       self.conn.execute(text("""drop schema if exists Shop cascade;
                              create schema if not exists Shop;
                              set search_path to Shop;  
                              drop table  if exists users;
                              create table users(
                                username TEXT primary key,
                                password TEXT,
                                admin INTEGER DEFAULT 0,
                                login_status INTEGER DEFAULT 0); 
                             
                               drop table if  exists products cascade;
                              create table products (name TEXT , 
                                description TEXT DEFAULT 'NO' , 
                                price NUMERIC, 
                                images TEXT,
                                primary key (name) ); 
                              
                              drop table  if exists cart cascade;
                              create table cart (username TEXT,
                                product TEXT , 
                                quantity INT ,
                                price Numeric,
                                paid INT,
                                primary key(username,product),
                                foreign key (username) references users(username)  on delete cascade,
                                foreign key (product) references products(name) on delete cascade
                              
                              
                              );
                              drop table  if exists hist cascade;
                                create table hist (id int primary key,username TEXT, 
                                product TEXT , 
                                quantity INT ,
                                price numeric,
                                complete int default 0,
                                foreign key (username) references users(username)  on delete cascade,
                                foreign key (product) references products(name) on delete cascade
                                
                              
                              );
                              
                              INSERT INTO products      VALUES('Rich Dad Poor Dad', '2017 marks 20 years since Robert Kiyosaki''s Rich Dad Poor Dad first made waves in the Personal Finance arena. It has since become the #1 Personal Finance book of all time... translated into dozens of languages and sold around the world.Rich Dad Poor Dad is Robert''s story of growing up with two dads — his real father and the father of his best friend, his rich dad— and the ways in which both men shaped his thoughts about money and investing. The book explodes the myth that you need to earn a high income to be rich and explains the difference between working for money and having your money work for you.', 11.99 ,'https://m.media-amazon.com/images/I/81bsw6fnUiL._SY522_.jpg');
                              
                              
""")) 
       self.conn.commit()
      

    def query( self,sqlcmd, args=None, df=True):
        result = pd.DataFrame() if df else None
        try:
            if df:
                result = pd.read_sql_query(text(sqlcmd), self.conn, params=args)
            else:
                result = self.conn.execute(text(sqlcmd), args).fetchall()
                result = result[0] if len(result) == 1 else result
        except Exception as e:
            print('Error encountered'+e)
            
        return result
    
    def execute(self,sqlcmd,args=None, df=True):
        try:
            if df:
                self.conn.execute(text(sqlcmd))
                self.conn.commit()
                return True
        except Exception as e:
           print("Error encountered: " +e)
           return False 

            
# ----------------------------------------------------------------------------------------------------------------------------------
            
        
    
    def add_user(self,username,password,admin=0,login_status=0):
        try:
            if self.check_username (username) == False:
                hashed_password = hash_password(password)
                
                # find number of rows in df
                
                return self.execute(f"""INSERT INTO Users
                        VALUES( '{username}', '{hashed_password}', {admin} ,  {login_status})""")
            else:
                return False
        except  Exception:
            print('Error encountered')
    
    def check_username(self,username):
        if self.query(f"SELECT username From users where username = '{username}'").shape[0] ==0:
            return False
        else:
            return True
    def check_admin(self,username):
        return self.query(f"SELECT admin From users where username = '{username}' and admin=1").shape[0] ==1
    
    def login_check(self,username,password):
        if self.check_username(username) == True:
            hashed_password = (self.query(f"""
                    SELECT password
                    FROM Users
                    WHERE username = '{username}' 
                """).iloc[0,0] )
            hased_stored_password, salt = hashed_password.split(':')
            hased_user_input_password = hashlib.sha256(salt.encode() + password.encode()).hexdigest()
            if hased_stored_password == hased_user_input_password:
                self.log_in(username)
                return True
            else:

                return False
            # self.conn.execute()
    def log_out(self):
        self.execute(f""" UPDATE Users SET login_status = 0 
""")  
    def log_in(self,username):
        self.execute(f""" UPDATE Users SET login_status = 1 where  username = '{username}'
""") 
    def login_status(self):
        if self.query(f"select username from users where login_status =1").shape[0] ==1:
            
            return self.query(f"select username from users where  login_status =1").values.tolist()[0][0]
        else:
            return ''
#----------------------------------------------------------------------------------------------------------- 
    def check_products(self,name):
        if self.query(f"SELECT name From products where name = '{name}'").shape[0] ==0:
            return False
        else:
            return True
    def add_products(self,name,price, images='data:image/png;base64,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',description ="NO"):
        try:

            if self.check_products (name) == False:
                return self.execute(f"""INSERT INTO products
                        VALUES('{name}', '{description}', {price}, '{images}' )""")
            else:
                return  False
        except Exception:
            print('Error')
    def modify_products(self, old_name, name, price, images='data:image/png;base64,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', description ="NO"):
        if  self.check_products (old_name) == True:
            return self.execute(f""" UPDATE products
                                SET name = '{name}' , price = {price}, images='{images}',description ='{description}'
                                WHERE name = '{old_name}';
""")
        else:
            return False

    
    def delete_products(self,name):
        if self.check_products (name) == True:
            return self.execute(f"""Delete from products
                    where name = '{name}'""")
        else:
            return False
    def show_all_products(self):
    
        return (self.query('Select * from products').values.tolist())

  #--------------------------------------------------------------------------------------------------------------------------------------------- 
    
    def add_cart(self,username,product,quantity,paid=0):
        if self.check_cart(product,username) == False:
                   
            return self.execute(f"""INSERT INTO cart
                    VALUES('{username}', '{product}', {quantity} ,(select p.price from 
                    products p where name = '{product}' ),{paid});
                    delete from cart where quantity=0""")
        else:
            
            return self.execute(f""" UPDATE cart
                                SET quantity = {quantity}+ quantity
                                WHERE username = '{username}' and product ='{product}';
                                delete from cart where quantity=0
                            
""")
    def set_cart(self,username,product,quantity,paid=0):
        if self.check_cart(product,username) == False:
                   
            return self.execute(f"""INSERT INTO cart
                    VALUES('{username}', '{product}', {quantity} ,(select p.price from 
                    products p where name = '{product}' ),{paid});
                    delete from cart where quantity=0""")
        else:
            
            return self.execute(f""" UPDATE cart
                                SET quantity = {quantity} , paid= {paid}
                                WHERE username = '{username}' and product ='{product}';
                                delete from cart where quantity=0""")

 
    
    def check_cart(self,product,username ):
        
        if self.query(f"""SELECT product From cart where product = '{product}' and username = '{username}' and quantity >=0 """).shape[0] ==0:
            return False
        else:
            return True
    
    def show_user_cart(self,username):
        return self.query(f""" Select username,product,quantity,price from cart where username = '{username}' """).values.tolist()
    def sub_total(self,username):
        return self.query(f""" Select sum(quantity*price) from cart where username = '{username}' """).values.tolist()[0][0]
    
    def show_hist(self,username = 'admin'):
        if username!='admin':
            return self.query(f""" Select id ,username,product,quantity,price,
                              price*quantity AS subtotal, complete from hist where username = '{username}' """).values.tolist()
        else:
            return self.query(f""" Select id ,username,product,quantity,price,
                              price*quantity AS subtotal ,complete from hist """).values.tolist()
    def complete_order(self,id):
        if self.query(f""" select complete from hist where id = {id} and complete = 0""").shape[0] ==1:
            return self.execute(f""" update hist set complete =1 where id ={id}
""")
        if self.query(f""" select complete from hist where id = {id} and complete = 1""").shape[0] ==1:
            return self.execute(f""" update hist set complete =0 where id ={id}
""")
        else:
            return False

    def check_paid(self):
        
        if self.query(f"""SELECT product From cart where  paid = 1""").shape[0] ==0:
            return True
        else:
            count =  len(self.query(""" select * from hist""").values.tolist())
            self.execute(f"""INSERT INTO hist (id, username, product, quantity, price)
                     SELECT {count}, username, product, quantity, price FROM cart
                     WHERE paid = 1""")





# a= SQLDatabase("Credential.json")
# #  check login
# print(a.add_user("admin",'password'))
# print(a.login_check('admin','passwor'))
# print(a.login_check('admin','password'))
# print(a.check_username('admin'))
# print (a.check_admin('admin'))
# print(a.log_out())
# print(a.log_in('admin'))
# print(a.login_status())
# print('--------------------------')
# # check 
# print(a.check_products('Rich Dad Poor Dad'))
# print(a.add_products('bS',10,description=clean_sentense("i's's")))
# print(a.modify_products('bS','billy summers',11))
# print(a.show_all_products())
# print(a.delete_products('billy summers'))

# # print('-------------------------------------')

# print(a.add_cart('admin','Rich Dad Poor Dad',10))
# print(a.add_cart('admin','Rich Dad Poor Dad',10))
# print(a.show_user_cart('admin'))

# print(a.sub_total('admin'))
# print(a.set_cart('admin','Rich Dad Poor Dad',10,1))
# print(a.check_paid())
# print(a.show_hist(username = 'admin'))
# print(a.complete_order(0))
# print(a.show_hist(username = 'admin'))
# print(a.query(f""" Select * from users  """).values.tolist())
# print()
# print()
# print()

# print()
# print()
# print()




