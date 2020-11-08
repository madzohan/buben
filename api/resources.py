from flask import jsonify, Blueprint, make_response, url_for, request
from flask_caching import Cache
from flask_restful import Resource, Api
from webargs import fields
from webargs.flaskparser import use_args, use_kwargs, parser, abort

from api import models, schemas


api_bp = Blueprint('api', __name__)

cache = Cache(config={'CACHE_TYPE': 'simple'})


class Product(Resource):
    @use_kwargs({"reviews_per_page": fields.Int(missing=5),
                 "page": fields.Int(missing=1)}, location="query")
    def get(self, product_id: int, page: int, reviews_per_page: int):
        reviews = cached = cache.get(request.url)
        if cached is None:
            reviews = models.Review.query.filter_by(product_id=product_id).order_by(
                models.Review.id.asc()).paginate(page, reviews_per_page).items
            cache.set(request.url, reviews)
        product_dump = schemas.Product().dump(reviews[0].product)
        product_dump["reviews"] = schemas.Review(many=True).dump(reviews)
        return jsonify({"products": [product_dump]})


class Review(Resource):
    def get(self, product_id: int, review_id: int):
        review = cached = cache.get(request.url)
        if cached is None:
            review = models.Review.query.get(review_id)
            cache.set(request.url, review)
        product_dump = schemas.Product().dump(review.product)
        product_dump["reviews"] = schemas.Review(many=True).dump([review])
        return jsonify({"products": [product_dump]})

    @use_args(schemas.Review())
    def put(self, kwargs: dict, product_id: int):
        new_review = models.Review(**kwargs)
        models.db.session.add(new_review)
        models.db.session.commit()
        product_dump = schemas.Product().dump(new_review.product)
        product_dump["reviews"] = schemas.Review(many=True).dump([new_review])
        resp = make_response(product_dump, 201)
        resp.headers["Location"] = url_for("api.review", product_id=product_id, review_id=new_review.id)
        return resp


api = Api(api_bp, prefix='/api/v1')
api.add_resource(Product, "/products/<int:product_id>.json", endpoint="product")
api.add_resource(Review,
                 "/products/<int:product_id>/reviews/<int:review_id>.json",
                 "/products/<int:product_id>/reviews/create.json",
                 endpoint="review")


# This error handler is necessary for usage with Flask-RESTful
@parser.error_handler
def handle_request_parsing_error(err, req, schema, *, error_status_code, error_headers):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(error_status_code, errors=err.messages)
