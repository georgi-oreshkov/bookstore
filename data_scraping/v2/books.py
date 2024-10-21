import random
import re
import urllib.parse
from io import BytesIO

import requests
from PIL import Image

import ai_assistance as ai
import exceptions as ex

generated_desc = False
book_scrape_depth = 20
google_api_key = 'AIzaSyA7lDE_wN8BVHFwB7PCB5AKpbpVORMK-rI'

authors_already_found = []


def display(book):
    print(book)
    Image.open(BytesIO(book.cover)).show()
    [Image.open(BytesIO(author.photo)).show() for author in book.authors]


def make_request(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        raise ex.RequestException(f'Request to {url} -> {response.status_code}')
    return response


def search_book(isbn: str):
    return make_request(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
                        f"&maxResults=10&printType=books&key={google_api_key}").json()


# def get_author_json(author_id: str):
#     return make_request(f"https://openlibrary.org/authors/{author_id}.json").json()

def get_wikipedia_url(author_name):
    search_query = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=" + urllib.parse.quote(
        author_name) + "&format=json"
    response = requests.get(search_query)
    page_title = response.json()["query"]["search"][0]["title"]
    page_url = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(page_title)
    return page_url


#     response = make_request(f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg").content
#     img = Image.open(BytesIO(response))
#     if img.size == (1, 1):
#         raise ex.CoverMissingException
#     return response


# def get_author_img(ol_id):
#     if ol_id is None:
#         raise ex.AuthorImgMissingException
#     return make_request(f"https://covers.openlibrary.org/a/id/{ol_id}-L.jpg").content
#
#
# def get_author_id_by_name(name: str):
#     response = make_request(f"https://openlibrary.org/search/authors.json?q={urllib.parse.quote_plus(name)}") \
#         .json().get('docs')
#     if response is None or response[0] is None or response[0].get('key'):
#         raise ex.AuthorMissingException(f"author id for {name} not found.")


def get_author_names(authors):
    return "& ".join([author.name for author in authors])


def create_author_if_not_exists(name):
    global authors_already_found
    for author in authors_already_found:
        # print(author.name.lower().strip(), name.lower().strip())
        if author.name.lower().strip() == name.lower().strip():
            print('author already found!')
            return author
    else:
        _author = Author(ai.correct(name))
        authors_already_found.append(_author)
        return _author


