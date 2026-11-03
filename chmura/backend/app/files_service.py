from sqlalchemy import func

from .models import File, FileVersion, Permission


class PermissionDenied(Exception):
    pass


def upload_file(db, storage, user, name, data):
    # szukamy pliku o tej nazwie, do którego ten użytkownik ma uprawnienia
    f = (
        db.query(File)
        .join(Permission, Permission.file_id == File.id)
        .filter(Permission.user_id == user.id, File.name == name)
        .first()
    )

    if f is None:
        # nowy plik: twórca dostaje komplet uprawnień
        f = File(name=name)
        db.add(f)
        db.flush()
        db.add(Permission(user_id=user.id, file_id=f.id,
                          can_read=True, can_write=True, can_update=True))
        version_no = 1
    else:
        perm = db.get(Permission, (user.id, f.id))
        if not perm.can_update:
            raise PermissionDenied()
        last = (db.query(func.max(FileVersion.version_no))
                  .filter_by(file_id=f.id).scalar() or 0)
        version_no = last + 1

    path = f"{f.id}/v{version_no}"
    storage.save(path, data)  # najpierw magazyn, potem baza

    v = FileVersion(file_id=f.id, version_no=version_no, blob_path=path,
                    size=len(data), uploaded_by=user.id)
    db.add(v)
    db.flush()
    f.current_version_id = v.id
    db.commit()
    return v