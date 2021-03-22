"""empty message

Revision ID: 5718a422eab5
Revises: 1f836d093701
Create Date: 2020-08-23 00:53:17.065574

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '5718a422eab5'
down_revision = '1f836d093701'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'user', 'role', ['role_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_ = 'foreignkey')
    # ### end Alembic commands ###
