"""enable pgvector extension

Revision ID: 5a8aca291a9f
Revises: 00ee7b1822f7
Create Date: 2026-02-20 16:02:46.099544

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '5a8aca291a9f'
down_revision = '00ee7b1822f7'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")


def downgrade():
    op.execute("DROP EXTENSION IF EXISTS vector;")
