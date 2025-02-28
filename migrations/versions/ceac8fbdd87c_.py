"""empty message

Revision ID: ceac8fbdd87c
Revises: 
Create Date: 2020-05-03 22:42:56.087762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ceac8fbdd87c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('video',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('fps', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('log',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('video1_id', sa.Integer(), nullable=False),
    sa.Column('time_code1', sa.String(), nullable=False),
    sa.Column('video2_id', sa.Integer(), nullable=False),
    sa.Column('time_code2', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['video1_id'], ['video.id'], ),
    sa.ForeignKeyConstraint(['video2_id'], ['video.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('video_hash',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('video_id', sa.Integer(), nullable=False),
    sa.Column('hash', sa.String(), nullable=False),
    sa.Column('time_code', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['video_id'], ['video.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('video_hash')
    op.drop_table('log')
    op.drop_table('video')
    # ### end Alembic commands ###
