"""
Test cases for Supplier Model

"""
import logging
import unittest
from werkzeug.exceptions import NotFound
import os
from service.models import Supplier, Product, Association, DataValidationError, db
from service import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  S U P P L I E R   M O D E L   T E S T   C A S E S
######################################################################
class TestSupplier(unittest.TestCase):
    """ Test Cases for Supplier Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Supplier.init_db(app)

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """ 
        db.session.remove()
        db.drop_all()

    def _create_supplier(self): 
        return Supplier(
            name="Jim Jones",
            address="123 Main Street, Anytown USA", 
            email="jjones@gmail.com", 
            phone_number="800-555-1212",
            available=True, 
            products=[]
        )
    
    def _create_suppliers(self, count):
        """ Method to create suppliers in bulk """
        suppliers = []
        for _ in range(count):
            test_supplier = self._create_supplier()
            suppliers.append(test_supplier)
        return suppliers

    def _create_product(self): 
        return Product(
            name="Macbook"
        )

    def _create_association(self): 
         supplier = self._create_supplier()
         product = self._create_product()
         product.create()
         association = Association(wholesale_price=999)
         association.product = product
         supplier.products.append(association)
         supplier.save()

         return supplier
    
    ######################################################################
    #  S U P P L I E R   T E S T   C A S E S
    ######################################################################
        
    def test_create_a_supplier(self):
        """ Create a Supplier and assert that it exists """
        supplier = self._create_supplier()
        self.assertTrue(supplier != None)
        self.assertEqual(supplier.id, None)
        self.assertEqual(supplier.name, "Jim Jones")
        self.assertEqual(supplier.address, "123 Main Street, Anytown USA")
        self.assertEqual(supplier.email, "jjones@gmail.com")
        self.assertEqual(supplier.phone_number, "800-555-1212")
        self.assertEqual(supplier.available, True) 
        self.assertEqual(supplier.products,[])

    #Test supplier without optional phone number 
        supplier = Supplier(
            name="Jim Jones",
            address="123 Main Street, Anytown USA", 
            email="jjones@gmail.com", 
            available=True 
        )    
        self.assertTrue(supplier != None)
        self.assertEqual(supplier.id, None)
        self.assertEqual(supplier.available, True)
        self.assertEqual(supplier.phone_number, None)  

    def test_add_a_supplier(self):
        """ Create a supplier and add it to the database """
        suppliers = Supplier.all()
        self.assertEqual(suppliers, [])

        supplier = self._create_supplier()
        self.assertTrue(supplier != None)
        self.assertEqual(supplier.id, None)
        supplier.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertNotEqual(supplier.id, None)
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 1)

    def test_update_a_supplier(self):
        """ Update a Supplier """
        supplier = self._create_supplier()
        logging.debug(supplier)
        supplier.create()
        logging.debug(supplier)
        self.assertEqual(supplier.id, 1)
        # Change it an save it
        supplier.name = "Updated Name"
        original_id = supplier.id
        supplier.save()
        self.assertEqual(supplier.id, original_id)
        self.assertEqual(supplier.name, "Updated Name")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 1)
        self.assertEqual(suppliers[0].id, 1)
        self.assertEqual(suppliers[0].name, "Updated Name")

    def test_delete_a_supplier(self):
        """ Delete a Supplier """
        supplier = self._create_supplier()
        supplier.create()
        self.assertEqual(len(Supplier.all()), 1)
        # delete the pet and make sure it isn't in the database
        supplier.delete()
        self.assertEqual(len(Supplier.all()), 0)

    def test_serialize_a_supplier(self):
        """ Test serialization of a Supplier """
        supplier = self._create_supplier()
        data = supplier.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], supplier.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], supplier.name)
        self.assertIn("address", data)
        self.assertEqual(data["address"], supplier.address)
        self.assertIn("email", data)
        self.assertEqual(data["email"], supplier.email)
        self.assertIn("available", data)
        self.assertEqual(data["available"], supplier.available)
        self.assertIn("phone_number", data)
        self.assertEqual(data["phone_number"], supplier.phone_number)

    def test_deserialize_a_supplier(self):
        """ Test deserialization of a Supplier """
        data = {
            "id": 1,
            "name": "Jim Jones",
            "address": "123 Main Street, Anytown USA", 
            "email": "jjones@gmail.com",
            "phone_number": "800-555-1212",
            "available": True, 
            "products": []
        }
        supplier = Supplier()
        supplier.deserialize(data)
        self.assertNotEqual(supplier, None)
        self.assertEqual(supplier.id, None)
        self.assertEqual(supplier.name, "Jim Jones")
        self.assertEqual(supplier.address, "123 Main Street, Anytown USA")
        self.assertEqual(supplier.email, "jjones@gmail.com")
        self.assertEqual(supplier.phone_number, "800-555-1212")
        self.assertEqual(supplier.available, True)

    def test_deserialize_missing_data(self):
        """ Test deserialization of a supplier """
        data = {
            "id": 1,
            "name": "Jim Jones",
            "address": "123 Main Street, Anytown USA", 
        }
        supplier = Supplier()
        self.assertRaises(DataValidationError, supplier.deserialize, data)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        supplier = Supplier()
        self.assertRaises(DataValidationError, supplier.deserialize, data)

    def test_find_supplier(self):
        """ Find a Supplier by ID """    
        suppliers = self._create_suppliers(5)       
        for supplier in suppliers:
            supplier.create() 
        logging.debug(suppliers)
        # make sure they got saved
        self.assertEqual(len(Supplier.all()), 5)
        # find the 2nd supplier in the list
        supplier = Supplier.find(suppliers[1].id)
        self.assertIsNot(supplier, None)
        self.assertEqual(supplier.id, suppliers[1].id)
        self.assertEqual(supplier.name, suppliers[1].name)

    def test_find_by_name(self):
        """ Find a supplier by Name """
        Supplier(
            name="Supplier 1",
            email="supplier1@email.com",
            address="Supplier address 1",
            available=True, 
            phone_number="312 478 9890"
        ).create()

        Supplier(
            name="Supplier 2",
            email="supplier2@email.com",
            address="Supplier address 2", 
            available=False
        ).create()
        
        suppliers = Supplier.find_by_name("Supplier 1")
        self.assertEqual(suppliers[0].email, "supplier1@email.com")
        self.assertEqual(suppliers[0].address, "Supplier address 1")
        self.assertEqual(suppliers[0].available, True)
        self.assertEqual(suppliers[0].phone_number, "312 478 9890")

        suppliers = Supplier.find_by_name("Supplier 2")
        self.assertEqual(suppliers[0].email, "supplier2@email.com")
        self.assertEqual(suppliers[0].address, "Supplier address 2")
        self.assertEqual(suppliers[0].available, False)
        self.assertEqual(suppliers[0].phone_number, None)


    def test_find_by_email(self):
        """ Find a supplier by Email """
        Supplier(
            name="Supplier 1",
            email="supplier1@email.com",
            address="Suplier address 1",
            available=True, 
            phone_number="312 478 9890"
        ).create()

        Supplier(
            name="Supplier 2",
            email="supplier2@email.com",
            address="Suplier address 2", 
            available=False 
        ).create()
        
        suppliers = Supplier.find_by_email("supplier1@email.com")
        self.assertEqual(suppliers[0].name, "Supplier 1")
        self.assertEqual(suppliers[0].address, "Suplier address 1")
        self.assertEqual(suppliers[0].available, True)
        self.assertEqual(suppliers[0].phone_number, "312 478 9890")

        suppliers = Supplier.find_by_email("supplier2@email.com")
        self.assertEqual(suppliers[0].name, "Supplier 2")
        self.assertEqual(suppliers[0].address, "Suplier address 2")
        self.assertEqual(suppliers[0].available, False)
        self.assertEqual(suppliers[0].phone_number, None)

    def test_find_by_address(self):
        """ Find a supplier by Address """
        Supplier(
            name="Supplier 1",
            email="supplier1@email.com",
            address="Suplier address 1",
            available=True,
            phone_number="312 478 9890"
        ).create()

        Supplier(
            name="Supplier 2",
            email="supplier2@email.com",
            address="Suplier address 2", 
            available=False
        ).create()
        
        suppliers = Supplier.find_by_address("Suplier address 1")
        self.assertEqual(suppliers[0].name, "Supplier 1")
        self.assertEqual(suppliers[0].email, "supplier1@email.com")
        self.assertEqual(suppliers[0].available, True)
        self.assertEqual(suppliers[0].phone_number, "312 478 9890")

        suppliers = Supplier.find_by_address("Suplier address 2")
        self.assertEqual(suppliers[0].name, "Supplier 2")
        self.assertEqual(suppliers[0].email, "supplier2@email.com")
        self.assertEqual(suppliers[0].available, False)
        self.assertEqual(suppliers[0].phone_number, None)

    def test_find_by_available(self):
        """ Find a supplier by available """
        Supplier(
            name="Supplier 1",
            email="supplier1@email.com",
            address="Suplier address 1",
            available=True, 
            phone_number="312 478 9890"
        ).create()

        Supplier(
            name="Supplier 2",
            email="supplier2@email.com",
            address="Suplier address 2", 
            available=False 
        ).create()
        
        suppliers = Supplier.find_by_available(True)
        self.assertEqual(suppliers[0].name, "Supplier 1")
        self.assertEqual(suppliers[0].address, "Suplier address 1")
        self.assertEqual(suppliers[0].available, True)
        self.assertEqual(suppliers[0].phone_number, "312 478 9890")

        suppliers = Supplier.find_by_available(False)
        self.assertEqual(suppliers[0].name, "Supplier 2")
        self.assertEqual(suppliers[0].address, "Suplier address 2")
        self.assertEqual(suppliers[0].available, False)
        self.assertEqual(suppliers[0].phone_number, None)

    def test_sort_by(self):
        """ Find a supplier by available """
        Supplier(
            name="B Supplier 1",
            email="asupplier1@email.com",
            address="Suplier address 1",
            available=True, 
            phone_number="312 478 9890"
        ).create()

        Supplier(
            name="A Supplier 2",
            email="bsupplier2@email.com",
            address="Suplier address 2", 
            available=False 
        ).create()
        
        suppliers = Supplier.sort_by("name")
        self.assertEqual(suppliers[0].name, "A Supplier 2")
        self.assertEqual(suppliers[1].name, "B Supplier 1")

        suppliers = Supplier.sort_by("email")
        self.assertEqual(suppliers[0].email, "asupplier1@email.com")
        self.assertEqual(suppliers[1].email, "bsupplier2@email.com")


    def test_find_or_404_found(self):
        """ Find or return 404 found """
        suppliers = self._create_suppliers(3)
        for supplier in suppliers:
            supplier.create()

        supplier = Supplier.find_or_404(suppliers[1].id)
        self.assertIsNot(supplier, None)
        self.assertEqual(supplier.id, suppliers[1].id)
        self.assertEqual(supplier.name, suppliers[1].name)
        self.assertEqual(supplier.email, suppliers[1].email)
        self.assertEqual(supplier.address, suppliers[1].address)
        self.assertEqual(supplier.available, suppliers[1].available)
        self.assertEqual(supplier.phone_number, suppliers[1].phone_number)

    def test_find_or_404_not_found(self):
        """ Find or return 404 NOT found """
        self.assertRaises(NotFound, Supplier.find_or_404, 0)

    def test_deserialize_product_key_error(self):
        """ Deserialize a product listing with a KeyError """
        products = Product()
        self.assertRaises(DataValidationError, products.deserialize, {})

    def test_deserialize_product_type_error(self):
        """ Deserialize a product listing with a TypeError """
        products = Product()
        self.assertRaises(DataValidationError, products.deserialize, [])

    ######################################################################
    #  P R O D U C T   T E S T   C A S E S
    ######################################################################
        
    def test_create_a_product(self):
        """ Create a Product and assert that it exists """
        product = self._create_product()
        self.assertTrue(product != None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Macbook")

    def test_add_a_product(self):
        """ Create a Product and add it to the database """
        products = Product.all()
        self.assertEqual(products, [])

        product = self._create_product()
        self.assertTrue(product != None)
        self.assertEqual(product.id, None)
        product.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertNotEqual(product.id, None)
        products = Product.all()
        self.assertEqual(len(products), 1)

    def test_update_a_product(self):
        """ Update a Product """
        product = self._create_product()
        logging.debug(product)
        product.create()
        logging.debug(product)
        self.assertEqual(product.id, 1)
        # Change it an save it
        product.name = "Updated Name"
        original_id = product.id
        product.save()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.name, "Updated Name")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, 1)
        self.assertEqual(products[0].name, "Updated Name")

    def test_delete_a_product(self):
        """ Delete a Product """
        product = self._create_product()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_serialize_a_product(self):
        """ Test serialization of a Product """
        product = self._create_product()
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], product.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], product.name)


    def test_deserialize_a_product(self):
        """ Test deserialization of a Product """
        data = {
            "id": 1,
            "name": "Macbook"
        }
        product = Product()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        self.assertEqual(product.id, 1)
        self.assertEqual(product.name, "Macbook")


    ######################################################################
    #  A S S O C I A T I O N   T E S T   C A S E S
    ######################################################################
        
    def test_create_asociation(self):
        """ Create a Supplier with a Product and assert that it exists """
        supplier = self._create_association()
        self.assertTrue(supplier != None)
        self.assertEqual(supplier.id, 1)
        self.assertEqual(supplier.name, "Jim Jones")
        self.assertEqual(supplier.address, "123 Main Street, Anytown USA")
        self.assertEqual(supplier.email, "jjones@gmail.com")
        self.assertEqual(supplier.phone_number, "800-555-1212")
        self.assertEqual(supplier.products[0].supplier_id, 1)
        self.assertEqual(supplier.products[0].product_id, 1)
        self.assertEqual(supplier.products[0].wholesale_price, 999)
        self.assertEqual(supplier.products[0].product.name, "Macbook")

    def test_update_association(self):
        """ Create a Supplier-Product association, then update it's wholesale price """
        supplier = self._create_association()
        logging.debug(supplier)
        self.assertEqual(supplier.id, 1)
        # Change it an save it
        supplier.products[0].wholesale_price = 1000
        original_id = supplier.id
        supplier.save()
        self.assertEqual(supplier.id, original_id)
        self.assertEqual(supplier.products[0].wholesale_price, 1000)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        associations = Association.all()
        self.assertEqual(len(associations), 1)
        self.assertEqual(associations[0].supplier_id, 1)
        self.assertEqual(associations[0].wholesale_price, 1000)

    def test_delete_association(self):
        """ Delete an Association """
        supplier = self._create_association()
        self.assertEqual(len(Association.all()), 1)
        # delete the pet and make sure it isn't in the database
        supplier.products[0].delete()
        self.assertEqual(len(Association.all()), 0)

    def test_delete_association2(self):
        """ Delete an Association 2 """
        supplier = self._create_association()
        product = self._create_product()
        product.create()
        association2 = Association(wholesale_price=1000)
        association2.supplier_id = supplier.id
        association2.product_id = product.id
        supplier.products.append(association2)
        self.assertEqual(len(Association.all()), 2)
        # delete the pet and make sure it isn't in the database
        supplier.products[0].delete()
        self.assertEqual(len(Association.all()), 1)

    def test_serialize_an_association(self):
        """ Test serialization of a Association """
        association = Association(
            supplier_id=20,
            product_id=10,
            wholesale_price=99
        )
        data = association.serialize()
        logging.debug(data)
        self.assertNotEqual(data, None)
        self.assertIn("supplier_id", data)
        self.assertEqual(data["supplier_id"], association.supplier_id)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], association.product_id)
        self.assertIn("wholesale_price", data)
        self.assertEqual(data["wholesale_price"], association.wholesale_price)

    def test_deserialize_an_association(self):
        """ Test deserialization of a association """
        data = {
            "supplier_id": 1,
            "product_id": 1,
            "wholesale_price": 33
        }
        association = Association()
        association.deserialize(data)

        self.assertEqual(association.supplier_id, 1)
        self.assertEqual(association.product_id, 1)
        self.assertEqual(association.wholesale_price, 33)

    def test_deserialize_association_missing_data(self):
        """ Test deserialization of a supplier """
        data = {
            "supplier_id": 1,
            "product_id": 1
        }
        association = Association()
        self.assertRaises(DataValidationError, association.deserialize, data)

    def test_deserialize_association_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        association = Association()
        self.assertRaises(DataValidationError, association.deserialize, data)

    def test_multiple_associations(self):
        """ Create two associations, list them out, and confirm both were created """    
        supplier = self._create_association()     
        supplier2 = self._create_association()     
        logging.debug(supplier)
        # make sure they got saved
        self.assertEqual(len(Association.all()), 2)
        # make sure the first association was connected to supplier 1
        self.assertEqual(supplier.products[0].supplier_id, 1)
        # make sure the second association was connected to supplier 2
        self.assertEqual(supplier2.products[0].supplier_id,2)