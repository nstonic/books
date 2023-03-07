# -*- coding: utf-8 -*-
import json
import os
import sys

from argparse import ArgumentParser
from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked
from pathvalidate.argparse import validate_filepath_arg

from settings import JSON_PATH


def render_page(json_path: str):
    env = Environment(
        loader=FileSystemLoader(''),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    try:
        with open(json_path) as file:
            books_descriptions = json.load(file)
    except FileNotFoundError:
        print(
            'Необходимо указать путь к json-файлу с данными либо в файле settings.py,'
            'либо в аргументе --json_path при запуске скрипта из командной строки.\n'
            'Подробнее читайте в README.',
            file=sys.stderr
        )
        exit()
    book_cards_on_page = 10
    book_cards_separated_by_pages = list(chunked(books_descriptions, book_cards_on_page))
    for page_number, books_descriptions in enumerate(book_cards_separated_by_pages, start=1):
        number_of_columns = 2
        rendered_page = template.render(
            books_cards=chunked(books_descriptions, number_of_columns),
            total_pages=len(book_cards_separated_by_pages),
            current_page=page_number
        )
        os.makedirs('pages', exist_ok=True)
        page_path = os.path.join('pages', f'index{page_number}.html')
        with open(page_path, 'w', encoding='utf8') as file:
            file.write(rendered_page)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        '--json_path',
        type=validate_filepath_arg,
        help='Указать путь к json-файлу с данными'
    )
    args = parser.parse_args()
    json_path = args.json_path or JSON_PATH
    render_page(json_path)


if __name__ == '__main__':
    main()
    server = Server()
    server.watch(os.path.join('template.html'), main)
    server.serve()
