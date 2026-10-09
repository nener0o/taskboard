"""Тот же сценарий на настоящем MongoDB: mongodb://localhost:27017"""

from pprint import pprint

from pymongo import MongoClient


def main() -> None:
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
    db = client.fullstack_labs
    db.books.drop()
    db.books.insert_many(
        [
            {"title": "Мастер и Маргарита", "year": 1967, "author": {"name": "Булгаков"}, "tags": ["роман"]},
            {"title": "Властелин колец", "year": 1954, "author": {"name": "Толкин"}, "tags": ["фэнтези"]},
        ]
    )
    db.books.insert_one(
        {"title": "Ведьмак", "year": 1993, "author": {"name": "Сапковский"}, "tags": ["фэнтези"], "isbn": "978-5-17-000000-0"}
    )
    found = list(db.books.find({"$or": [{"year": {"$gte": 1960}, "tags": "фэнтези"}, {"author.name": "Булгаков"}]}, {"_id": 0}).sort("year", 1))
    pprint(found)
    client.close()


if __name__ == "__main__":
    main()
