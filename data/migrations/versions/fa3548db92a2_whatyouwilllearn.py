"""whatyouwilllearn

Revision ID: fa3548db92a2
Revises: 8fa03b0c4391
Create Date: 2025-04-18 23:14:45.945861

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'fa3548db92a2'
down_revision: Union[str, None] = '8fa03b0c4391'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('course', sa.Column('what_you_will_learn', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.drop_column('course', 'what_will_you_learn')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('course', sa.Column('what_will_you_learn', sa.VARCHAR(), nullable=True))
    op.drop_column('course', 'what_you_will_learn')
    # ### end Alembic commands ###
