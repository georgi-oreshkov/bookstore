import re

import openai
import requests

openai.api_key = '-'


def get_book_genre(book_title: str, author: str):
    print('generating genres...')
    prompt = f"Choose 2 genres from the list: " \
             f"(Fiction, Non-fiction, Mystery, Thriller, Romance, Science Fiction, " \
             f"Fantasy, Historical, Biography, Horror, Poetry) " \
             f"for the book {book_title} from {author} separated by ','."
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.9,
        max_tokens=50,
        n=1,
        stop=None,
        timeout=15
    )
    genres = response.choices[0].text.strip()
    genres = re.sub(r'[^\w\s,]', '', genres)  # remove any punctuation marks
    return [genre.strip() for genre in genres.split(',')]


# def calc_price(title, page_count, book_format):
#     print('generating price...')
#
#     prompt = f"Predict the price (only giving a single decimal number) of a {book_format} book titled '{title}' " \
#              f"with {page_count} pages in euro."
#     response = openai.Completion.create(
#         model="text-babbage-001",
#         prompt=prompt,
#         max_tokens=10,
#         n=1,
#         stop=None,
#         temperature=0.1,
#         timeout=15
#     )
#     # Extract the predicted price from the API response
#     predicted_price = response.choices[0].text.strip()
#     return float(predicted_price)


def generate_desc(title: str):
    print('generating desc...')

    prompt = f'Write a description/summary of the book: {title} strictly between 100 and 240 words.'
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=300,
        n=1,
        stop=None,
        temperature=0.8,
        timeout=30
    )
    return response.choices[0].text


def unify_date(date: str):
    print('unifying date...')

    if not date:
        return
    prompt = f'Convert "{date}" to this format: YYYY-MM-DD. if something is missing put 00.'
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=20,
        n=1,
        stop=None,
        temperature=0,
        timeout=15
    )
    return response.choices[0].text


def get_pages_ai(title: str, author: str):
    print('estimating pages...')
    prompt = f'Estimate the number of pages (a single integer) for {title} by {author}'
    response = openai.Completion.create(
        model="text-babbage-001",
        prompt=prompt,
        max_tokens=5,
        n=1,
        stop=None,
        temperature=0.1,
        timeout=15
    )
    return re.sub(r'\n\s', '', response.choices[0].text)


def generate_image(author_name: str):
    print('generating author image...')

    prompt = f'Oil painting image of {author_name}, smooth background, low-medium detail'
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,  # Number of images to generate
            size="256x256",
            response_format="url"
        )
    except openai.error.InvalidRequestError as e:
        print(e.error)
        return None

    image_url = response['data'][0]['url']
    image_data = requests.get(image_url).content
    return image_data


def correct(thing: str):
    print('correcting...')

    return openai.Completion.create(
        model="text-davinci-002",
        prompt=f'Return only the correct english spelling of "{thing}"',
        temperature=0.1,
        max_tokens=20,
        n=1,
        stop=None,
        timeout=15
    ).choices[0].text.replace('\n', '')


def get_books_of_author(author_name: str):
    print('getting books...')
    prompt = f'Write the titles of around 10 of the most popular books {author_name} ' \
             f'has ever written, separated by a comma. ' \
             f'only write correct and accurate titles'
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.5,
        max_tokens=500,
        n=1,
        stop=None,
        timeout=15
    )
    return re.sub(r'[^\w\s,\']', '', response.choices[0].text.strip())


def get_author_bio(author_name: str):
    prompt = (
        f"Generate a short 6-7 sentence description of {author_name}. "
        f"The description should sound catchy and be true to the author's nature and writing style.")
    # Set up the OpenAI API request parameters
    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=128,
        n=1,
        stop=None,
        temperature=0.7,
    )
    # Retrieve the generated text from the API response
    generated_text = completions.choices[0].text.strip()
    # Remove any extraneous text generated by the GPT-3 model
    generated_text = re.sub(r"\n", "", generated_text)
    generated_text = re.sub(r"\r", "", generated_text)
    return generated_text
