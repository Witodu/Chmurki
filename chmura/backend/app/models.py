from datetime import datetime

from sqlalchemy import (
    BigInteger, Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    # use_alter: files i file_versions wskazują na siebie nawzajem,
    # więc ten klucz jest dodawany dopiero po utworzeniu obu tabel
    current_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("file_versions.id", use_alter=True, name="fk_files_current_version"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class FileVersion(Base):
    __tablename__ = "file_versions"
    __table_args__ = (UniqueConstraint("file_id", "version_no"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"))
    version_no: Mapped[int]
    blob_path: Mapped[str] = mapped_column(String(255))
    size: Mapped[int] = mapped_column(BigInteger)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Permission(Base):
    __tablename__ = "permissions"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"), primary_key=True)
    can_read: Mapped[bool] = mapped_column(Boolean, default=False)
    can_write: Mapped[bool] = mapped_column(Boolean, default=False)
    can_update: Mapped[bool] = mapped_column(Boolean, default=False)


class LogEntry(Base):
    __tablename__ = "logbook"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    operation: Mapped[str] = mapped_column(String(30))
    file_id: Mapped[int | None] = mapped_column(ForeignKey("files.id"), nullable=True)
    result: Mapped[str] = mapped_column(String(20))