"""initial migration.

Revision ID: 764bfa5fa61e
Revises: 
Create Date: 2024-09-14 19:35:34.828085

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '764bfa5fa61e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('readers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('books',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('author', sa.String(length=50), nullable=False),
    sa.Column('reader_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['reader_id'], ['readers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('books')
    op.drop_table('readers')
    # ### end Alembic commands ###
