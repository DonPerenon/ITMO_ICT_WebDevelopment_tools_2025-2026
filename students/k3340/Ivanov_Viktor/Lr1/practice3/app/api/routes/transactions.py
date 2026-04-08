from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import Category, Tag, Transaction, TransactionTagLink, User
from app.schemas.categories import CategoryRead
from app.schemas.transactions import (
    TagWithMeta,
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def _serialize_transaction(session: Session, tx: Transaction) -> TransactionRead:
    category_obj = session.get(Category, tx.category_id) if tx.category_id else None
    links = session.exec(
        select(TransactionTagLink).where(TransactionTagLink.transaction_id == tx.id)
    ).all()

    tags: list[TagWithMeta] = []
    for link in links:
        tag = session.get(Tag, link.tag_id)
        if tag:
            tags.append(
                TagWithMeta(
                    id=tag.id,
                    name=tag.name,
                    relevance=link.relevance,
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
                id=category_obj.id,
                name=category_obj.name,
                tx_type=category_obj.tx_type,
                user_id=category_obj.user_id,
            )
            if category_obj
            else None
        ),
        tags=tags,
    )


@router.get("", response_model=list[TransactionRead])
def transactions_list(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[TransactionRead]:
    transactions = session.exec(
        select(Transaction).where(Transaction.user_id == current_user.id)
    ).all()
    return [_serialize_transaction(session, tx) for tx in transactions]


@router.get("/{transaction_id}", response_model=TransactionRead)
def transactions_get(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TransactionRead:
    tx = session.get(Transaction, transaction_id)
    if not tx or tx.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return _serialize_transaction(session, tx)


@router.post("", response_model=TransactionRead, status_code=201)
def transactions_create(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TransactionRead:
    if payload.category_id is not None:
        category = session.get(Category, payload.category_id)
        if not category or category.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Category not found")

    tx = Transaction(
        title=payload.title,
        amount=payload.amount,
        tx_type=payload.tx_type,
        occurred_at=payload.occurred_at or datetime.utcnow(),
        description=payload.description,
        user_id=current_user.id,
        category_id=payload.category_id,
    )
    session.add(tx)
    session.commit()
    session.refresh(tx)

    for item in payload.tags:
        tag = session.get(Tag, item.tag_id)
        if not tag or tag.user_id != current_user.id:
            raise HTTPException(status_code=404, detail=f"Tag {item.tag_id} not found")

        session.add(
            TransactionTagLink(
                transaction_id=tx.id,
                tag_id=item.tag_id,
                relevance=item.relevance,
                note=item.note,
            )
        )

    session.commit()
    return _serialize_transaction(session, tx)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def transactions_update(
    transaction_id: int,
    payload: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TransactionRead:
    tx = session.get(Transaction, transaction_id)
    if not tx or tx.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    updates = payload.model_dump(exclude_unset=True)

    if "category_id" in updates and updates["category_id"] is not None:
        category = session.get(Category, updates["category_id"])
        if not category or category.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Category not found")

    tags_payload = updates.pop("tags", None)

    for key, value in updates.items():
        setattr(tx, key, value)

    session.add(tx)

    if tags_payload is not None:
        existing_links = session.exec(
            select(TransactionTagLink).where(TransactionTagLink.transaction_id == tx.id)
        ).all()
        for link in existing_links:
            session.delete(link)

        for item in tags_payload:
            tag = session.get(Tag, item["tag_id"])
            if not tag or tag.user_id != current_user.id:
                raise HTTPException(status_code=404, detail=f"Tag {item['tag_id']} not found")

            session.add(
                TransactionTagLink(
                    transaction_id=tx.id,
                    tag_id=item["tag_id"],
                    relevance=item["relevance"],
                    note=item.get("note"),
                )
            )

    session.commit()
    session.refresh(tx)
    return _serialize_transaction(session, tx)


@router.delete("/{transaction_id}")
def transactions_delete(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    tx = session.get(Transaction, transaction_id)
    if not tx or tx.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    links = session.exec(
        select(TransactionTagLink).where(TransactionTagLink.transaction_id == tx.id)
    ).all()
    for link in links:
        session.delete(link)

    session.delete(tx)
    session.commit()
    return {"ok": True}
