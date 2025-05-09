"""empty message

Revision ID: 077482317f35
Revises: 9d2dac02a814
Create Date: 2025-02-13 12:53:57.640350

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '077482317f35'
down_revision = '9d2dac02a814'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('image',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('image',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)

    # ### end Alembic commands ###
