"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2020-11-17 22:22:09.511306

"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'product',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asin', sa.VARCHAR(length=10), nullable=False),
        sa.Column('title', sa.VARCHAR(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asin'))
    op.create_table(
        'review',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asin', sa.VARCHAR(length=10), nullable=False),
        sa.Column('title', sa.VARCHAR(), nullable=False),
        sa.Column('body', sa.TEXT(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(('product_id', ), ['product.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'))


def downgrade():
    op.drop_table('review')
    op.drop_table('product')
