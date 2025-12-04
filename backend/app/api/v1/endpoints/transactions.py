from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.crud import crud_transaction
from app.db.session import get_db
from app.schemas.transaction import TransactionCreate, TransactionInDB, TransactionUpdate

router = APIRouter()


@router.post("/transactions/", response_model=TransactionInDB)
def create_new_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    return crud_transaction.create_transaction(db=db, transaction=transaction, user_id=1)


@router.get("/transactions/", response_model=List[TransactionInDB])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    transactions = crud_transaction.get_transactions(db, skip=skip, limit=limit)
    return transactions


@router.get("/transactions/grid", response_model=Dict[str, Any])
def get_transaction_grid(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("date", regex="^(date|description|amount)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """
    Grid endpoint with server-side pagination and sorting using raw SQL.
    Returns transactions with their category and tags.
    """
    offset = (page - 1) * size

    allowed_columns = {"date": "t.date", "description": "t.description", "amount": "t.amount"}
    order_column = allowed_columns.get(sort_by, "t.date")
    order_direction = "ASC" if sort_order == "asc" else "DESC"

    query = text(f"""
        SELECT
            t.id,
            t.description,
            t.amount,
            t.type,
            t.date,
            t.user_id,
            c.id as category_id,
            c.name as category_name,
            COALESCE(
                STRING_AGG(tg.name, ',' ORDER BY tg.name),
                ''
            ) as tags
        FROM transactions t
        INNER JOIN categories c ON t.category_id = c.id
        LEFT JOIN transaction_tags tt ON t.id = tt.transaction_id
        LEFT JOIN tags tg ON tt.tag_id = tg.id
        GROUP BY t.id, t.description, t.amount, t.type, t.date, t.user_id, c.id, c.name
        ORDER BY {order_column} {order_direction}
        LIMIT :limit OFFSET :offset
    """)

    count_query = text("SELECT COUNT(*) as total FROM transactions")

    result = db.execute(query, {"limit": size, "offset": offset})
    count_result = db.execute(count_query)

    rows = result.fetchall()
    total = count_result.scalar()

    items = []
    for row in rows:
        tag_list = [tag.strip() for tag in row.tags.split(',')] if row.tags else []
        items.append({
            "id": row.id,
            "description": row.description,
            "amount": float(row.amount),
            "type": row.type,
            "date": row.date.isoformat(),
            "user_id": row.user_id,
            "category_rel": {
                "id": row.category_id,
                "name": row.category_name
            },
            "tags": tag_list
        })

    return {
        "items": items,
        "total": total
    }


@router.get("/transactions/{transaction_id}", response_model=TransactionInDB)
def read_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = crud_transaction.get_transaction(db, transaction_id=transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put("/transactions/{transaction_id}", response_model=TransactionInDB)
def update_existing_transaction(
    transaction_id: int, transaction: TransactionUpdate, db: Session = Depends(get_db)
):
    db_transaction = crud_transaction.update_transaction(db, transaction_id, transaction)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction


@router.delete("/transactions/{transaction_id}", response_model=TransactionInDB)
def delete_existing_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = crud_transaction.delete_transaction(db, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction
