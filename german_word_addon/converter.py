from itertools import zip_longest

import bs4

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Iterator


@dataclass
class GermanNote:
    word: str
    translation: str
    explanation: str = ''
    examples: List[Tuple[str, str]] = field(default_factory=list)


def convert(source_note: Dict[str, str]) -> GermanNote:
    front_raw: str = (
            source_note.get('Слово')
            or source_note.get('Infinitiv')
            or source_note.get('Front')
            or source_note.get('Вопрос')
            or ''
    )

    back_raw: str = (
            source_note.get('Перевод')
            or source_note.get('Back')
            or source_note.get('Ответ')
            or ''
    )

    front_iter: Iterator[str]
    back_iter: Iterator[str]
    front_iter, back_iter = [
        iter(filter(None, (
            re.sub(r'\s+', ' ', l).strip()
            for l in html_to_text(r).split('\n')
        )))
        for r in [front_raw, back_raw]
    ]

    word: str = front_raw
    translation: str = back_raw
    explanation = ''
    examples: List[Tuple[str, str]] = []

    del front_raw
    del back_raw

    try:
        word: str = (
            next(front_iter)
            .removeprefix('der ')
            .removeprefix('die ')
            .removeprefix('das ')
        )
        word = word.split('-', 1)[0]
        word = word.split(',', 1)[0]
        word = word.split('(', 1)[0]
        word = word.strip()

        translation = next(back_iter)

        while True:
            front_line = next(front_iter)
            back_line = next(back_iter)

            if front_line.startswith('Syn:'):
                explanation = front_line
                front_line = next(front_iter)

            if front_line == back_line:
                back_line = next(back_iter)

            examples.append((
                re.sub(r'\s+([,.])', r'\1', front_line),
                re.sub(r'\s+([,.])', r'\1', back_line),
            ))
    except StopIteration:
        pass

    return GermanNote(
        word=word,
        translation=translation,
        explanation=explanation,
        examples=examples,
    )


NON_BREAKING_ELEMENTS = ['a', 'abbr', 'acronym', 'audio', 'b', 'bdi', 'bdo', 'big', 'button',
                         'canvas', 'cite', 'code', 'data', 'datalist', 'del', 'dfn', 'em', 'embed', 'i', 'iframe',
                         'img', 'input', 'ins', 'kbd', 'label', 'map', 'mark', 'meter', 'noscript', 'object', 'output',
                         'picture', 'progress', 'q', 'ruby', 's', 'samp', 'script', 'select', 'slot', 'small', 'span',
                         'strong', 'sub', 'sup', 'svg', 'template', 'textarea', 'time', 'u', 'tt', 'var', 'video',
                         'wbr']


# https://stackoverflow.com/a/75501596
def html_to_text(markup, preserve_new_lines=True, strip_tags=('style', 'script', 'code')):
    from bs4 import BeautifulSoup
    from html import unescape

    soup = BeautifulSoup(unescape(markup), "html.parser")
    for element in soup(strip_tags): element.extract()
    if preserve_new_lines:
        for element in soup.find_all():
            if element.name not in NON_BREAKING_ELEMENTS:
                element.append('\n') if element.name == 'br' else element.append('\n\n')
    return soup.get_text(" ")
