"""adds Requests table

Revision ID: 721393398844
Revises: b8d529888ca9
Create Date: 2019-04-16 14:00:23.295400

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '721393398844'
down_revision = 'b8d529888ca9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('membership_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['membership_id'], ['membership.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_requests_timestamp'), 'requests', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_requests_timestamp'), table_name='requests')
    op.drop_table('requests')
    # ### end Alembic commands ###
