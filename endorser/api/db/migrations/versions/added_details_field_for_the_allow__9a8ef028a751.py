"""Added details field for the /allow/ endpoints

Revision ID: 9a8ef028a751
Revises: fb66f2d55aee
Create Date: 2024-02-22 19:49:54.326215

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '9a8ef028a751'
down_revision = 'fb66f2d55aee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('allowedcredentialdefinition', sa.Column('details', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('allowedpublicdid', sa.Column('details', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('allowedschema', sa.Column('details', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('allowedschema', 'details')
    op.drop_column('allowedpublicdid', 'details')
    op.drop_column('allowedcredentialdefinition', 'details')
    # ### end Alembic commands ###