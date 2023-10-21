import pytest

from german_word_addon import converter
from typing import List, Dict, Tuple


@pytest.mark.parametrize(['response', 'expected'], [
    (
            {
                'choices': [
                    {
                        'finish_reason': 'stop',
                        'index': 0,
                        'message': {
                            'content': '1) Sie werfen ihm vor, zu spät gekommen zu sein. - Они упрекают его в том,'
                                       ' что он пришел слишком поздно.\n2) Er hat einen Blick auf seine Uhr geworfen.'
                                       ' - Он бросил взгляд на свои часы.\n3) Der Hund hat den Ball in den Fluss'
                                       ' geworfen. - Собака бросила мяч в реку.',
                            'role': 'assistant',
                        },
                    },
                ],
                'created': 1697903289,
                'id': 'chatcmpl-8C8UryEAzc12NHfqcUriWDWUOqbxm',
                'model': 'gpt-4-0613',
                'object': 'chat.completion',
                'usage': {'completion_tokens': 108, 'prompt_tokens': 68, 'total_tokens': 176}
            },

            [
                ('Sie werfen ihm vor, zu spät gekommen zu sein.',
                 'Они упрекают его в том, что он пришел слишком поздно.'),

                ('Er hat einen Blick auf seine Uhr geworfen.',
                 'Он бросил взгляд на свои часы.'),

                ('Der Hund hat den Ball in den Fluss geworfen.',
                 'Собака бросила мяч в реку.'),
            ]
    ),

    (
            {
                'choices': [
                    {
                        'finish_reason': 'stop',
                        'index': 0,
                        'message': {
                            'content': '1) "Ich habe viele Jahre Erfahrung in '
                                       'diesem Bereich." - "У меня есть '
                                       'многолетний опыт работы в этой '
                                       'области."\n'
                                       '\n'
                                       '2) "Deine Erfahrung kann sehr hilfreich '
                                       'sein." - "Твой опыт может быть очень '
                                       'полезен."\n'
                                       '\n'
                                       '3) "Ich habe keine Erfahrung mit solchen '
                                       'Situationen." - "У меня нет опыта в '
                                       'подобных ситуациях."',
                            'role': 'assistant',
                        },
                    },
                ],
            },
            [('Ich habe viele Jahre Erfahrung in diesem Bereich.',
              'У меня есть многолетний опыт работы в этой области.'),
             ('Deine Erfahrung kann sehr hilfreich sein.',
              'Твой опыт может быть очень полезен.'),
             ('Ich habe keine Erfahrung mit solchen Situationen.',
              'У меня нет опыта в подобных ситуациях.')]
    )
])
def test_examples_from_chatgpt_responses(response: Dict, expected: List[Tuple[str, str]]):
    actual = list(converter.examples_from_chatgpt_responses(response))
    assert actual == expected
