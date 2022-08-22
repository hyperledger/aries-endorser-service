"""initial-db-tables

Revision ID: d925cb39480e
Revises:
Create Date: 2022-05-05 11:45:18.781171

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d925cb39480e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "contact",
        sa.Column(
            "contact_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("author_status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("endorse_status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("connection_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("connection_protocol", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "connection_alias", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("public_did", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("their_label", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("contact_id"),
    )
    op.create_table(
        "endorserequest",
        sa.Column(
            "endorse_request_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("transaction_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("connection_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("endorser_did", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("author_did", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "transaction_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("ledger_txn", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("endorse_request_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("endorserequest")
    op.drop_table("contact")
    # ### end Alembic commands ###
