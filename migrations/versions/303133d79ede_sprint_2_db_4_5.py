"""sprint 2 db 4.5

Revision ID: 303133d79ede
Revises: acddb38691ac
Create Date: 2020-01-25 22:35:24.464990

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '303133d79ede'
down_revision = 'acddb38691ac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_Complications_type'), 'Complications', ['type'], unique=False)
    op.drop_index('ix_\u0421omplications_type', table_name='Complications')
    op.add_column('IndicatorsDefs', sa.Column('id_value', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('IndicatorsDefs', 'id_value')
    op.create_index('ix_\u0421omplications_type', 'Complications', ['type'], unique=False)
    op.drop_index(op.f('ix_Complications_type'), table_name='Complications')
    # ### end Alembic commands ###
