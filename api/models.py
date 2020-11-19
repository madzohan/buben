from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# Define the database object
db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()


class Product(db.Model):
    id = db.Column(db.INT, primary_key=True)
    asin = db.Column(db.VARCHAR(length=10), nullable=False, unique=True)
    title = db.Column(db.VARCHAR, nullable=False)
    reviews = db.relationship("Review", backref="product", lazy="dynamic")

    def __repr__(self):
        return "<Product asin={}>".format(self.asin)


class Review(db.Model):
    id = db.Column(db.INT, primary_key=True)
    asin = db.Column(db.VARCHAR(length=10), nullable=False)
    title = db.Column(db.VARCHAR, nullable=False)
    body = db.Column(db.TEXT, nullable=False)
    product_id = db.Column(db.INT, db.ForeignKey("product.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return "<Review id={} title={}>".format(self.id, self.title)
