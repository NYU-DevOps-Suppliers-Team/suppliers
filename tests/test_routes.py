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
from flask_api import status  # HTTP Status Codes
from service.models import db, Supplier
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
            phone_number="800-555-1212"
        )
    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # data = resp.get_json()
        # self.assertEqual(data["name"], "Supplier REST API Service")

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
        
        # ToDo: Uncomment once Retreive Supplier is implemented 

        # # Check that the location header was correct
        # resp = self.app.get(location, content_type="application/json")
        # self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # new_supplier = resp.get_json()
        # self.assertEqual(new_supplier["name"], test_supplier.name)
        # self.assertEqual(new_supplier["email"], test_supplier.email)
        # self.assertEqual(new_supplier["address"], test_supplier.address)
        # self.assertEqual(new_supplier["phone_number"], test_supplier.phone_number)