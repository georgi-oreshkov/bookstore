import ai_assistance as ai
author_list = [
    'Stephen King', 'Rick Riordan', 'J. K. Rowling', 'J.R.R. Tolkien', 'Michael Crichton',
    'Robert McCammon', "Isaac Asimov", 'Lovecraft',
    'Dan Brown',
    'Arthur Clarke', "George R.R. Martin",

]

author_list_v2 = ["Charles Dickens", "Mark Twain", "Leo Tolstoy",
                  "Fyodor Dostoevsky", "Virginia Woolf", "Ernest Hemingway", "Gabriel Garcia Marquez",
                  "Toni Morrison"
                  ]

author_list.extend(author_list_v2)
file = open('list1.txt', mode='w', encoding='utf-8')
print(type(file))
# for author in author_list:
#     file.write(f'{author}: {ai.get_books_of_author(author)}\n')

file.close()
