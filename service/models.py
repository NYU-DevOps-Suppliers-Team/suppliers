"""
Models for Supplier

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc


logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass

######################################################################
#  A S S O C I A T I O N  T A B L E
######################################################################
class Association(db.Model):
    __tablename__ = 'association'
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    wholesale_price = db.Column(db.Integer)
    product = db.relationship("Product", back_populates="suppliers")
    supplier = db.relationship("Supplier", back_populates="products")
    
    def serialize(self):
        """ Serializes an Association into a dictionary """
        return {
            "supplier_id": self.supplier_id,
            "product_id": self.product_id,
            "wholesale_price": self.wholesale_price
            }

    def deserialize(self, data):
        """
        Deserializes a Association from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.wholesale_price = data["wholesale_price"]
            self.supplier_id = data["supplier_id"]
            self.product_id = data["product_id"]

        except KeyError as error:
            raise DataValidationError(
                "Invalid Association: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Association: body of request contained bad or no data"
            )
        return self

    def delete(self):
        """ Removes a Association from the data store """
        logger.info("Deleting association")
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def all(cls):
        """ Returns all of the Associations in the database """
        logger.info("Processing all Associations")
        return cls.query.all()

    @classmethod
    def find(cls, supplier_id, product_id):
        """ Finds Association by it's ID """
        logger.info("Processing lookup for id %s ...", supplier_id)
        return cls.query.get((supplier_id, product_id))
    
######################################################################
#  S U P P L I E R   M O D E L
######################################################################

class Supplier(db.Model):
    """
    Class that represents a Supplier
    """

    app = None
   
    __tablename__ = 'supplier'

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    email = db.Column(db.String(63), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(20))
    available = db.Column(db.Boolean(), nullable=False, default=True)
    products = db.relationship("Association", back_populates="supplier")

    def __repr__(self):
        return "<Supplier %r id=[%s]>" % (self.name, self.id)

    def create(self):
        """
        Creates a Supplier to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a Supplier to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a Supplier from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Supplier into a dictionary """
        supplier = {"id": self.id,
                "name": self.name,
                "address": self.address,
                "email": self.email,
                "phone_number": self.phone_number,
                "available": self.available, 
                "products": []
        }
        for product in self.products:
            supplier['products'].append(product.serialize())
        return supplier

    def deserialize(self, data):
        """
        Deserializes a Supplier from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.address = data["address"]
            self.email = data["email"]
            self.phone_number = data.get("phone_number") 
            self.available = data["available"]
            # handle inner list of product listings
            products = data.get("products")
            for json_products in products:
                product = Product()
                product.deserialize(json_products)
                self.products.append(product)
        except KeyError as error:
            raise DataValidationError(
                "Invalid Supplier: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Supplier: body of request contained bad or no data"
            )
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Suppliers in the database """
        logger.info("Processing all Suppliers")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Supplier by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a Supplier by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Suppliers with the given name

        Args:
            name (string): the name of the Suppliers you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_email(cls, email):
        """Returns all Suppliers with the given email

        Args:
            email (string): the email of the Suppliers you want to match
        """
        logger.info("Processing email query for %s ...", email)
        return cls.query.filter(cls.email == email)
        
    @classmethod
    def find_by_address(cls, address):
        """Returns all Suppliers with the given address

        Args:
            address (string): the address of the Suppliers you want to match
        """
        logger.info("Processing address query for %s ...", address)
        return cls.query.filter(cls.address == address)       

    @classmethod
    def find_by_available(cls, available):
        """Returns all Suppliers with the given available

        Args:
            available (string): the available of the Suppliers you want to match
        """
        logger.info("Processing available query for %s ...", available)
        return cls.query.filter(cls.available == available)     

    @classmethod
    def sort_by(cls, sort_by):
        """Returns all of the suppliers sorted by customer_id"""
        logger.info("Processing all suppliers query sorted by %s ...", sort_by)
        return cls.query.order_by(asc(sort_by))

######################################################################
#  P R O D U C T  M O D E L
######################################################################
class Product(db.Model):
    """
    Class that represents an Product
    """
   
    __tablename__ = 'product'

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    suppliers = db.relationship("Association", back_populates="product") 

    def __repr__(self):
        return "<Product %r id=[%s]>" % (self.name, self.id)

    def create(self):
        """
        Creates a Product to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a Product to the database
        """
        logger.info("Saving %s", self.id)
        db.session.commit()

    def delete(self):
        """ Removes a Product from the data store """
        logger.info("Deleting %s", self.id)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Product into a dictionary """
        return {
            "id": self.id,
            "name": self.name
            }

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data["id"]
            self.name = data["name"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid Product: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Product: body of request contained bad or no data"
            )
        return self 

    @classmethod
    def all(cls):
        """ Returns all of the Products in the database """
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Product by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a Product by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)