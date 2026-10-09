import sqlite3
from pprint import pprint


def sql_part() -> None:
    print("=== SQL (SQLite, та же схема подойдёт и для PostgreSQL) ===")
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            year INTEGER NOT NULL,
            author_id INTEGER NOT NULL REFERENCES authors(id)
        );
        CREATE TABLE loans (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL REFERENCES books(id),
            reader TEXT NOT NULL,
            returned INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    conn.executemany("INSERT INTO authors (name) VALUES (?)", [("Булгаков",), ("Толкин",), ("Сапковский",)])
    conn.executemany(
        "INSERT INTO books (title, year, author_id) VALUES (?, ?, ?)",
        [
            ("Мастер и Маргарита", 1967, 1),
            ("Собачье сердце", 1925, 1),
            ("Властелин колец", 1954, 2),
            ("Ведьмак", 1993, 3),
        ],
    )
    print("Фильтр и связь:")
    for row in conn.execute(
        """
        SELECT b.title, a.name, b.year
        FROM books b JOIN authors a ON a.id = b.author_id
        WHERE b.year >= 1950
        ORDER BY b.year
        """
    ):
        print(" ", row)
    print("Агрегация:")
    for row in conn.execute(
        """
        SELECT a.name, COUNT(b.id)
        FROM authors a LEFT JOIN books b ON b.author_id = a.id
        GROUP BY a.name
        ORDER BY COUNT(b.id) DESC
        """
    ):
        print(" ", row)
    conn.commit()
    try:
        conn.execute("BEGIN")
        conn.execute("INSERT INTO loans (book_id, reader) VALUES (1, 'Ира')")
        raise RuntimeError("сбой выдачи")
    except RuntimeError:
        conn.rollback()
        print("Транзакция откатилась, выдач:", conn.execute("SELECT COUNT(*) FROM loans").fetchone()[0])
    conn.close()


def document_part() -> None:
    print("=== Документы (модель MongoDB) ===")
    books = [
        {"title": "Мастер и Маргарита", "year": 1967, "author": {"name": "Булгаков"}, "tags": ["роман"]},
        {"title": "Властелин колец", "year": 1954, "author": {"name": "Толкин"}, "tags": ["фэнтези"]},
    ]
    books.append({"title": "Ведьмак", "year": 1993, "author": {"name": "Сапковский"}, "tags": ["фэнтези"], "isbn": "978-5-17-000000-0"})
    found = [book for book in books if book["year"] >= 1960 and "фэнтези" in book["tags"] or book["author"]["name"] == "Булгаков"]
    print("Поиск без миграции схемы, у третьей книги появился isbn:")
    pprint(found)


if __name__ == "__main__":
    sql_part()
    document_part()
