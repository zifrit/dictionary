"""added relationships

Revision ID: 27cc4c88807f
Revises: 8dcaee74a30a
Create Date: 2025-03-21 22:37:44.440587

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "27cc4c88807f"
down_revision: Union[str, None] = "8dcaee74a30a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("topic", sa.Column("dictionary_id", sa.Integer(), nullable=False))
    op.create_foreign_key(
        "dictionary_topic_fk", "topic", "dictionary", ["dictionary_id"], ["id"]
    )
    op.add_column("words", sa.Column("topic_id", sa.Integer(), nullable=False))
    op.create_foreign_key("topic_words_fk", "words", "topic", ["topic_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("topic_words_fk", "words", type_="foreignkey")
    op.drop_column("words", "topic_id")
    op.drop_constraint("dictionary_topic_fk", "topic", type_="foreignkey")
    op.drop_column("topic", "dictionary_id")
    # ### end Alembic commands ###
