"""sprint 2 db 4.8

Revision ID: 5d7c8ee54269
Revises: afc6454db7c7
Create Date: 2020-01-26 19:56:03.829362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d7c8ee54269'
down_revision = 'afc6454db7c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    """
    op.create_table('Histories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('clinic', sa.Integer(), nullable=True),
    sa.Column('hist_number', sa.String(length=100), nullable=True),
    sa.Column('time_created', sa.DateTime(), nullable=True),
    sa.Column('patient', sa.Integer(), nullable=True),
    sa.Column('research_group', sa.Integer(), nullable=True),
    sa.Column('time_research_in', sa.DateTime(), nullable=True),
    sa.Column('time_research_out', sa.DateTime(), nullable=True),
    sa.Column('reason', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['clinic'], ['Clinics.id'], ),
    sa.ForeignKeyConstraint(['patient'], ['Patients.id'], ),
    sa.ForeignKeyConstraint(['reason'], ['Reasons.id'], ),
    sa.ForeignKeyConstraint(['research_group'], ['ResearchGroups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Diagnoses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('clinic', sa.Integer(), nullable=True),
    sa.Column('history', sa.Integer(), nullable=True),
    sa.Column('patient', sa.Integer(), nullable=True),
    sa.Column('diagnose', sa.Integer(), nullable=True),
    sa.Column('side_damage', sa.String(length=100), nullable=True),
    sa.Column('date_created', sa.Date(), nullable=True),
    sa.Column('prothes', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['clinic'], ['Clinics.id'], ),
    sa.ForeignKeyConstraint(['diagnose'], ['Diagnoses.id'], ),
    sa.ForeignKeyConstraint(['history'], ['Histories.id'], ),
    sa.ForeignKeyConstraint(['patient'], ['Patients.id'], ),
    sa.ForeignKeyConstraint(['prothes'], ['Prosthesis.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    """
    op.create_table('ProfilesAnswers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('profile', sa.Integer(), nullable=True),
    sa.Column('profile_item', sa.Integer(), nullable=True),
    sa.Column('response', sa.String(length=100), nullable=True),
    sa.Column('response_value', sa.Numeric(), nullable=True),
    sa.ForeignKeyConstraint(['profile_item'], ['ProfileItems.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    #op.create_foreign_key(None, 'ProfilesAnswers', 'Profiles', ['profile'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'ProfilesAnswers', type_='foreignkey')
    op.drop_table('Diagnoses')
    op.drop_table('Histories')
    # ### end Alembic commands ###
