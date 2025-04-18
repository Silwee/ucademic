"""lesson

Revision ID: 989b3164454a
Revises: 9b93598985b2
Create Date: 2025-04-16 18:06:36.856744

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '989b3164454a'
down_revision: Union[str, None] = '9b93598985b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('section',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('sectionTitle', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['course.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_section_course_id'), 'section', ['course_id'], unique=False)
    op.create_index(op.f('ix_section_id'), 'section', ['id'], unique=False)
    op.create_index(op.f('ix_section_sectionTitle'), 'section', ['sectionTitle'], unique=False)
    op.create_table('lesson',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('free_preview', sa.Boolean(), nullable=False),
    sa.Column('link', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('section_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['section_id'], ['section.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lesson_duration'), 'lesson', ['duration'], unique=False)
    op.create_index(op.f('ix_lesson_free_preview'), 'lesson', ['free_preview'], unique=False)
    op.create_index(op.f('ix_lesson_id'), 'lesson', ['id'], unique=False)
    op.create_index(op.f('ix_lesson_section_id'), 'lesson', ['section_id'], unique=False)
    op.create_index(op.f('ix_lesson_title'), 'lesson', ['title'], unique=False)
    op.add_column('course', sa.Column('requirements', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('course', sa.Column('what_will_you_learn', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('course', sa.Column('rating', sa.Float(), nullable=True))
    op.add_column('course', sa.Column('students', sa.Integer(), nullable=True))
    op.add_column('course', sa.Column('duration', sa.Integer(), nullable=True))
    op.add_column('course', sa.Column('lessons', sa.Integer(), nullable=True))
    op.add_column('course', sa.Column('last_updated', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_course_duration'), 'course', ['duration'], unique=False)
    op.create_index(op.f('ix_course_last_updated'), 'course', ['last_updated'], unique=False)
    op.create_index(op.f('ix_course_lessons'), 'course', ['lessons'], unique=False)
    op.create_index(op.f('ix_course_rating'), 'course', ['rating'], unique=False)
    op.create_index(op.f('ix_course_students'), 'course', ['students'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_course_students'), table_name='course')
    op.drop_index(op.f('ix_course_rating'), table_name='course')
    op.drop_index(op.f('ix_course_lessons'), table_name='course')
    op.drop_index(op.f('ix_course_last_updated'), table_name='course')
    op.drop_index(op.f('ix_course_duration'), table_name='course')
    op.drop_column('course', 'last_updated')
    op.drop_column('course', 'lessons')
    op.drop_column('course', 'duration')
    op.drop_column('course', 'students')
    op.drop_column('course', 'rating')
    op.drop_column('course', 'what_will_you_learn')
    op.drop_column('course', 'requirements')
    op.drop_index(op.f('ix_lesson_title'), table_name='lesson')
    op.drop_index(op.f('ix_lesson_section_id'), table_name='lesson')
    op.drop_index(op.f('ix_lesson_id'), table_name='lesson')
    op.drop_index(op.f('ix_lesson_free_preview'), table_name='lesson')
    op.drop_index(op.f('ix_lesson_duration'), table_name='lesson')
    op.drop_table('lesson')
    op.drop_index(op.f('ix_section_sectionTitle'), table_name='section')
    op.drop_index(op.f('ix_section_id'), table_name='section')
    op.drop_index(op.f('ix_section_course_id'), table_name='section')
    op.drop_table('section')
    # ### end Alembic commands ###
