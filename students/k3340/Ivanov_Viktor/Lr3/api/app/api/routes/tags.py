from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import Tag, User
from app.schemas.tags import TagCreate, TagRead, TagUpdate

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=list[TagRead])
def tags_list(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Tag]:
    return session.exec(select(Tag).where(Tag.user_id == current_user.id)).all()


@router.get("/{tag_id}", response_model=TagRead)
def tags_get(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Tag:
    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.post("", response_model=TagRead, status_code=201)
def tags_create(
    payload: TagCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Tag:
    tag = Tag(name=payload.name, user_id=current_user.id)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.patch("/{tag_id}", response_model=TagRead)
def tags_update(
    tag_id: int,
    payload: TagUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Tag:
    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tag not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(tag, key, value)

    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.delete("/{tag_id}")
def tags_delete(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    tag = session.get(Tag, tag_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tag not found")

    session.delete(tag)
    session.commit()
    return {"ok": True}
