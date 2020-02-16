""" 

Revision ID: ad3c9211c3a9
Revises: ee8100679397
Create Date: 2020-02-16 16:27:17.022482

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad3c9211c3a9'
down_revision = 'ee8100679397'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Indicators', sa.Column('type', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Indicators', 'type')
    # ### end Alembic commands ###
