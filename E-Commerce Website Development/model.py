'''
    Our Model class
    This should control the actual "logic" of your website
    And nicely abstracts away the program logic from your page loading
    It should exist as a separate layer to any database or data structure that you might be using
    Nothing here should be stateful, if it's stateful let the database handle it
'''
from bottle import response ,request
import view
import random
import hashlib
from sql import SQLDatabase
from flask import Flask
my_database = SQLDatabase("Credential.json")
# my_database.empty_database()

# Initialise our views, all arguments are defaults for the template
page_view = view.View()



#-----------------------------------------------------------------------------
# Index
#-----------------------------------------------------------------------------

def index():
    '''
        index
        Returns the view for the index
    '''
    return page_view.load_template("homepage")

#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''
    return page_view.load_template("login")

#-----------------------------------------------------------------------------

# Check the login credentials
def login_check(username, password):
    '''
        login_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''
    my_database.log_out()
    # By default assume good creds
    if username and password != "":
        
        
        if my_database.login_check(username, password) and username != "admin":
            my_database.log_in(username)
            return page_view("redirect", name=username,url="http://localhost:8081/product", message=username)
        elif my_database.login_check(username, password) and username == "admin":
            my_database.log_in(username)
            return page_view.load_and_render("redirect",url="http://localhost:8081/product")
        else:
            return page_view("redirect", url = "http://localhost:8081/Login_error")
            
            
        
            
    else:
        return  page_view("redirect", url = "http://localhost:8081/Login_error")
        # "Username and password can not be empty"



#-----------------------------------------------------------------------------
# Register
#-----------------------------------------------------------------------------
def create_html_template(username):
    with open (f'templates/{username}.html', "a") as f:
        pass

def friend_message_form(user,friend):
    return page_view(user+"/"+friend)
def user_page(user):
    return page_view(user)
def gen_key_page(username):
    return page_view('/generateKey',url = f"/generateKey/{username}",name=username)
def register_form():
    '''
        login_form
        Returns the view for the login_form
    '''
    return page_view.load_template("register")

#-----------------------------------------------------------------------------

def register_check(username, password): #start of wliima need to change
    '''
        login_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''

    # By default assume good creds
    if username and password != "":
        register = True
        if my_database.check_username(username):
            register = False
            err_str = "User already exists"
        else:
            my_database.add_user(username , password)
        
        if register : 
            create_html_template(username)
            
            
            # with open('templates/generateKey.txt', "w") as f:
            #     f.write(f"{username}")
            
            return page_view("redirect",url="http://localhost:8081/login")
        else :
            
            
           
            return page_view("redirect", url="http://localhost:8081/Register_error")
    else:
        return page_view("redirect" , url="http://localhost:8081/Register_error")




#-----------------------------------------------------------------------------
# About
#-----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''
    return page_view("about", garble=about_garble())


# Returns a random string each time
def about_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.", 
    "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
    "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
    "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
    "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
    "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return garble[random.randint(0, len(garble) - 1)]


#-----------------------------------------------------------------------------
# Debug
#-----------------------------------------------------------------------------

def debug(cmd):
    try:
        return str(eval(cmd))
    except:
        pass


#-----------------------------------------------------------------------------
# 404
# Custom 404 error page
#-----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)






# def print_intented_friend_list(username):
#     my_database.print_intented_friend_list(username) 
    
# def print_real_friend_list(username):

#     my_database.print_real_friend_list(username)  
