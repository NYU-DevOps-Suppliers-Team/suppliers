"""
Test cases for Supplier Model

"""
import logging
import unittest
import os
from service.models import Supplier, DataValidationError, db
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
            product_list=[1,2,3,4]
        )

    def _create_suppliers(self, count):
        """ Factory method to create suppliers in bulk """
        suppliers = []
        for _ in range(count):
            test_supplier = self._create_supplier()
            suppliers.append(test_supplier)
        return suppliers

    ######################################################################
    #  T E S T   C A S E S
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
        self.assertEqual(supplier.product_list, [1,2,3,4])

    #Test supplier without optional phone number 
        supplier = Supplier(
            name="Jim Jones",
            address="123 Main Street, Anytown USA", 
            email="jjones@gmail.com",
            product_list=[1,2,3,4]
        )    
        self.assertTrue(supplier != None)
        self.assertEqual(supplier.id, None)
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
        self.assertIn("phone_number", data)
        self.assertEqual(data["phone_number"], supplier.phone_number)
        self.assertIn("product_list", data)
        self.assertEqual(data["product_list"], supplier.product_list)

    def test_deserialize_a_supplier(self):
        """ Test deserialization of a Supplier """
        data = {
            "id": 1,
            "name": "Jim Jones",
            "address": "123 Main Street, Anytown USA", 
            "email": "jjones@gmail.com",
            "phone_number": "800-555-1212",
            "product_list": [1,2,3,4]
        }
        supplier = Supplier()
        supplier.deserialize(data)
        self.assertNotEqual(supplier, None)
        self.assertEqual(supplier.id, None)
        self.assertEqual(supplier.name, "Jim Jones")
        self.assertEqual(supplier.address, "123 Main Street, Anytown USA")
        self.assertEqual(supplier.email, "jjones@gmail.com")
        self.assertEqual(supplier.phone_number, "800-555-1212")
        self.assertEqual(supplier.product_list, [1,2,3,4])

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
            address="Suplier address 1",
            phone_number="312 478 9890",
            product_list=[1, 2, 3, 4]
        ).create()

        Supplier(
            name="Supplier 2",
            email="supplier2@email.com",
            address="Suplier address 2",
            product_list=[1, 2, 3, 4, 5]
        ).create()
        
        suppliers = Supplier.find_by_name("Supplier 1")
        self.assertEqual(suppliers[0].email, "supplier1@email.com")
        self.assertEqual(suppliers[0].address, "Suplier address 1")
        self.assertEqual(suppliers[0].phone_number, "312 478 9890")
        self.assertEqual(suppliers[0].product_list, [1, 2, 3, 4])

        suppliers = Supplier.find_by_name("Supplier 2")
        self.assertEqual(suppliers[0].email, "supplier2@email.com")
        self.assertEqual(suppliers[0].address, "Suplier address 2")
        self.assertEqual(suppliers[0].phone_number, None)
        self.assertEqual(suppliers[0].product_list, [1, 2, 3, 4, 5])


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
        self.assertEqual(supplier.phone_number, suppliers[1].phone_number)
        self.assertEqual(supplier.product_list, suppliers[1].product_list)