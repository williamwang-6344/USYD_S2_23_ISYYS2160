
from sql import SQLDatabase

database = SQLDatabase("database")

database.empty_database()
database.database_setup()

database.add_user("wwh" , "1234")
# data_base.add_user("wwh2" , "1234")
# data_base.add_friend("wwh" , "wwh2")
database.add_user("wwh3" , "1234")
# print(database.check_credentials("wwh" , "1234"))
# print(database.check_credentials("wwh" , "1234"))
database.add_friend("wwh" , "wwh3")
database.add_friend("wwh3" , "wwh")
print(database.cur.execute("SELECT friend_list From Users").fetchall())
# print(database.check_login_status("wwh"))
# # print(data_base.check_credentials("wwh" , "1234"))

# print(database.print_request_list("wwh3"))
# database.add_friend("wwh3" , "wwh")
print(database.print_request_list("wwh3"))
print(database.print_real_friend_list("wwh"))