class Book:
    """
    self
    title
    author
    pages
    publish_date (2009-11-00)
    publisher (name)
    format
    cover
    description
    genre/s (names) + algorithm to add them if they don't exist or to connect it to a proper one
    price
    available
    link list
    """

    @staticmethod
    def from_gbs_id(gbs_id: str):
        try:
            volume_data = make_request(f'https://www.googleapis.com/books/v1/volumes/{gbs_id}').json().get('volumeInfo')
        except ex.RequestException as e:
            print(f'fail at volume data with {e.message}')
            return
        if volume_data.get('language') != 'en':
            print('fail at language')
            return

        identifiers = volume_data.get('industryIdentifiers')
        if not identifiers:
            print('no identifiers')
            return

        for entry in identifiers:
            if entry.get('type') in ('ISBN_13', 'ISBN_10'):
                isbn = entry.get('identifier')
                break
        else:
            print('fail at isbn')
            return

        title = volume_data.get("title", None)
        try:
            authors = [create_author_if_not_exists(author) for author in volume_data.get('author')]
        except ex.AuthorMissingException as e:
            print(f'fail at author -> {e.message}')
            return
        page_count = volume_data.get("pageCount", None)
        publish_date = ai.unify_date(volume_data.get("publishedDate", None))
        publisher = volume_data.get("publisher", None)
        book_format = random.choice(('Paperback', 'Hardcover'))
        try:
            if volume_data.get('imageLinks') is None:
                print('no imageLinks')
                return
            thumbnail_try = volume_data.get('imageLinks').get('thumbnail', None)
            img_url = thumbnail_try if thumbnail_try is not None \
                else volume_data.get('imageLinks').get('smallThumbnail', None)
            if img_url is None:
                print('no thumbnail')
                return
            cover = make_request(img_url).content
        except ex.RequestException:
            print('fail at cover')
            return
        description = ai.generate_desc(title) if generated_desc else volume_data.get("description", None)
        genres = ai.get_book_genre(title, get_author_names(authors))
        price = random.uniform(6, 24)
        links = {
            'previewLink': volume_data.get('previewLink'),
            'infoLink': volume_data.get('previewLink'),
            'canonicalVolumeLink': volume_data.get('previewLink')
        }
        return Book(isbn, title, authors, page_count, publish_date, publisher,
                    book_format, cover, description, genres, price, links)

    def __init__(self, isbn, title, authors, pages,
                 publish_date, publisher, book_format,
                 cover, description, genres, price, links):
        self.isbn = isbn
        self.title = title
        self.authors = authors
        self.pages = pages
        self.publish_date = publish_date
        self.publisher = publisher
        self.book_format = book_format
        self.cover = cover
        self.description = description
        self.genres = genres
        self.price = price
        self.links = links

    def __str__(self):
        authors = ", ".join(str(author) for author in self.authors)
        links = "\n".join(f"{link}: {self.links[link]}" for link in self.links)
        return (f"Title: {self.title}\n"
                f"Authors: {authors}\n"
                f"Pages: {self.pages}\n"
                f"Publish Date: {self.publish_date}\n"
                f"Publisher: {self.publisher}\n"
                f"Format: {self.book_format}\n"
                f"Cover: {self.cover}\n"
                f"Description: {self.description}\n"
                f"Genres: {', '.join(self.genres)}\n"
                f"Price: {self.price}\n"
                f"Links: {', '.join(links)}")

    def types_str(self):
        types = [type(val).__name__ for val in vars(self).values()]
        return ', '.join(types)


class Author:
    """
    name
    wiki
    bio
    photo
    """

    # def __init__(self, name: str):
    #     key = get_author_id_by_name(name)
    #     if key is None:
    #         raise ex.AuthorMissingException('No key')
    #
    #     try:
    #         author_data = get_author_json(key)
    #     except ex.RequestException as e:
    #         raise ex.AuthorMissingException(e.message)
    #
    #     self.name = name
    #     self.wiki = author_data.get('wikipedia', None)
    #     bio_tmp = author_data.get('bio', None)
    #     self.bio = bio_tmp if type(bio_tmp) is str or bio_tmp is None else bio_tmp['value']
    #     try:
    #         self.photo = get_author_img(author_data.get('photos', [None, ])[0])
    #     except ex.AuthorImgMissingException:
    #         self.photo = ai.generate_image(self.name)
    def __init__(self, name: str):
        self.name = ai.correct(name)
        self.wiki = get_wikipedia_url(name)
        self.bio = ai.get_author_bio(name)
        self.photo = ai.generate_image(self.name)

    def __str__(self):
        return f"{self.name}\nWikipedia: {self.wiki}\nBio: {self.bio}\n"

    def types_str(self):
        types = [type(val).__name__ for val in vars(self).values()]
        return ', '.join(types)


