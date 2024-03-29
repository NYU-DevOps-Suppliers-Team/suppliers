"""
My Service

Describe what your service does here
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Supplier, Product, Association, DataValidationError

# Import Flask application
from . import app

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)


@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_400_BAD_REQUEST, error="Bad Request", message=message
        ),
        status.HTTP_400_BAD_REQUEST,
    )


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(status=status.HTTP_404_NOT_FOUND, error="Not Found", message=message),
        status.HTTP_404_NOT_FOUND,
    )


@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
            error="Method not Allowed",
            message=message,
        ),
        status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = str(error)
    app.logger.warning(message)
    return (
        jsonify(
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            error="Unsupported media type",
            message=message,
        ),
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    )


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    app.logger.error(message)
    return (
        jsonify(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal Server Error",
            message=message,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    # return (
    #     jsonify(
    #         name="Supplier REST API Service",
    #         version="1.0",
    #         paths=url_for("list_suppliers", _external=True),
    #     ),
    #     status.HTTP_200_OK,
    # )
    return app.send_static_file('index.html')

########################################################################################################################################## 
# SUPPLIER ROUTES
########################################################################################################################################### 


######################################################################
# CREATE A NEW SUPPLIER
######################################################################
@app.route("/suppliers", methods=["POST"])
def create_suppliers():
    """
    Creates a Supplier
    This endpoint will create a Supplier based the data in the body that is posted
    """
    app.logger.info("Request to create a Supplier")
    check_content_type("application/json")
    supplier = Supplier()
    supplier.deserialize(request.get_json())
    supplier.create()
    message = supplier.serialize()
    location_url = url_for("get_supplier", supplier_id=supplier.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# LIST ALL SUPPLIERS
######################################################################
@app.route("/suppliers", methods=["GET"])
def list_suppliers():
    """ Returns all of the Suppliers """
    app.logger.info("Request for supplier list")
    suppliers = []
    name = request.args.get("name")
    email = request.args.get("email")
    address = request.args.get("address")
    available = request.args.get("available")
    sort_by = request.args.get('sort_by')


    if name:
        suppliers = Supplier.find_by_name(name)
    elif email:
        suppliers = Supplier.find_by_email(email)
    elif address:
        suppliers = Supplier.find_by_address(address)    
    elif available:
        suppliers = Supplier.find_by_available(available)             
    else:
        if sort_by is not None:
            suppliers = Supplier.sort_by(sort_by)
        else:
            suppliers = Supplier.all()

    results = [supplier.serialize() for supplier in suppliers]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# DELETE A SUPPLIER
######################################################################
@app.route("/suppliers/<int:id>", methods=["DELETE"])
def delete_suppliers(id):
    """
    Delete a Supplier
    This endpoint will delete a Supplier based the id specified in the path
    """
    app.logger.info("Request to delete supplier with id: %s", id)
    supplier = Supplier.find(id)
    if supplier:
        supplier.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)
    
#####################################################################    
# READ A SUPPLIER
######################################################################
@app.route("/suppliers/<int:supplier_id>", methods=["GET"])
def get_supplier(supplier_id):
    """
    Read a single Supplier
    This endpoint will return a Supplier based on it's id
    """
    app.logger.info("Request for supplier with id: %s", supplier_id)
    supplier = Supplier.find(supplier_id)
    if not supplier:
        raise NotFound("Supplier with id '{}' was not found.".format(supplier_id))
    return make_response(jsonify(supplier.serialize()), status.HTTP_200_OK)


######################################################################
# UPDATE AN EXISTING SUPPLIER
######################################################################
@app.route("/suppliers/<int:supplier_id>", methods=["PUT"])
def update_suppliers(supplier_id):
    """
    Update a Supplier
    This endpoint will update a Supplier based the body that is posted
    """
    app.logger.info("Request to update Supplier with id: %s", supplier_id)
    check_content_type("application/json")
    supplier = Supplier.find(supplier_id)
    if not supplier:
        raise NotFound("Supplier with id '{}' was not found.".format(supplier_id))
    supplier.deserialize(request.get_json())
    supplier.id = supplier_id
    supplier.save()
    return make_response(jsonify(supplier.serialize()), status.HTTP_200_OK)

######################################################################
# MAKE A SUPPLIER UNAVAILABLE
######################################################################
@app.route('/suppliers/<int:supplier_id>/unavailable', methods=['PUT'])
def unavailable_supplier(supplier_id):
    """ Marking a supplier unavailable """
    supplier = Supplier.find(supplier_id)
    if not supplier:
        abort(status.HTTP_404_NOT_FOUND, "Supplier with id '{}' was not found.".format(supplier_id)) 
    supplier.available=False 
    supplier.save()
    return make_response(jsonify(supplier.serialize()), status.HTTP_200_OK)

########################################################################################################################################## 
# PRODUCT ROUTES
########################################################################################################################################### 

######################################################################
# ADD A PRODUCT AKA CREATE
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to create a Product")
    check_content_type("application/json")
    product = Product()
    product.deserialize(request.get_json())
    product.create()
    message = product.serialize()
    location_url = url_for("get_product", product_id=product.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )
    
#####################################################################    
# READ A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """
    Read a single Product
    This endpoint will return a product based on it's id
    """
    app.logger.info("Request for product with id: %s", product_id)
    product = Product.find(product_id)
    if not product:
        raise NotFound("product with id '{}' was not found.".format(product_id))
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)

######################################################################
# UPDATE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """
    Update a Product
    This endpoint will update a Product based the body that is posted
    """
    app.logger.info("Request to update Product with id: %s", product_id)
    check_content_type("application/json")
    product = Product.find(product_id)
    if not product:
        raise NotFound("Product with id '{}' was not found.".format(product_id))
    product.deserialize(request.get_json())
    product.id = product_id
    product.save()
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A PRODUCT
######################################################################
@app.route("/products/<int:id>", methods=["DELETE"])
def delete_products(id):
    """
    Delete a Product
    This endpoint will delete a Product based the id specified in the path
    """
    app.logger.info("Request to delete product with id: %s", id)
    product = Product.find(id)
    if product:
        product.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
# LIST ALL PRODUCTS
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """ Returns all of the products """
    app.logger.info("Request for product list")
    products = []
    name = request.args.get("name")
    if name:
        products = Product.find_by_name(name)
    else:
        products = Product.all()

    results = [product.serialize() for product in products]
    return make_response(jsonify(results), status.HTTP_200_OK)

########################################################################################################################################## 
# ASSOCIATION ROUTES
########################################################################################################################################### 

######################################################################
# CREATE A NEW ASSOCIATION
######################################################################
@app.route('/suppliers/<int:supplier_id>/products/<int:product_id>', methods=["POST"])
def create_association(supplier_id, product_id):
    """
    Creates an Association between a supplier and a product
    This endpoint will create an Association based the data in the body that is posted
    """
    app.logger.info("Request to create an Association")
    check_content_type("application/json")
    
    supplier = Supplier.find_or_404(supplier_id)
    product = Product.find_or_404(product_id)
    association = Association()
    association.deserialize(request.get_json())
    association.product = product
    supplier.products.append(association)
    supplier.save()

    message = association.serialize()
    #location_url = url_for("get_association", supplier_id=supplier.id, _external=True)
    location_url = "get function not implemented yet"
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

#####################################################################    
# READ A ASSOCIATION
######################################################################
@app.route("/suppliers/<int:supplier_id>/products/<int:product_id>", methods=["GET"])
def get_association(supplier_id, product_id):
    """
    Read a single association
    This endpoint will return a association based on the productId and the supplierId
    """
    app.logger.info("Request for association with id: %s", supplier_id, product_id)

    association = Association.find(supplier_id, product_id)

    if not association:
        raise NotFound("association with supplier id '{}' and with product id '{}' was not found.".format(supplier_id, product_id))
    return make_response(jsonify(association.serialize()), status.HTTP_200_OK)


######################################################################
# UPDATE WHOLESALE PRICE ON AN EXISTING ASSOCIATION
######################################################################
@app.route('/suppliers/<int:supplier_id>/products/<int:product_id>', methods=["PUT"])
def update_association(supplier_id, product_id):
    """
    Update the wholesale price on an association between a supplier and a product
    This endpoint will update an association based the data in the body that is posted
    """
    app.logger.info("Request to update an Association")
    check_content_type("application/json")
    
    supplier = Supplier.find_or_404(supplier_id)
    product = Product.find_or_404(product_id)
    association = Association()
    association.deserialize(request.get_json())
    supplier.products.wholesale_price = association.wholesale_price
    supplier.save()

    return make_response(jsonify(association.serialize()), status.HTTP_200_OK)

######################################################################
# LIST ALL ASSOCIATIONS
######################################################################
@app.route("/associations", methods=["GET"])
def list_associations():
    """ Returns all of the associations """
    app.logger.info("Request for association list")
    associations = []
    
    associations = Association.all()

    results = [association.serialize() for association in associations]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# LIST ALL SUPPLIERS PRODUCTS
######################################################################
@app.route("/suppliers/<int:supplier_id>/products", methods=["GET"])
def list_supplier_products(supplier_id):
    """ Returns all of the products given a supplier """
    supplier = Supplier.find_or_404(supplier_id)
    result = supplier.serialize()

    return make_response(jsonify(result["products"]), status.HTTP_200_OK)

######################################################################
# DELETE AN ASSOCIATION
######################################################################
@app.route('/suppliers/<int:supplier_id>/products/<int:product_id>', methods=["DELETE"])
def delete_association(supplier_id, product_id):
    """
    Delete an association between a supplier and a product
    This endpoint will delete an association based the data in the body that is posted
    """
    app.logger.info("Request to delete an Association")
    check_content_type("application/json")
    
    association = Association.find(supplier_id, product_id)

    if not association:
        raise NotFound("association with supplier id '{}' and with product id '{}' was not found.".format(supplier_id, product_id))
    else:
        association.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Supplier.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers["Content-Type"] == content_type:
        return
    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(415, "Content-Type must be {}".format(content_type))