import unittest
from sql import SQLDatabase
from sql import hash_password
from sql import pgconnect


class TestSQLDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # This method will run once before any of the test methods.
        cls.db = SQLDatabase("Credential.json")
    def test_add_cart(self):
        self.db.add_user('wwh','1234') 
        self.assertTrue(self.db.add_cart('wwh','Rich Dad Poor Dad',10))
        self.assertTrue(self.db.add_cart('wwh','Rich Dad Poor Dad',10))
        self.assertEqual(self.db.show_user_cart('wwh')[0][2],20)
        self.assertTrue(self.db.set_cart('wwh','Rich Dad Poor Dad',0))
        self.assertEqual(self.db.show_user_cart('wwh'),[])
        self.assertTrue(self.db.set_cart('wwh','Rich Dad Poor Dad',10,1))
        self.db.check_paid()
        self.assertEqual(self.db.show_hist("wwh")[0][1],'Rich Dad Poor Dad')
    
    def test_add_user(self):
        
        self.db.add_user('admin','password',1)      
        self.assertEqual(len(self.db.query(f""" Select * from users  """).values.tolist()),2)
        self.assertFalse( self.db.add_user('admin','password',1)  )
        self.assertFalse( self.db.add_user('wwh','1234')  )
        

    def test_check_username(self):
        self.db.check_username('admin')
        self.assertTrue(self.db.check_username('admin'))
        self.assertFalse(self.db.check_username('ad'))
    
    def test_login_check(self):
        self.db.log_in('admin')
        self.assertEqual(self.db.login_status(),'admin')
        self.assertTrue(self.db.check_admin('admin'))
        self.db.log_out()
        self.assertEqual(self.db.login_status(),'')
        self.assertFalse(self.db.login_check('admin','passwor'))
        self.assertTrue(self.db.login_check('admin','password'))
    def test_check_products(self):
        self.assertTrue(self.db.check_products('Rich Dad Poor Dad'))
        self.assertFalse(self.db.check_products('Rich Dad '))
    def test_add_products(self):
        self.assertTrue(self.db.add_products('bS',10))
        self.assertEqual(len(self.db.show_all_products()),2)
        self.assertTrue(self.db.modify_products('bS','billy summers',11))
        self.assertFalse(self.db.modify_products('bS','billy summers',11))
        self.assertEqual(self.db.show_all_products()[1][0],'billy summers')
        self.assertTrue(self.db.delete_products('billy summers'))

        


unittest.main()