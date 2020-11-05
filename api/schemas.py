from api import models


class Product(models.ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Product


class Review(models.ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Review
        include_fk = True
