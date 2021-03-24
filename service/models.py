"""
Models for Supplier

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass

######################################################################
#  P R O D U C T  L I S T   M O D E L
######################################################################
class ProductList(db.Model):
    """
    Class that represents an ProductListing
    """

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    product_id = db.Column(db.Integer)
    name = db.Column(db.String(64))
    wholesale_price = db.Column(db.Integer)

    def __repr__(self):
        return "<ProductListing %r id=[%s]>" % (self.product_id, self.id, self.supplier_id)

    def create(self):
        """
        Creates a ProductListing to the database
        """
        logger.info("Creating %s", self.id)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a ProductListing to the database
        """
        logger.info("Saving %s", self.id)
        db.session.commit()

    def delete(self):
        """ Removes a ProductListing from the data store """
        logger.info("Deleting %s", self.id)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a ProductListing into a dictionary """
        return {"id": self.id,
                "supplier_id": self.supplier_id,
                "product_id": self.product_id,
                "name": self.name,
                "wholesale_price": self.wholesale_price
        }

    def deserialize(self, data):
        """
        Deserializes a ProductListing from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.supplier_id = data["supplier_id"]
            self.product_id = data["product_id"]
            self.name = data["name"]
            self.wholesale_price = data.get("wholesale_price") 
        except KeyError as error:
            raise DataValidationError(
                "Invalid ProductListing: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid ProductListing: body of request contained bad or no data"
            )
        return self 


######################################################################
#  S U P P L I E R   M O D E L
######################################################################

class Supplier(db.Model):
    """
    Class that represents a Supplier
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    email = db.Column(db.String(63), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(20))
    productlist = db.relationship('ProductList', backref='supplier', lazy=True)

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
                "productlist": []
        }
        for productlisting in self.productlist:
            supplier['productlist'].append(productlisting.serialize())
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
            # handle inner list of product listings
            products = data.get("productlist")
            for json_products in products:
                productlisting = ProductList()
                productlisting.deserialize(json_products)
                self.productlist.append(productlisting)
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
