"""empty message

Revision ID: 9d2dac02a814
Revises: ffc82788e1df
Create Date: 2025-02-13 12:52:56.401869

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9d2dac02a814'
down_revision = 'ffc82788e1df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('description',
               existing_type=mysql.VARCHAR(length=255),
               type_=sa.String(length=400),
               existing_nullable=True)
        batch_op.alter_column('image',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('image',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)
        batch_op.alter_column('description',
               existing_type=sa.String(length=400),
               type_=mysql.VARCHAR(length=255),
               existing_nullable=True)

    # ### end Alembic commands ###
