"""empty message

Revision ID: 182631751690
Revises: 077482317f35
Create Date: 2025-02-17 20:10:12.542558

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '182631751690'
down_revision = '077482317f35'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('description',
               existing_type=mysql.VARCHAR(length=400),
               type_=sa.String(length=700),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('description',
               existing_type=sa.String(length=700),
               type_=mysql.VARCHAR(length=400),
               existing_nullable=True)

    # ### end Alembic commands ###
