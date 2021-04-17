"""
TestSupplier API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus
from flask_api import status  # HTTP Status Codes
from service.models import db, Supplier, Product, Association
from service.routes import app, init_db 

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgres://postgres:postgres@localhost:5432/postgres"
)
######################################################################
#  T E S T   C A S E S
######################################################################
class TestSuppplierServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    def setUp(self):
        """ Runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
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
        """ Factory method to create suppliers in bulk """
        suppliers = []
        for _ in range(count):
            test_supplier = self._create_supplier()
            resp = self.app.post(
                "/suppliers", json=test_supplier.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test supplier"
            )
            new_supplier = resp.get_json()
            test_supplier.id = new_supplier["id"]
            suppliers.append(test_supplier)
        return suppliers

    def _create_product(self): 
        return Product(
            name="Macbook"
        )

    def _create_products(self, count):
        """ Factory method to create products in bulk """
        products = []
        for _ in range(count):
            test_product = self._create_product()
            resp = self.app.post(
                "/products", json=test_product.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test product"
            )
            new_product = resp.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    def _create_association(self): 
        supplier = self._create_supplier()
        product = self._create_product()
        product.create()
        association = Association(wholesale_price=999)
        association.supplier_id = supplier.id
        association.product_id = product.id
        supplier.products.append(association)
        return supplier

    def _create_association_with_price(self, price): 
        supplier = self._create_supplier()
        product = self._create_product()
        product.create()
        association = Association(wholesale_price=price)
        association.product = product
        supplier.products.append(association)
        supplier.save()
        
        return association

    def _create_associations(self, count):
        """ Factory method to create products in bulk """
        for _ in range(count):
            test_association = self._create_association_with_price(count + 100)



    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # data = resp.get_json()
        # self.assertEqual(data["name"], "Supplier REST API Service")
    
    ######################################################################
    #  SUPPLIER ROUTE TEST CASES
    ######################################################################

    def test_create_supplier(self):
        """ Create a new Supplier """
        test_supplier = self._create_supplier()
        logging.debug(test_supplier)
        resp = self.app.post(
            "/suppliers", json=test_supplier.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_supplier = resp.get_json()
        self.assertEqual(new_supplier["name"], test_supplier.name)
        self.assertEqual(new_supplier["email"], test_supplier.email)
        self.assertEqual(new_supplier["address"], test_supplier.address)
        self.assertEqual(new_supplier["phone_number"], test_supplier.phone_number)
        self.assertEqual(new_supplier["products"], test_supplier.products)

    def test_get_supplier_not_found(self):
        """ Get a supplier thats not found """
        resp = self.app.get("/suppliers/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_supplier(self):
        """ Get a single Supplier """
        # get the id of a supplier
        test_suppliers = self._create_suppliers(5)
        test_supplier = test_suppliers[0]
        test_supplier.create()
        resp = self.app.get(
            "/suppliers/{}".format(test_supplier.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], test_supplier.name)
     
        # ToDo: Uncomment once Retreive Supplier is implemented 

        # # Check that the location header was correct
        # resp = self.app.get(location, content_type="application/json")
        # self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # new_supplier = resp.get_json()
        # self.assertEqual(new_supplier["name"], test_supplier.name)
        # self.assertEqual(new_supplier["email"], test_supplier.email)
        # self.assertEqual(new_supplier["address"], test_supplier.address)
        # self.assertEqual(new_supplier["phone_number"], test_supplier.phone_number)

    def test_update_supplier(self):
        """ Update an existing supplier """
        # create a supplier to update
        test_supplier = self._create_supplier() 
        resp = self.app.post(
            "/suppliers", json=test_supplier.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the supplier
        new_supplier = resp.get_json()
        logging.debug(new_supplier)
        new_supplier["name"] = "Updated Name"
        resp = self.app.put(
            "/suppliers/{}".format(new_supplier["id"]),
            json=new_supplier,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_supplier = resp.get_json()
        self.assertEqual(updated_supplier["name"], "Updated Name")
            
    def test_delete_supplier(self):
        """ Delete a Supplier """
        test_supplier = self._create_supplier() 
        test_supplier.create()
        resp = self.app.delete(
            "/suppliers/{}".format(test_supplier.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "/suppliers/".format(test_supplier.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_get_supplier_list(self):
        """ Get a list of Suppliers """
        self._create_suppliers(5)
        resp = self.app.get("/suppliers")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_query_supplier_list_by_name(self):
        """ Query Suppliers by name """
        suppliers = self._create_suppliers(5)
        test_name = suppliers[0].name
        name_suppliers = [supplier for supplier in suppliers if supplier.name == test_name]
        resp = self.app.get(
            "/suppliers", query_string="name={}".format(quote_plus(test_name))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(name_suppliers))
        # check the data just to be sure
        for supplier in data:
            self.assertEqual(supplier["name"], test_name)

    def test_query_supplier_list_by_email(self):
        """ Query Suppliers by email """
        suppliers = self._create_suppliers(5)
        test_email = suppliers[0].email
        email_suppliers = [supplier for supplier in suppliers if supplier.email == test_email]
        resp = self.app.get(
            "/suppliers", query_string="email={}".format(quote_plus(test_email))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(email_suppliers))
        # check the data just to be sure
        for supplier in data:
            self.assertEqual(supplier["email"], test_email)
    
    def test_query_supplier_list_by_address(self):
        """ Query Suppliers by address """
        suppliers = self._create_suppliers(5)
        test_address = suppliers[0].address
        address_suppliers = [supplier for supplier in suppliers if supplier.address == test_address]
        resp = self.app.get(
            "/suppliers", query_string="address={}".format(quote_plus(test_address))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(address_suppliers))
        # check the data just to be sure
        for supplier in data:
            self.assertEqual(supplier["address"], test_address)

    def test_query_supplier_list_by_availability(self):
        """ Query Suppliers by availability """
        suppliers = self._create_suppliers(5)
        test_available = suppliers[0].available
        available_suppliers = [supplier for supplier in suppliers if supplier.available == test_available]
        resp = self.app.get(
            "/suppliers", query_string="available={}".format(quote_plus(str(test_available)))
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(available_suppliers))
        # check the data just to be sure
        for supplier in data:
            self.assertEqual(supplier["available"], test_available)

    def test_content_type_error(self):
        """ Create a new Supplier """
        test_supplier = self._create_supplier()
        logging.debug(test_supplier)
        resp = self.app.post(
            "/suppliers", json=test_supplier.serialize(), content_type="badcontent"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_mark_supplier_availability(self):
        """ Mark an available Supplier (action test) """
        supplier = self._create_supplier()
        supplier.create()
        
        resp = self.app.get('/suppliers/{}'.format(supplier.id), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        logging.debug('data = %s', data)
        #Ensure that an available flag is true prior to action
        self.assertEqual(data["available"], True)

        resp = self.app.put('/suppliers/{}/unavailable'.format(supplier.id), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp = self.app.get('/suppliers/{}'.format(supplier.id), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        logging.debug('data = %s', data)
        #Ensure that an available flag is set to false after action
        self.assertEqual(data["available"], False)

######################################################################
#  PRODUCT ROUTE TEST CASES
######################################################################

    def test_create_product(self):
        """ Create a new Product """
        test_product = self._create_product()
        test_product.create()
        logging.debug(test_product)
        resp = self.app.post(
            "/products", json=test_product.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = resp.get_json()
        self.assertEqual(new_product["name"], test_product.name)

    def test_get_product_not_found(self):
        """ Get a product thats not found """
        resp = self.app.get("/products/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_product(self):
        """ Get a single Product """
        # get the id of a product
        test_products = self._create_products(5)
        test_product = test_products[0]
        test_product.create()
        resp = self.app.get(
            "/products/{}".format(test_product.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], test_product.name)

    def test_update_product(self):
        """ Update an existing product """
        # create a product to update
        test_product = self._create_product()
        resp = self.app.post(
            "/products", json=test_product.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the product
        new_product = resp.get_json()
        logging.debug(new_product)
        new_product["name"] = "Updated Name"
        resp = self.app.put(
            "/products/{}".format(new_product["id"]),
            json=new_product,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = resp.get_json()
        self.assertEqual(updated_product["name"], "Updated Name")
    
    def test_delete_product(self):
        """ Delete a Product """
        test_product = self._create_product() 
        test_product.create()
        resp = self.app.delete(
            "/products/{}".format(test_product.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "/products/".format(test_product.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_product_list(self):
        """ Get a list of Products """
        self._create_products(5)
        resp = self.app.get("/products")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

######################################################################
#  ASSOCIATION ROUTE TEST CASES
######################################################################

    def test_add_association(self):
        """ Add an product to a supplier """

        supplier = self._create_supplier()
        supplier.create()
        product = self._create_product()
        product.create()

        data = dict(
            supplier_id=supplier.id,
            product_id=product.id,
            wholesale_price=24
        )

        resp = self.app.post(
            "/suppliers/{}/products/{}".format(supplier.id, product.id),
            json=data,
            content_type="application/json"
        )

        logging.debug(resp)
     
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug(data)

        self.assertEqual(data["supplier_id"], supplier.id)
        self.assertEqual(data["product_id"], supplier.products[0].product_id)
        self.assertEqual(data["wholesale_price"], supplier.products[0].wholesale_price)


    def test_update_association(self):
        """ Create a supplier/product association to update """

        # create the assciation
        supplier = self._create_supplier()
        supplier.create()
        product = self._create_product()
        product.create()

        data = dict(
            supplier_id=supplier.id,
            product_id=product.id,
            wholesale_price=24
        )

        resp = self.app.post(
            "/suppliers/{}/products/{}".format(supplier.id, product.id),
            json=data,
            content_type="application/json"
        )

        logging.debug(resp)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        #update the wholesale price
        new_association = resp.get_json()
        new_association["wholesale_price"] = 100
        resp = self.app.put(
            "/suppliers/{}/products/{}".format(supplier.id, product.id),
            json=new_association,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_association = resp.get_json()
        self.assertEqual(updated_association["wholesale_price"], 100)
    
    def test_get_association(self):
        """ Get a single association """

        association1 = self._create_association_with_price(359)
        resp = self.app.get(
            "/suppliers/{}/products/{}".format(association1.supplier_id,association1.product_id), content_type="application/json"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        print(data)
        self.assertEqual(data["wholesale_price"], association1.wholesale_price)
        self.assertEqual(data["supplier_id"], association1.supplier_id)
        self.assertEqual(data["product_id"], association1.product_id)
        

        association2 = self._create_association_with_price(2010)
        resp = self.app.get(
            "/suppliers/{}/products/{}".format(association2.supplier_id,association1.product_id), content_type="application/json"
        )

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_association_list(self):
        """ Get a list of associations """
        self._create_associations(5)
        resp = self.app.get("/associations")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_list_supplier_products(self):
        """ Get a list of all products given a supplier """
        supplier = self._create_supplier()
        product = self._create_product()
        product.create()
        product2 = self._create_product()
        product2.create()

        association = Association(wholesale_price=1000)
        association.product = product
        supplier.products.append(association)

        association2 = Association(wholesale_price=500)
        association2.product = product2
        supplier.products.append(association2)
        supplier.save()


        resp = self.app.get(
            "/suppliers/{}/products".format(association.supplier_id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        print(data)
        self.assertEqual(len(data), 2)



    def test_delete_association(self):
        """ Delete an association """

        association = self._create_association_with_price(999)
        resp = self.app.delete(
            "/suppliers/{}/products/{}".format(association.supplier_id,association.product_id), content_type="application/json"
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "/suppliers/{}/products/{}".format(association.supplier_id,association.product_id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
