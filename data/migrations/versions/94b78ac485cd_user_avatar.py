"""user_avatar

Revision ID: 94b78ac485cd
Revises: 0a05f8c783ca
Create Date: 2025-03-27 12:46:33.037515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '94b78ac485cd'
down_revision: Union[str, None] = '0a05f8c783ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('avatar_link', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.drop_column('user', 'avatar')
    op.drop_column('user', 'avatar_content_type')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('avatar_content_type', sa.VARCHAR(), nullable=True))
    op.add_column('user', sa.Column('avatar', sa.BLOB(), nullable=True))
    op.drop_column('user', 'avatar_link')
    # ### end Alembic commands ###
