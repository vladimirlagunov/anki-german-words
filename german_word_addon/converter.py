import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Iterator, Iterable


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
            for l in html_to_text(re.sub(r'\s+', ' ', r, re.MULTILINE | re.DOTALL).strip()).split('\n')
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

    for suffix in ['', '2', '3']:
        if front := source_note.get(f'FrontExample{suffix}'):
            examples.append((
                front,
                source_note.get(f'BackExample{suffix}', '')
            ))

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


def parse_note_from_wiktionary(wiktionary: str) -> Dict[str, List[str]]:
    # categories = [
    #     'Adjektiv',
    #     'Adverb',
    #     'Eigenname',
    #     'Partizip I',
    #     'Partizip II',
    #     'Präposition',
    #     'Redewendung',
    #     'Substantiv',
    #     'Verb',
    # ]
    notes = []
    lines = iter(wiktionary.split('\n'))
    for line in lines:
        if line.startswith('{{Deutsch Substantiv Übersicht'):
            notes.append(defaultdict(set))
            _fill_substantiv(notes[-1], lines)
        elif line.startswith('{{Deutsch Verb Übersicht'):
            notes.append(defaultdict(set))
            _fill_verb(notes[-1], lines)
        elif line.startswith('*{{ru}}: {{Ü') and notes:
            for m in re.finditer(r'\{\{Üt\|ru\|([^}]+)}}', line):
                notes[-1]['WordTranslation'].add(m.groups()[0])

    for key in {k for n in notes for k in n.keys()}:
        for note in notes:
            note.setdefault(key, {'???'})

    result_variants: Dict[str, Dict[str, str]] = {}
    for note in notes:
        short_translation = ', '.join(sorted(note.get('WordTranslation', {'???'})))
        for key, value in note.items():
            dct = result_variants.setdefault(key, {})
            for v in value:
                dct[v] = ', '.join(sorted(filter(None, [dct.get(v), short_translation])))

    result_note = {}
    for key, value in result_variants.items():
        if len(value) == 1 or key == 'WordTranslation':
            result_note[key] = sorted(value.keys() - {'???'})
        else:
            result_note[key] = [f'{k} – {v}' for k, v in value.items()]

    return result_note


def _fill_substantiv(note: Dict[str, str], lines: Iterator[str]) -> None:
    plural = set()
    for line in lines:
        line = line.strip()
        if line == '}}':
            break
        elif m := re.match('^[|]Nominativ Plural[^=]*=(.*)$', line):
            plural.add(m.group(1))
        elif line == '|Genus=m':
            note['DerDieDas'].add('der')
        elif line == '|Genus=f':
            note['DerDieDas'].add('die')
        elif line == '|Genus=n':
            note['DerDieDas'].add('das')
        elif line == '|Genus=0':
            note['DerDieDas'].add('Pl.')
            plural = set()
    note['Plural'] = note['Plural'].union(plural)


def _fill_verb(note: Dict[str, str], lines: Iterator[str]) -> None:
    partizip2 = ''
    hilfsverb = ''
    for line in lines:
        if line == '}}':
            break
        elif line.startswith('|Präsens_er, sie, es='):
            note['DrittenPerson'].add(line.split('=', 1)[1].strip())
        elif line.startswith('|Präteritum_ich='):
            note['Präteritum'].add(line.split('=', 1)[1].strip())
        elif line.startswith('|Partizip II='):
            partizip2 = line.split('=', 1)[1]
        elif line.startswith('|Hilfsverb='):
            hilfsverb = line.split('=', 1)[1]
    if partizip2 and hilfsverb:
        note['Perfekt'].add(f'{hilfsverb} {partizip2}')


def examples_from_chatgpt_responses(responses: Dict) -> Iterable[Tuple[str, str]]:
    for choice in responses.get('choices', [])[::-1]:
        if not isinstance(message := choice.get('message'), dict):
            continue
        if message.get('role') != 'assistant':
            continue
        if not isinstance(content := message.get('content'), str):
            continue
        flags = re.UNICODE | re.IGNORECASE | re.MULTILINE | re.DOTALL
        for groups in re.findall(r'(?:\s*beispiel:\s*[-"\']*\s*)?([a-züöäß][^а-я]*)(?:\s*перевод:\s*[-"\']*\s*)?([а-я][^\na-züöäß]*)', content, flags):
            l = []
            for g in groups:
                if m := re.match(r'''^\s*["']?\s*(.*?)\s*["']?\s*-?\s*["']?\s*$''', g, flags):
                    l.append(m.group(1))
                else:
                    l.append(g)
            yield tuple(l)
