from typing_extensions import TypedDict

from fastapi import FastAPI, HTTPException

from models import (
    Category,
    CategoryCreate,
    Tag,
    Transaction,
    TransactionCreate,
    TransactionType,
    TransactionUpdate,
)

app = FastAPI(title="Practice 1.1 - Personal Finance API")


def _find_by_id(items: list, obj_id: int):
    for item in items:
        if item.id == obj_id:
            return item
    return None


# Временная БД
TEMP_CATEGORIES: list[Category] = [
    Category(id=1, name="Salary", tx_type=TransactionType.income),
    Category(id=2, name="Food", tx_type=TransactionType.expense),
    Category(id=3, name="Transport", tx_type=TransactionType.expense),
]

TEMP_TAGS: list[Tag] = [
    Tag(id=1, name="monthly"),
    Tag(id=2, name="card"),
    Tag(id=3, name="cash"),
]

TEMP_TRANSACTIONS: list[Transaction] = [
    Transaction(
        id=1,
        title="Salary for March",
        amount=120000,
        tx_type=TransactionType.income,
        category=TEMP_CATEGORIES[0],
        tags=[TEMP_TAGS[0], TEMP_TAGS[1]],
        comment="Main job",
    ),
    Transaction(
        id=2,
        title="Groceries",
        amount=3500,
        tx_type=TransactionType.expense,
        category=TEMP_CATEGORIES[1],
        tags=[TEMP_TAGS[1]],
    ),
    Transaction(
        id=3,
        title="Metro",
        amount=75,
        tx_type=TransactionType.expense,
        category=TEMP_CATEGORIES[2],
        tags=[TEMP_TAGS[2]],
    ),
]


@app.get("/")
def hello() -> str:
    return "Hello, Personal Finance API!"


@app.get("/transactions_list")
def transactions_list() -> list[Transaction]:
    return TEMP_TRANSACTIONS


@app.get("/transaction/{transaction_id}")
def transaction_get(transaction_id: int) -> Transaction:
    transaction = _find_by_id(TEMP_TRANSACTIONS, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.post("/transaction")
def transaction_create(
    payload: TransactionCreate,
) -> TypedDict("Response", {"status": int, "data": Transaction}):
    category = _find_by_id(TEMP_CATEGORIES, payload.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    tags = []
    for tag_id in payload.tag_ids:
        tag = _find_by_id(TEMP_TAGS, tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail=f"Tag with id={tag_id} not found")
        tags.append(tag)

    next_id = max((tx.id for tx in TEMP_TRANSACTIONS), default=0) + 1
    tx = Transaction(
        id=next_id,
        title=payload.title,
        amount=payload.amount,
        tx_type=payload.tx_type,
        category=category,
        tags=tags,
        comment=payload.comment,
    )
    TEMP_TRANSACTIONS.append(tx)
    return {"status": 200, "data": tx}


@app.put("/transaction/{transaction_id}")
def transaction_update(transaction_id: int, payload: TransactionUpdate) -> Transaction:
    transaction = _find_by_id(TEMP_TRANSACTIONS, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    data = payload.model_dump(exclude_unset=True)

    if "category_id" in data:
        category = _find_by_id(TEMP_CATEGORIES, data["category_id"])
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        transaction.category = category

    if "tag_ids" in data:
        tags = []
        for tag_id in data["tag_ids"]:
            tag = _find_by_id(TEMP_TAGS, tag_id)
            if not tag:
                raise HTTPException(status_code=404, detail=f"Tag with id={tag_id} not found")
            tags.append(tag)
        transaction.tags = tags

    for field in ["title", "amount", "tx_type", "comment"]:
        if field in data:
            setattr(transaction, field, data[field])

    return transaction


@app.delete("/transaction/delete/{transaction_id}")
def transaction_delete(transaction_id: int) -> dict[str, bool]:
    transaction = _find_by_id(TEMP_TRANSACTIONS, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    TEMP_TRANSACTIONS.remove(transaction)
    return {"ok": True}


@app.get("/categories_list")
def categories_list() -> list[Category]:
    return TEMP_CATEGORIES


@app.get("/category/{category_id}")
def category_get(category_id: int) -> Category:
    category = _find_by_id(TEMP_CATEGORIES, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@app.post("/category")
def category_create(
    payload: CategoryCreate,
) -> TypedDict("Response", {"status": int, "data": Category}):
    next_id = max((c.id for c in TEMP_CATEGORIES), default=0) + 1
    category = Category(id=next_id, name=payload.name, tx_type=payload.tx_type)
    TEMP_CATEGORIES.append(category)
    return {"status": 200, "data": category}
