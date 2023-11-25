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
    ),

    (
            {'choices': [{'finish_reason': 'stop',
                          'index': 0,
                          'message': {'content': '1. "Das Wasser dieser Quelle ist sehr '
                                                 'klar."\n'
                                                 '   Перевод: "Вода этого источника очень '
                                                 'чистая."\n'
                                                 '\n'
                                                 '2. "Ich habe verschiedene Quellen für '
                                                 'meine Forschungsarbeit benutzt."\n'
                                                 '   Перевод: "Я использовал различные '
                                                 'источники для моей исследовательской '
                                                 'работы."\n'
                                                 '\n'
                                                 '3. "Die Quelle des Problems wurde noch '
                                                 'nicht identifiziert."\n'
                                                 '   Перевод: "Источник проблемы еще не '
                                                 'был идентифицирован."',
                                      'role': 'assistant'}}],
             'created': 1700906098,
             'id': 'chatcmpl-8OjfGvRWYRSxejEi5RFhkkdKxF1sq',
             'model': 'gpt-4-1106-preview',
             'object': 'chat.completion',
             'system_fingerprint': 'fp_a24b4d720c',
             'usage': {'completion_tokens': 128, 'prompt_tokens': 68, 'total_tokens': 196}},
        [
            ('Das Wasser dieser Quelle ist sehr klar.',
             'Вода этого источника очень чистая.'),
            ('Ich habe verschiedene Quellen für meine Forschungsarbeit benutzt.',
             'Я использовал различные источники для моей исследовательской работы.'),
            ('Die Quelle des Problems wurde noch nicht identifiziert.',
             'Источник проблемы еще не был идентифицирован.')
        ],
    ),

    (
            {'choices': [{'finish_reason': 'stop',
                          'index': 0,
                          'message': {'content': 'Пример использования:\n'
                                                 '\n'
                                                 '- Sie müssen Ihre Steuererklärung bis '
                                                 'zum 31. Juli einreichen.\n'
                                                 '\n'
                                                 'Перевод:\n'
                                                 '\n'
                                                 '- Вы должны подать свою налоговую '
                                                 'декларацию до 31 июля.',
                                      'role': 'assistant'}}],
             'created': 1700910165,
             'id': 'chatcmpl-8OkirB4S6q80DKtEW9zCCa0Z3cwtk',
             'model': 'gpt-4-1106-preview',
             'object': 'chat.completion',
             'system_fingerprint': 'fp_a24b4d720c',
             'usage': {'completion_tokens': 55, 'prompt_tokens': 69, 'total_tokens': 124}},
        [
            ('Sie müssen Ihre Steuererklärung bis zum 31. Juli einreichen.',
             'Вы должны подать свою налоговую декларацию до 31 июля.'),
        ],
    )
])
def test_examples_from_chatgpt_responses(response: Dict, expected: List[Tuple[str, str]]):
    actual = list(converter.examples_from_chatgpt_responses(response))
    assert actual == expected
