import os

from SPARQLWrapper import SPARQLWrapper, JSON
from time import sleep

# Set up the SPARQL endpoint URL for the Wikidata Query Service
endpoint_url = "https://query.wikidata.org/sparql"
user_agent = "BookStoreSchoolProject/1.0"

file = open('list.txt', mode='a+', encoding='utf8')
file.seek(0)
lines = file.readlines()
if not lines:
    found_list = [line.split(',')[1].strip() for line in lines]
else:
    found_list = []
del lines
file.seek(os.SEEK_END)
print(found_list)


def write_if_not_exists(line: str, author: str):
    global file
    global found_list

    isbn = line.split(',')[1].strip()
    if isbn in found_list:
        return
    print('writing...')
    found_list += isbn
    file.write(f'{line}, {author}\n')


def execute_sparql_query(query: str, url: str):
    sleep(1)
    sparql = SPARQLWrapper(url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.addCustomHttpHeader("User-Agent", user_agent)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        result = ','.join([result[key]["value"] for key in result])
        yield result


def get_books(author):
    # Set up the SPARQL query
    query = f"""
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>

    SELECT DISTINCT ?book
    WHERE {{
      ?book wdt:P50 wd:{author} .
      ?book wdt:P31 wd:Q7725634. #literary work
      ?book wdt:P7937 ?type .
      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en" .
        ?book rdfs:label ?title .
        ?type rdfs:label ?typeLabel .
      }}
      FILTER(regex(?typeLabel, ".*novel.*", "i") || regex(?typeLabel, ".*collection", "i")) .
    }}
    ORDER BY ?title
    """

    books = execute_sparql_query(query, endpoint_url)
    for book in books:
        query2 = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>        

        SELECT ?editionLabel ?edition ?authorName ?isbn
        WHERE {{
            wd:{book.split('/')[-1]} wdt:P747 ?edition .
            ?edition wdt:P407 wd:Q1860 ;
                wdt:P50 ?author ;
                wdt:P212 ?isbn .     
            SERVICE wikibase:label {{
                bd:serviceParam wikibase:language "en" .
                ?edition rdfs:label ?editionLabel .
                ?author rdfs:label ?authorName .
            }}
        }}
        LIMIT 1
        """
        yield execute_sparql_query(query2, endpoint_url)

    pass


author_list = [
    'Stephen King', 'Rick Riordan', 'J. K. Rowling', 'J. R. R. Tolkien',
    'Robert R. McCammon', "Isaac Asimov", 'H. P. Lovecraft',
    'Dan Brown', "Ernest Hemingway", 'Michael Crichton',
    'Arthur C. Clarke', "George R. R. Martin",
]

author_uri_list = (
    "Q39829",
    "Q212727",
    "Q34660",
    "Q892",
    "Q2598859",
    "Q34981",
    "Q169566",
    "Q7345",
    "Q23434",
    "Q172140",
    "Q47087",
    "Q181677",
    "Q2541295",
    "Q190220",
    "Q311671",
    "Q358188",
    "Q18683986",
    "Q283408",
    "Q312101",
    "Q46248",
    "Q457608"
)

for auth in author_uri_list:
    print(f'\n{auth}\n{"-" * 20}\n')
    for editions in get_books(auth):
        try:
            line = next(editions)
            write_if_not_exists(line, auth)
            print(line)
        except StopIteration:
            pass
file.close()
