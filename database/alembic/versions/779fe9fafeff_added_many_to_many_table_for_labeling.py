"""added many to many table for labeling 

Revision ID: 779fe9fafeff
Revises: 911d0c388567
Create Date: 2018-06-09 17:27:50.302406

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '779fe9fafeff'
down_revision = '911d0c388567'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('labeled_image_association',
    sa.Column('labeling_session_id', sa.TEXT(), nullable=True),
    sa.Column('labeled_image_id', sa.TEXT(), nullable=True),
    sa.ForeignKeyConstraint(['labeled_image_id'], ['labeled_image.id'], ),
    sa.ForeignKeyConstraint(['labeling_session_id'], ['labeling_session.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('labeled_image_association')
    # ### end Alembic commands ###