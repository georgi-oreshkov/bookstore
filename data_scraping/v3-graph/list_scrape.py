import csv
import random
import re
from io import BytesIO
from time import sleep
from ai_assistance import get_book_genre

import requests

from data_manager import Book
from data_manager import DatabaseManager


class RequestException(Exception):
    def __init__(self, message):
        self.message = message


def load_csv(file_path):
    _data = []
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            columns = row[1:4]  # Extract columns 2, 3, 4 (index 1, 2, 3)
            _data.append(columns)
    return _data


def remove_symbols_and_lower(text):
    # Remove symbols using regular expression
    text = re.sub(r'[^a-zA-Z]', '', text)

    # Convert the remaining letters to lowercase
    text = text.lower()

    return text


def convert_to_date(date):
    # Remove non-digit characters
    date = re.sub(r'\D', '', date)

    # Pad with zeros if date is a partial date
    if len(date) < 4:
        date += '0' * (4 - len(date))
        date += '0101'  # Add '0101' for missing parts
    elif len(date) < 6:
        date += '0' * (6 - len(date))
        date += '01'  # Add '01' for missing day
    elif len(date) < 8:
        date += '01'  # Add '01' for missing day

    # Format the date as YYYY-MM-DD
    formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"

    return formatted_date


def make_request(url: str):
    response = requests.get(url)
    if response.status_code != 200:
        raise RequestException(f'Request to {url} -> {response.status_code}')
    return response


data = load_csv('list.txt')
google_api_key = 'AIzaSyA7lDE_wN8BVHFwB7PCB5AKpbpVORMK-rI'
db = DatabaseManager('31.13.202.185', 'bookstore_user', '308-_-803', 'bookstore')
count = 0
for book_line in data:
    resp = make_request(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{book_line[0]}').json()
    if resp['totalItems'] == 0:
        continue
    print(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{book_line[0]}')
    print(resp['items'][0]['selfLink'])
    resp = make_request(resp['items'][0]['selfLink']).json()['volumeInfo']
    readyData = {'title': resp['title'], 'author': resp['author'], 'publisher': resp.get('publisher', None),
                 'date': resp.get('publishedDate', None), 'description': resp.get('description', None),
                 'pages': resp.get('pageCount', None), 'imageLinks': resp.get('imageLinks', None)}

    valid = True
    for test in readyData.values():
        if test is None:
            print('fail')
            valid = False
            break

    if not valid:
        continue
    sleep(2)

    readyData['image'] = readyData['imageLinks'].get('medium', None)
    del readyData['imageLinks']
    print(remove_symbols_and_lower(book_line[1]), remove_symbols_and_lower(readyData['title']))
    if readyData['image'] is None \
            or remove_symbols_and_lower(book_line[1]) != remove_symbols_and_lower(readyData['title']):
        print('fail')
        continue
    readyData['image'] = make_request(str(readyData['image'])).content
    # Image.open(BytesIO(readyData['image'])).show()
    count += 1
    db.insert_book(Book(book_line[0],
                        readyData['title'],
                        readyData['pages'],
                        convert_to_date(readyData['date']),
                        readyData['publisher'],
                        readyData['image'],
                        readyData['description'],
                        random.uniform(10, 40),
                        random.uniform(6, 50),
                        readyData['author'],
                        random.choice(('Fantasy', 'Thriller', 'Mystery', 'Adventure'))
                        ))

print(count)
