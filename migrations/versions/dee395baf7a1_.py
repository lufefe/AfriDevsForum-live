"""empty message

Revision ID: dee395baf7a1
Revises: 9743d48ded13
Create Date: 2020-08-23 00:35:48.743005

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'dee395baf7a1'
down_revision = '9743d48ded13'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('role_id', sa.Integer(), nullable = True))
    op.create_foreign_key(None, 'user', 'roles', ['role_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_ = 'foreignkey')
    op.drop_column('user', 'role_id')
    # ### end Alembic commands ###
