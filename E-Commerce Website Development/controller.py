'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from bottle import route, get, post, error, request,response, static_file
import os
import model 
from sql import SQLDatabase
my_database = SQLDatabase("Credential.json")
my_database.add_user("admin",'password',1)
forum_title = []
forum_message = []
path = 'templates/forum'

files = os.listdir(path)
for items in files:
    if "title.txt" in items:
        forum_title.append(items)
    if "message.txt" in items:
        forum_message.append(items)


#-----------------------------------------------------------------------------
# Static file paths 
#-----------------------------------------------------------------------------

# Allow image loading
@route('/img/<picture:path>')
def serve_pictures(picture):
    '''
        serve_pictures

        Serves images from static/img/

        :: picture :: A path to the requested picture

        Returns a static file object containing the requested picture
    '''
    return static_file(picture, root='static/img/')

#-----------------------------------------------------------------------------

# Allow CSS
@route('/css/<css:path>')
def serve_css(css):
    '''
        serve_css

        Serves css from static/css/

        :: css :: A path to the requested css

        Returns a static file object containing the requested css
    '''
    return static_file(css, root='static/css/')

#-----------------------------------------------------------------------------

# Allow javascript
@route('/js/<js:path>')
def serve_js(js):
    '''
        serve_js

        Serves js from static/js/

        :: js :: A path to the requested javascript

        Returns a static file object containing the requested javascript
    '''
    return static_file(js, root='static/js/')

#-----------------------------------------------------------------------------
# Pages
#-----------------------------------------------------------------------------

# Redirect to login
@get('/')

@get('/home')
def get_index():
    '''
        get_index
        
        Serves the index page
    '''
    my_database.log_out()
   
    return model.index()

#-----------------------------------------------------------------------------
@get('/Chinese_homepage')
def get_index():

   
    return model.page_view("Chinese_homepage")
# Display the login page
@get('/login')
def get_login_controller():
    '''
        get_login
        
        Serves the login page
    '''
    my_database.log_out()
    return model.login_form()

#-----------------------------------------------------------------------------

# Attempt the login
@post('/login')
def post_login():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''
    
    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    
    # Call the appropriate method
    return model.login_check(username, password)

#-----------------------------------------------------------------------------


@get("/admin")
def get_admin():
    return model.page_view.load_and_render("adminpage")
@post("/admin")
def post_admin():
    mute_user = request.forms.get('mute_user')
    post = request.forms.get('post')
    username = request.forms.get("username")
   
    if post != "":
        post_title =post+"title.txt"
        post_message = post+"message.txt" 
        if post_title not in forum_title:
           return model.page_view("redirect",url="http://localhost:8081/Cannot_delete_post_error") 
        os.remove(f"templates/forum/{post_title}")
        os.remove(f"templates/forum/{post_message}")
        
    elif mute_user!="":
        my_database.mute_user(mute_user)
        if my_database.check_username(mute_user)== False:
            return model.page_view("redirect",url="http://localhost:8081/Cannot_mute_user_error")
    elif username!= "":
        my_database.remove_user(username)
        if my_database.check_username(mute_user)== False:
            return model.page_view("redirect",url="http://localhost:8081/Cannot_delete_user_error")
    return model.page_view("adminpage")
    
@get('/register')
def get_register_controller():
    '''
        get_login
        
        Serves the login page
    '''
    my_database.log_out()
    return model.register_form()

#-----------------------------------------------------------------------------
# Redirect to login


@post('/register')
def post_register():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''
    
    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    print(username,password)
    
    # Call the appropriate method
    return model.register_check(username, password)



   
        
@get ('/userPage')
def personal_page():
    


    return model.page_view("userPage", Username = "Richard Song")
    
    #-----------------------------------------------------------------------------
@post ('userPage')
def personal_page():
    
    
    return model.page_view("redirect")

@get('/about')
def get_about():
    '''
        get_about
        
        Serves the about page
    '''
    
    return model.about()


# Display the product page (GET request)
# Display the product page (GET request)
# Display the product page (GET request)
@get('/product')
    # Product data
def get_product_page():   
    products = my_database.show_all_products()
    print (products)
    # Read the HTML content from the two template files
    with open('templates/product_page_start.html', 'r', encoding='utf-8') as start_file:
        start_html = start_file.read()

    with open('templates/product_page_end.html', 'r', encoding='utf-8') as end_file:
        end_html = end_file.read()

    # Generate the product list content
    product_list_html = ""
    for index, product in enumerate(products):
        product_name, product_description, product_price, product_image = product
        product_list_html += f"""
        <li>
            <img src="{product_image}" alt="{product_name}" width="100" height="100">
            <strong>Product Name:</strong> {product_name}
            <strong>Product Description:</strong> {product_description}
            <strong>Product Price:</strong> ${product_price}
            <input type="radio" name="selected_product" id="product{index}" value="{product_name}" data-price="{product_price}" required>
            <label for="quantity{index}">Quantity:</label>
            <input type="number" id="quantity{index}" name="quantity{index}" value="0" min="0">
        </li>
        """

    # Combine the HTML parts and the product list
    final_html = start_html + product_list_html + end_html

    # Write final_html to product.html
    with open('templates/product.html', 'w', encoding='utf-8') as product_file:
        product_file.write(final_html)

    # Render the product.html file
    return model.page_view("product")
@post('/product')
def post_product_page():
    products = my_database.show_all_products()

    selected_product_name = request.forms.get('selected_product')
    selected_product_index = next((index for index, product in enumerate(products) if product[0] == selected_product_name), None)

    # Handle the case where the product name is not found
    if selected_product_index is None:
        print("Error: Product not found")
        return get_product_page()

    # Retrieve the corresponding quantity
    product_quantity = request.forms.get(f'quantity{selected_product_index}')
    
    if my_database.login_status()=='':
        return model.page_view("redirect",url="http://localhost:8081/login")
    # Print the selected product name and quantity to the console
    else:
        my_database.add_cart(my_database.login_status(),selected_product_name,product_quantity)

        return model.page_view("redirect",url="http://localhost:8081/product") 
#-----------------------------------------------------------------------------

# Help with debugging
@post('/debug/<cmd:path>')
def post_debug(cmd):
    
    return model.debug(cmd)

#-----------------------------------------------------------------------------

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error): 
    
    return model.handle_errors(error)


@get('/Login_error')
def Login_error():

    
    return model.page_view("Login_error")


@get('/productpage')
def productpage():

    return model.about()


@get('/Register_error')
def Sign_in_error():

    
    return model.page_view("Register_error")

