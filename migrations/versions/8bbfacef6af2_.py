"""empty message

Revision ID: 8bbfacef6af2
Revises: c4cb3e547ed2
Create Date: 2025-02-19 13:13:56.638450

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8bbfacef6af2'
down_revision = 'c4cb3e547ed2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('historial_cambios', schema=None) as batch_op:
        batch_op.drop_column('datos_previos')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('historial_cambios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('datos_previos', mysql.JSON(), nullable=True))

    # ### end Alembic commands ###
