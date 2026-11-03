from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .auth import get_current_user
from .database import get_db
from .files_service import PermissionDenied, upload_file
from .models import File, FileVersion, Permission, User
from .storage import Storage

router = APIRouter()
storage = Storage()


@router.post("/files")
def upload(file: UploadFile,
           user: User = Depends(get_current_user),
           db: Session = Depends(get_db)):
    data = file.file.read()
    try:
        v = upload_file(db, storage, user, file.filename, data)
    except PermissionDenied:
        db.rollback()
        raise HTTPException(403, "Brak uprawnień do aktualizacji pliku")
    except Exception:
        db.rollback()
        raise HTTPException(500, "Błąd przesyłania pliku")
    return {"id": v.file_id, "name": file.filename, "version": v.version_no}


@router.get("/files")
def list_files(user: User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    rows = (
        db.query(File, FileVersion)
        .join(Permission, Permission.file_id == File.id)
        .join(FileVersion, FileVersion.id == File.current_version_id)
        .filter(Permission.user_id == user.id, Permission.can_read)
        .all()
    )
    return [{"id": f.id, "name": f.name, "size": v.size,
             "date": v.uploaded_at, "version": v.version_no}
            for f, v in rows]