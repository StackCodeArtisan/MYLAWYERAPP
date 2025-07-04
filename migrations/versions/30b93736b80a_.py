"""empty message

Revision ID: 30b93736b80a
Revises: 
Create Date: 2025-03-31 16:01:14.589505

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '30b93736b80a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('appointment_datetime', sa.DateTime(), nullable=False))
        batch_op.add_column(sa.Column('case_details', sa.Text(), nullable=False))
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=False))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.alter_column('client_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
        batch_op.alter_column('lawyer_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
        batch_op.create_index('ix_appointments_client', ['client_id'], unique=False)
        batch_op.create_index('ix_appointments_lawyer_status', ['lawyer_id', 'status'], unique=False)
        batch_op.drop_column('appointment_date')
        batch_op.drop_column('appointment_time')
        batch_op.drop_column('appointment_price')
        batch_op.drop_column('appointment_note')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('appointment_note', mysql.TEXT(), nullable=True))
        batch_op.add_column(sa.Column('appointment_price', mysql.FLOAT(), nullable=True))
        batch_op.add_column(sa.Column('appointment_time', mysql.TIME(), nullable=True))
        batch_op.add_column(sa.Column('appointment_date', sa.DATE(), nullable=True))
        batch_op.drop_index('ix_appointments_lawyer_status')
        batch_op.drop_index('ix_appointments_client')
        batch_op.alter_column('lawyer_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
        batch_op.alter_column('client_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
        batch_op.drop_column('created_at')
        batch_op.drop_column('status')
        batch_op.drop_column('case_details')
        batch_op.drop_column('appointment_datetime')

    # ### end Alembic commands ###
