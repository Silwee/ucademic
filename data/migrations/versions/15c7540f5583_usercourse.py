"""usercourse

Revision ID: 15c7540f5583
Revises: 60e4b8670e95
Create Date: 2025-04-24 18:00:21.662256

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '15c7540f5583'
down_revision: Union[str, None] = '60e4b8670e95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###

    op.create_table('usercourselink',
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['course.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('course_id', 'user_id')
    )
    op.create_index(op.f('ix_usercourselink_course_id'), 'usercourselink', ['course_id'], unique=False)
    op.create_index(op.f('ix_usercourselink_user_id'), 'usercourselink', ['user_id'], unique=False)
    op.add_column('course', sa.Column('instructor_id', sa.Uuid(), nullable=True,))
    op.drop_index('ix_course_duration', table_name='course')
    op.drop_index('ix_course_lessons', table_name='course')
    op.drop_index('ix_course_students', table_name='course')
    op.create_index(op.f('ix_course_instructor_id'), 'course', ['instructor_id'], unique=False)
    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.create_foreign_key('course', 'user', ['instructor_id'], ['id'])
    op.drop_column('course', 'students')
    op.drop_column('course', 'lessons')
    op.drop_column('course', 'duration')
    op.add_column('user', sa.Column('is_instructor', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_user_is_instructor'), 'user', ['is_instructor'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_is_instructor'), table_name='user')
    op.drop_column('user', 'is_instructor')
    op.add_column('course', sa.Column('duration', sa.INTEGER(), nullable=True))
    op.add_column('course', sa.Column('lessons', sa.INTEGER(), nullable=True))
    op.add_column('course', sa.Column('students', sa.INTEGER(), nullable=True))
    op.drop_constraint(None, 'course', type_='foreignkey')
    op.drop_index(op.f('ix_course_instructor_id'), table_name='course')
    op.create_index('ix_course_students', 'course', ['students'], unique=False)
    op.create_index('ix_course_lessons', 'course', ['lessons'], unique=False)
    op.create_index('ix_course_duration', 'course', ['duration'], unique=False)
    op.drop_column('course', 'instructor_id')
    op.drop_index(op.f('ix_usercourselink_user_id'), table_name='usercourselink')
    op.drop_index(op.f('ix_usercourselink_course_id'), table_name='usercourselink')
    op.drop_table('usercourselink')
    # ### end Alembic commands ###
