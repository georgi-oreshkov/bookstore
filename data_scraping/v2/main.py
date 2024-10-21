from io import BytesIO

import mysql.connector
from PIL import Image

import books

# books.generated_desc = True

author_list = [
    'Stephen King', 'Rick Riordan', 'J. K. Rowling', 'J.R.R. Tolkien',
    'Robert McCammon', "Isaac Asimov", 'Lovecraft',
    'Dan Brown', "Ernest Hemingway", 'Michael Crichton',
    'Arthur Clarke', "George R.R. Martin",

]

author_list_v2 = ["Charles Dickens", "Mark Twain", "Leo Tolstoy",
                  "Fyodor Dostoevsky", "Virginia Woolf", "Ernest Hemingway", "Gabriel Garcia Marquez",
                  "Toni Morrison"
                  ]

author_list.extend(author_list_v2)
# cnx = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="123456789",
#     database="paper_trail"
# )
storage = open('list.txt', mode='r+', encoding='utf-8')
for author in author_list:
    print(author)
    for book in books.scrape_from_author(author, storage):
        # books.display(book)
        print(f'{book.title.ljust(20)} -> {book.isbn} | {book.types_str()} '
              f'<- {[author.types_str() for author in book.authors]}')
        Image.open(BytesIO(book.cover)).show()
        [Image.open(BytesIO(author.photo)).show()
         if author not in books.authors_already_found
         else print('author image already displayed')
         for author in book.authors]
        # books.insert(book, cnx)
storage.close()
# cnx.close()