def insert(book: Book, cnx):
    insert_author = "INSERT INTO author (name, wiki_link, bio, photo) VALUES (%s, %s, %s, %s)"
    select_author = "SELECT id FROM author WHERE author.name = %s"
    insert_book_author = "INSERT INTO book_author (book_id, author_id) VALUES (%s, %s)"
    insert_publisher = "INSERT INTO publisher (name) VALUES (%s)"
    select_publisher = "SELECT id FROM publisher WHERE name = %s"
    insert_book = "INSERT INTO book (isbn, title, pages, publish_date, " \
                  "publisher, book_format, cover, description, price, available) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    select_book = "SELECT id FROM book WHERE isbn = %s"
    insert_link = "INSERT INTO link (book, title, url) VALUES (%s, %s, %s)"
    insert_genre = "INSERT INTO genre (name) VALUES (%s)"
    select_genre = "SELECT id FROM genre WHERE name = %s"
    insert_book_genre = "INSERT INTO book_genre (book_id, genre_id) VALUES (%s, %s)"

    cursor = cnx.cursor()

    cursor.execute(select_publisher, (book.publisher,))
    publisher_id = cursor.fetchall()
    if not publisher_id:
        cursor.execute(insert_publisher, (book.publisher,))
        cursor.execute(select_publisher, (book.publisher,))
        publisher_id = cursor.fetchall()
    publisher_id = publisher_id[0]  # unpack?

    cursor.execute(insert_book, (book.isbn, book.title, book.pages, book.publish_date, publisher_id[0],
                                 book.book_format, book.cover, book.description, book.price, 1))
    cursor.execute(select_book, (book.isbn,))
    book_id = cursor.fetchall()[0][0]
    for author in book.authors:
        cursor.execute(select_author, (author.name,))
        author_id = cursor.fetchall()
        if not author_id:
            cursor.execute(insert_author, (author.name, author.wiki, author.bio, author.photo))
            cursor.execute(select_author, (author.name,))
            author_id = cursor.fetchall()
        cursor.execute(insert_book_author, (book_id, author_id[0][0]))

    for genre in book.genres:
        cursor.execute(select_genre, (genre,))
        genre_id = cursor.fetchall()
        if not genre_id:
            cursor.execute(insert_genre, (genre,))
            cursor.execute(select_genre, (genre,))
            genre_id = cursor.fetchall()

        cursor.execute(insert_book_genre, (int(book_id), int(genre_id[0][0])))

    for link in book.links.keys():
        cursor.execute(insert_link, (book_id, link, book.links[link]))

    cursor.close()
    cnx.commit()


def scrape_from_author(author_name: str, storage):
    storage.seek(0)
    line = storage.readline()
    while line:
        if line.split('>>>')[0] == author_name:
            books = line.split('>>>')[1]
            break
        line = storage.readline()
    else:
        books = ai.get_books_of_author(author_name)
        storage.write(f'{author_name}: {books}\n')
    author_name = ai.correct(author_name)

    for book in (book.strip().strip("'") for book in books.split(',')):
        book_enc = urllib.parse.quote_plus(book.lower())
        request = f'https://www.googleapis.com/books/v1/volumes?q=intitle:{book_enc}' \
                  f'&maxResults={book_scrape_depth}&printType=books&projection=lite' \
                  f'&key={google_api_key}'
        book_search = requests.get(request)
        print(request)
        if book_search.status_code != 200:
            print(f"{book_search.status_code} for {book}.")
            continue

        data = book_search.json()
        print(f'{book} -> {book_search.status_code} -> found {data.get("totalItems")}')
        if data.get('totalItems') == 0:
            continue

        print('\\/' * 30)
        items = data.get('items')
        if not items:
            continue

        for item in items:
            print('-' * 50)
            item_vl = item.get('volumeInfo')
            if re.sub(r'[^A-Za-z]', '', book).lower() not in re.sub(r'[^A-Za-z]', '', item_vl.get('title')).lower():
                print(f"wrong title -> {item_vl.get('title')} != {book}")
                print(re.sub(r'[^A-Za-z]', '', book).lower().rjust(30))
                print(re.sub(r'[^A-Za-z]', '', item_vl.get('title')).lower().rjust(30))
                continue

            authors = item_vl.get('author', None)
            if not authors:
                print('no author')
                continue
            for author_found in authors:
                if author_name.lower().replace(' ', '') not in author_found.lower().replace(' ', ''):
                    print('wrong author')
                    continue

            gbs_id = item.get('id')
            print(f'Trying {gbs_id}')
            _book = Book.from_gbs_id(gbs_id)
            if _book:
                print(' -> success')
                yield _book
                break
            else:
                print(' -> fail')
