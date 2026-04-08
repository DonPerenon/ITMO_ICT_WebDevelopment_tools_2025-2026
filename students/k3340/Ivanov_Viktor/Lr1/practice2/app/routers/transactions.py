from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.connection import get_session
from app.models import (
    Category,
    CategoryRead,
    Tag,
    TagRead,
    Transaction,
    TransactionCreate,
    TransactionRead,
    TransactionTagLink,
    TransactionTagRead,
    TransactionUpdate,
    User,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def _serialize_transaction(session: Session, tx: Transaction) -> TransactionRead:
    category = session.get(Category, tx.category_id) if tx.category_id else None
    links = session.exec(
        select(TransactionTagLink).where(TransactionTagLink.transaction_id == tx.id)
    ).all()

    tags: list[TransactionTagRead] = []
    for link in links:
        tag = session.get(Tag, link.tag_id)
        if tag:
            tags.append(
                TransactionTagRead(
                    tag=TagRead(id=tag.id, name=tag.name, user_id=tag.user_id),
                    priority=link.priority,
                    note=link.note,
                )
            )

    return TransactionRead(
        id=tx.id,
        title=tx.title,
        amount=tx.amount,
        tx_type=tx.tx_type,
        occurred_at=tx.occurred_at,
        description=tx.description,
        user_id=tx.user_id,
        category_id=tx.category_id,
        category=(
            CategoryRead(
                id=category.id,
                name=category.name,
                tx_type=category.tx_type,
                user_id=category.user_id,
            )
            if category
            else None
        ),
        tags=tags,
    )


@router.get("", response_model=list[TransactionRead])
def transactions_list(session: Session = Depends(get_session)) -> list[TransactionRead]:
    items = session.exec(select(Transaction)).all()
    return [_serialize_transaction(session, tx) for tx in items]


@router.get("/{transaction_id}", response_model=TransactionRead)
def transactions_get(transaction_id: int, session: Session = Depends(get_session)) -> TransactionRead:
    tx = session.get(Transaction, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return _serialize_transaction(session, tx)


@router.post("", response_model=TransactionRead, status_code=201)
def transactions_create(
    payload: TransactionCreate,
    session: Session = Depends(get_session),
) -> TransactionRead:
    user = session.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.category_id:
        category = session.get(Category, payload.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        if category.user_id != payload.user_id:
            raise HTTPException(status_code=400, detail="Category does not belong to user")

    tx = Transaction(
        title=payload.title,
        amount=payload.amount,
        tx_type=payload.tx_type,
        occurred_at=payload.occurred_at or datetime.utcnow(),
        description=payload.description,
        user_id=payload.user_id,
        category_id=payload.category_id,
    )
    session.add(tx)
    session.commit()
    session.refresh(tx)

    for item in payload.tag_links:
        tag = session.get(Tag, item.tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail=f"Tag {item.tag_id} not found")
        if tag.user_id != payload.user_id:
            raise HTTPException(status_code=400, detail="Tag does not belong to user")

        session.add(
            TransactionTagLink(
                transaction_id=tx.id,
                tag_id=item.tag_id,
                priority=item.priority,
                note=item.note,
            )
        )

    session.commit()
    return _serialize_transaction(session, tx)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def transactions_update(
    transaction_id: int,
    payload: TransactionUpdate,
    session: Session = Depends(get_session),
) -> TransactionRead:
    tx = session.get(Transaction, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    updates = payload.model_dump(exclude_unset=True)

    if "category_id" in updates and updates["category_id"] is not None:
        category = session.get(Category, updates["category_id"])
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        if category.user_id != tx.user_id:
            raise HTTPException(status_code=400, detail="Category does not belong to user")

    tag_links_payload = updates.pop("tag_links", None)

    for key, value in updates.items():
        setattr(tx, key, value)

    session.add(tx)

    if tag_links_payload is not None:
        old_links = session.exec(
            select(TransactionTagLink).where(TransactionTagLink.transaction_id == tx.id)
        ).all()
        for link in old_links:
            session.delete(link)

        for item in tag_links_payload:
            tag = session.get(Tag, item["tag_id"])
            if not tag:
                raise HTTPException(status_code=404, detail=f"Tag {item['tag_id']} not found")
            if tag.user_id != tx.user_id:
                raise HTTPException(status_code=400, detail="Tag does not belong to user")

            session.add(
                TransactionTagLink(
                    transaction_id=tx.id,
                    tag_id=item["tag_id"],
                    priority=item["priority"],
                    note=item.get("note"),
                )
            )

    session.commit()
    session.refresh(tx)
    return _serialize_transaction(session, tx)


@router.delete("/{transaction_id}")
def transactions_delete(
    transaction_id: int,
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    tx = session.get(Transaction, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    links = session.exec(
        select(TransactionTagLink).where(TransactionTagLink.transaction_id == tx.id)
    ).all()
    for link in links:
        session.delete(link)

    session.delete(tx)
    session.commit()
    return {"ok": True}
