import re

import mysql.connector


class Book:
    def __init__(self, isbn, title, pages=None, publish_date=None, publisher=None, cover=None, description=None,
                 price=None, available=None, authors_names=None, genre_name=None):
        self.isbn = isbn
        self.title = title
        self.pages = pages
        self.publish_date = publish_date
        self.publisher = Publisher(publisher)
        self.cover = cover
        self.description = description
        self.price = price
        self.available = available

        self.authors = []
        for author_name in authors_names:
            self.authors.append(Author(author_name))
        self.genre = Genre(genre_name)

    def __str__(self):
        authors = ", ".join(str(author) for author in self.authors)
        return f"ISBN: {self.isbn}\n" \
               f"Title: {self.title}\n" \
               f"Pages: {self.pages}\n" \
               f"Publish Date: {self.publish_date}\n" \
               f"Publisher: {self.publisher}\n" \
               f"Description: {self.description}\n" \
               f"Price: {self.price}\n" \
               f"Available: {self.available}\n" \
               f"Authors: {authors}\n" \
               f"Genre: {self.genre}"


class Author:
    def __init__(self, name, wiki_link=None, bio=None, photo=None):
        self.name = name
        self.wiki_link = wiki_link
        self.bio = bio
        self.photo = photo

    def __str__(self):
        return self.name


class Genre:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class Publisher:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

    def __del__(self):
        self.connection.close()

    def get_author_id(self, author: Author):
        cursor = self.connection.cursor()
        query = "SELECT id FROM author WHERE name = %s"
        cursor.execute(query, (author.name,))
        result = cursor.fetchall()
        cursor.close()
        return result[0][0] if result else None

    def insert_authors(self, authors: list):
        # print(author)
        for author in authors:
            author_id = self.get_author_id(author)
            if author_id:
                print(author_id)
                yield author_id
            else:
                cursor = self.connection.cursor()
                query = "INSERT INTO author (name, wiki_link, bio, photo) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (author.name, author.wiki_link, author.bio, author.photo))
                author_id = cursor.lastrowid
                self.connection.commit()
                cursor.close()
                print(f'{author_id} --')
                yield author_id

    def get_genre_id(self, genre: Genre):
        cursor = self.connection.cursor()
        query = "SELECT id FROM genre WHERE name = %s"
        cursor.execute(query, (genre.name,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    def insert_genre(self, genre: Genre):
        genre_id = self.get_genre_id(genre)
        if genre_id:
            return genre_id

        cursor = self.connection.cursor()
        query = "INSERT INTO genre (name) VALUES (%s)"
        cursor.execute(query, (genre.name,))
        genre_id = cursor.lastrowid
        self.connection.commit()
        cursor.close()
        return genre_id

    def get_publisher_id(self, publisher: Publisher):
        cursor = self.connection.cursor()
        query = "SELECT id FROM publisher WHERE name = %s"
        cursor.execute(query, (publisher.name,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    def insert_publisher(self, publisher: Publisher):
        publisher_id = self.get_publisher_id(publisher)
        if publisher_id:
            return publisher_id

        cursor = self.connection.cursor()
        query = "INSERT INTO publisher (name) VALUES (%s)"
        cursor.execute(query, (publisher.name,))
        publisher_id = cursor.lastrowid
        self.connection.commit()
        cursor.close()
        return publisher_id

    def insert_book(self, book: Book):
        author_ids = self.insert_authors(book.authors)
        genre_id = self.insert_genre(book.genre)
        publisher_id = self.insert_publisher(book.publisher)

        cursor = self.connection.cursor()
        query = "INSERT INTO book (isbn, title, pages, publish_date, publisher, cover, description, price, available) " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        cursor.execute(query, (
            book.isbn, book.title, book.pages, book.publish_date, publisher_id, book.cover, book.description,
            book.price, book.available
        ))
        book_id = cursor.lastrowid

        query = "INSERT INTO book_author (book_id, author_id) VALUES (%s, %s)"
        for author_id in author_ids:
            cursor.execute(query, [book_id, author_id])

        query = "INSERT INTO book_genre (book_id, genre_id) VALUES (%s, %s)"
        cursor.execute(query, (book_id, genre_id))

        self.connection.commit()
        cursor.close()
        return book_id


# Create a DatabaseManager instance
