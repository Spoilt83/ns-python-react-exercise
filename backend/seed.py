import os
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), './app')))

from app.db.base import Base
from app.db.session import engine
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.tag import Tag

from app.core.config import settings

def load_seed_data():
    seed_data_path = os.path.join(os.path.dirname(__file__), '..', 'data')

    with open(os.path.join(seed_data_path, 'categories.json'), 'r') as f:
        categories = json.load(f)

    with open(os.path.join(seed_data_path, 'transactions.json'), 'r') as f:
        transactions = json.load(f)

    return categories, transactions

def seed_db():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("Clearing existing data...")
        db.execute(text("TRUNCATE TABLE transactions, categories, tags, transaction_tags RESTART IDENTITY CASCADE"))
        db.commit()

        print("Loading seed data from centralized JSON files...")
        categories_data, transactions_data = load_seed_data()

        print("Seeding database with initial data...")

        category_objects = {}
        for cat_name in categories_data:
            category = Category(name=cat_name)
            db.add(category)
            category_objects[cat_name] = category
        db.commit()

        for cat_name, category_obj in category_objects.items():
            db.refresh(category_obj)

        category_name_to_id_map = {cat_name: category_obj.id for cat_name, category_obj in category_objects.items()}

        print("Creating tags...")
        tag_names = ["work", "travel", "reimbursable", "recurring", "urgent", "personal"]
        tag_objects = {}
        for tag_name in tag_names:
            tag = Tag(name=tag_name)
            db.add(tag)
            tag_objects[tag_name] = tag
        db.commit()

        for tag_name, tag_obj in tag_objects.items():
            db.refresh(tag_obj)

        for idx, data in enumerate(transactions_data):
            transaction_data = {
                "description": data["description"],
                "amount": data["amount"],
                "type": data["type"],
                "category_id": category_name_to_id_map[data["category"]],
                "user_id": data["user_id"],
                "date": datetime.fromisoformat(data["date"])
            }
            transaction = Transaction(**transaction_data)

            if idx % 3 == 0:
                transaction.tags.append(tag_objects["work"])
            if idx % 4 == 0:
                transaction.tags.append(tag_objects["reimbursable"])
            if idx % 5 == 0:
                transaction.tags.append(tag_objects["recurring"])
            if data["type"] == "debit" and idx % 7 == 0:
                transaction.tags.append(tag_objects["travel"])

            db.add(transaction)
        db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
