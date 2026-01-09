"""Initial migration - Create users, chats, messages, and settings tables

Revision ID: 001
Revises: 
Create Date: 2025-10-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_admin', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    
    # Create chats table
    op.create_table(
        'chats',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), default='New Chat'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True),
    )
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('chat_id', UUID(as_uuid=True), sa.ForeignKey('chats.id', ondelete='CASCADE'), nullable=False),
        sa.Column('human', sa.Text, nullable=False),
        sa.Column('bot', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    
    # Create settings table
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('ai_provider', sa.String(50), default='openai'),
        sa.Column('deny_words', sa.Text, default=''),
        sa.Column('max_tokens', sa.Integer, default=2000),
        sa.Column('temperature', sa.String(10), default='0.7'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('chats')
    op.drop_table('settings')
    op.drop_table('users')
