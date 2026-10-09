SELECT b.title, a.name
FROM books b
JOIN authors a ON a.id = b.author_id
WHERE b.year >= 2000
ORDER BY b.year;

SELECT a.name, COUNT(b.id) AS books
FROM authors a
LEFT JOIN books b ON b.author_id = a.id
GROUP BY a.name
ORDER BY books DESC;

BEGIN;
INSERT INTO loans (book_id, reader, returned) VALUES (1, 'Ира', 0);
ROLLBACK;
