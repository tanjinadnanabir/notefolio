# ┌──────────────────────────────────┐
# │              notes               │
# ├──────────────────────────────────┤
# │ id                               │
# │ user_id                          │
# │ folder_id                        │
# │ title                            │
# │ content                          │
# │ excerpt                          │
# │ is_pinned                        │
# │ is_archived                      │
# │ is_favorite                      │
# │ color                            │
# │ status                           │
# │ created_at                       │
# │ updated_at                       │
# │ deleted_at                       │
# └──────────────────────────────────┘

# User
#  │
#  └───────< Notes >─────── Folder

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    folder_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("folders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    excerpt: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    is_pinned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_favorite: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    color: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="notes",
    )

    folder = relationship(
        "Folder",
        back_populates="notes",
    )
    

# import uuid
# from datetime import datetime

# from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from app.db.database import Base


# class Note(Base):
#     __tablename__ = "notes"

#     id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#     )

#     owner_id: Mapped[uuid.UUID] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False,
#         index=True,
#     )

#     folder_id: Mapped[uuid.UUID | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("folders.id", ondelete="SET NULL"),
#         nullable=True,
#         index=True,
#     )

#     title: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     content: Mapped[str] = mapped_column(
#         Text,
#         nullable=False,
#         default="",
#     )

#     content_type: Mapped[str] = mapped_column(
#         String(20),
#         nullable=False,
#         default="markdown",
#     )

#     is_pinned: Mapped[bool] = mapped_column(
#         Boolean,
#         default=False,
#         nullable=False,
#         index=True,
#     )

#     is_archived: Mapped[bool] = mapped_column(
#         Boolean,
#         default=False,
#         nullable=False,
#         index=True,
#     )

#     is_deleted: Mapped[bool] = mapped_column(
#         Boolean,
#         default=False,
#         nullable=False,
#         index=True,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         server_default=func.now(),
#         nullable=False,
#     )

#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         server_default=func.now(),
#         onupdate=func.now(),
#         nullable=False,
#     )

#     deleted_at: Mapped[datetime | None] = mapped_column(
#         DateTime(timezone=True),
#         nullable=True,
#     )

#     owner: Mapped["User"] = relationship(
#         back_populates="notes",
#     )

#     folder: Mapped["Folder | None"] = relationship(
#         back_populates="notes",
#     )