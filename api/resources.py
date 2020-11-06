from flask import jsonify
from flask_restful import Resource, Api
from webargs import fields
from webargs.flaskparser import use_args, use_kwargs

from api import models, schemas


class Product(Resource):
    @use_kwargs({"reviews_per_page": fields.Int(missing=5),
                 "page": fields.Int(missing=1)}, location="query")
    def get(self, product_id: int, page: int, reviews_per_page: int):
        reviews = models.Review.query.filter_by(product_id=product_id).order_by(
            models.Review.id.asc()).paginate(page, reviews_per_page).items
        product_dump = schemas.Product().dump(reviews[0].product)
        product_dump["reviews"] = schemas.Review(many=True).dump(reviews)
        return jsonify({"products": [product_dump]})


class Review(Resource):
    def get(self, product_id: int, review_id: int):
        return

    @use_args(schemas.Review())
    def put(self, product_id: int):
        return


api = Api(prefix='/api/v1')
api.add_resource(Product, "/products/<int:product_id>")
api.add_resource(Review,
                 "/products/<int:product_id>/reviews/<int:review_id>",
                 "/products/<int:product_id>/reviews/create.json")
