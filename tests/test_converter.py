import pytest

from german_word_addon.converter import convert, GermanNote


@pytest.mark.parametrize(['source_note', 'expected'], [
    ({'Перевод': 'башня, собор<div><br></div><div>Ein Dom ist eine große Kirche.&nbsp;</div>',
      'Слово': 'der Dom'},
     GermanNote(word='Dom', translation='башня, собор'),
     ),

    ({'Перевод': 'куда<br><br>Куда ты идешь?<br><br>Я должен куда-то идти.',
      'Слово': 'wohin<br><br><i>Wohin</i><span style="color: rgb(32, 33, 34); '
               'background-color: rgb(255, 255, 255);">&nbsp;gehst '
               'du?<br></span><br>Ich muss mal kurz wohin.'},
     GermanNote(word='wohin', translation='куда', examples=[
         ('Wohin gehst du?', 'Куда ты идешь?'),
         ('Ich muss mal kurz wohin.', 'Я должен куда-то идти.'),
     ])),

    ({'Перевод': 'выставка', 'Слово': 'die Ausstellung'},
     GermanNote(word='Ausstellung', translation='выставка')),

    ({'Перевод': 'заниматься (чем-л; кем-л.)', 'Слово': 'beschäftigen sich'},
     GermanNote(word='beschäftigen sich', translation='заниматься (чем-л; кем-л.)')),

    ({'Infinitiv': 'verlieren',
      'Perfekt 3. Pers': 'hat verloren',
      'Präsens 3. Pers': 'verliert',
      'Präteritum 3. Pers': 'verlor',
      'Перевод': 'терять'},
     GermanNote(word='verlieren', translation='терять')),

    ({'Add Reverse': '',
      'Back': 'удивляться<br><br><font color="#808080">Он будет удивлен, что здесь '
              'так много людей.<br>Если вы не знаете, куда идете, вы будете '
              'удивлены, что оказались в другом месте.</font>',
      'Front': 'wundern sich, wunderte sich, hat sich '
               'gewundert<br><br>Syn:&nbsp;<a>wundern,&nbsp;</a><a>staunen,&nbsp;</a><a>überraschen,&nbsp;</a><a>erstaunen<br><br><ul><li>Er '
               'wird&nbsp;<em>sich wundern</em>, dass so viel Leute hier '
               'sind.</li><li><br></li><li>Wer nicht weiß, wo er hin will, '
               'wird&nbsp;<em>sich wundern</em>, dass er ganz woanders '
               'ankommt.</li></ul></a>'},
     GermanNote('wundern sich', translation='удивляться',
                explanation='Syn: wundern, staunen, überraschen, erstaunen',
                examples=[
                    ('Er wird sich wundern, dass so viel Leute hier sind.',
                     'Он будет удивлен, что здесь так много людей.'),
                    ('Wer nicht weiß, wo er hin will, wird sich wundern, dass er ganz woanders ankommt.',
                     'Если вы не знаете, куда идете, вы будете удивлены, что оказались в другом месте.')
                ])),

    # ({'Back': 'оборот, товарооборот',
    #   'BackExample': 'Я хочу 10% от оборота.\n',
    #   'BackExample2': 'Их оборот составляет 14 миллионов долларов в год.',
    #   'Front': 'der Umsatz',
    #   'FrontExample': 'Ich will 10 % vom Umsatz.\n',
    #   'FrontExample2': 'Sie generieren pro Jahr einen Umsatz von 14 Millionen '
    #                    '$.\n'}),
    #
    # ({'Add Reverse': '',
    #   'Back': 'пол<div><br></div><div><img '
    #           'src="quizlet-S1J6sC9yltjpjC6NxU1l1w.jpg"></div>',
    #   'Front': 'der Boden'}),
    #
    # ({'Back': 'die Ecke(n)', 'Front': 'угол'}),
    #
    # ({'Перевод': 'говорить, разговаривать, беседовать', 'Слово': 'reden'}),
    #
    # ({'Перевод': 'сунуть, засунуть', 'Слово': 'einstecken'}),
    #
    # ({'Перевод': '(раз)ломать, разбивать', 'Слово': 'brechen'}),
    #
    # ({'Вопрос': 'die Mannschaft -en', 'Ответ': 'команда'}),
    #
    # ({'Вопрос': 'die Ameise -n', 'Ответ': 'муравей'}),
    #
    # ({'Перевод': 'тетя', 'Слово': 'die Tante'}),
    #
    # ({'Add Reverse': '',
    #   'Back': '<div>дело, папка, послужной список, документ<br><br><font '
    #           'color="#666666">Пациенты имеют собственные файлы, содержащие '
    #           'информацию об их болезни.</font><br></div>',
    #   'Front': '\n'
    #            '<div>\n'
    #            '<div>\n'
    #            '<div>die Akte<br><br><div>\n'
    #            '<div>\n'
    #            '<div>\n'
    #            '<div>Patienten hat ihre eigenen Akten, in denen die Informationen '
    #            'zu ihrer Krankheit\n'
    #            'stehen.&nbsp;</div>\n'
    #            '</div>\n'
    #            '</div></div>\n'
    #            '</div>\n'
    #            '</div>\n'
    #            '</div>'}),
    #
    # ({'Add Reverse': '',
    #   'Back': 'голосовать, верный, быть правдой, соглашаетесь<br><br>Мой адрес '
    #           'больше не верен. <br><br>Погода в Германии могла бы быть и получше. '
    #           '- Правильно.',
    #   'Front': '<div>\n'
    #            '<div>\n'
    #            '<div>\n'
    #            '<div>\n'
    #            '<div>stimmen, stimmte, hat gestimmt&nbsp;<br><br><div>\n'
    #            '<div>\n'
    #            '<div>\n'
    #            '<div>\n'
    #            '<div>Meine Adresse stimmt nicht mehr.\n'
    #            '<br><br>Das Wetter in Deutschland könnte\n'
    #            'besser sein. – Das stimmt.&nbsp;</div>\n'
    #            '</div>\n'
    #            '</div>\n'
    #            '</div></div><br></div>\n'
    #            '</div>\n'
    #            '</div>\n'
    #            '</div></div>'}),
    #
    # ({'Add Reverse': '',
    #   'Back': 'устраивать, оборудовать<br><br>Я думаю, что могу это '
    #           'устроить.<br><div><br></div><div><img '
    #           'src="quizlet-gAjwz0Fy.-XkA8ikUGB2dg.jpg"></div>',
    #   'Front': 'einrichten, richtete&nbsp;ein, hat '
    #            'eingerichtet<br><br>Syn:&nbsp;<a>errichten,&nbsp;</a><a>aufbauen,&nbsp;</a><a>erstellen,&nbsp;</a><a>aufstellen</a><br><br>Ich '
    #            'glaube, das kann ich einrichten.<br><br>Ich muss das Haus mit '
    #            'weißen Möbeln einrichten.'}),
    #
    # ({'Вопрос': 'die Semmel -n', 'Ответ': 'булочка'}),
    #
    # ({'Add Reverse': '',
    #   'Back': 'хвалить<br><br>Я буду хвалить вас перед своим консорциумом в самых '
    #           'высоких тонах.',
    #   'Front': 'loben, lobte, hat gelobt<br><br>Ich werde Sie vor meinem '
    #            'Konsortium in den höchsten Tönen loben.<br><br>jemanden, sein Tun, '
    #            'Verhalten o.&nbsp;Ä. mit anerkennenden Worten (als Ermunterung, '
    #            'Bestätigung o.&nbsp;Ä.) positiv beurteilen und damit seiner '
    #            'Zufriedenheit, Freude o.&nbsp;Ä. Ausdruck geben'}),
    #
    # ({'Add Reverse': '',
    #   'Back': 'вещество<br><br>Вам понравится эта ткань.<br><br>Вещество сожжет '
    #           'тебя дотла.',
    #   'Front': 'der Stoff<br><br>Der Stoff wird dir gefallen.<br><br>Der Stoff '
    #            'brennt dich nieder.<br><br>'}),
    #
    # ({'Add Reverse': '',
    #   'Back': 'в любом случае, по крайней мере<br><br>Jedenfalls lächelte sie und '
    #           'sagte: Kein Problem<br><br>Во всяком случае, она улыбнулась и '
    #           'сказала: нет проблем',
    #   'Front': 'jedenfalls<br><br>Jedenfalls lächelte sie und sagte: Kein '
    #            'Problem<br>'}),
    #
    # ({'Перевод': 'еженедельный журнал', 'Слово': 'die Wochenzeitschrift'}),
    #
    # ({'Add Reverse': '',
    #   'Back': 'звучать, показаться, прозвучать<br><br>И, откровенно говоря, вы '
    #           'начинаете звучать немного безумно.<br><br>Я не хочу показаться '
    #           'эгоцентричным, но, похоже, ты смотришь только на меня.',
    #   'Front': 'klingen, klang, hat '
    #            'geklungen<br><br>Syn:&nbsp;<a>scheinen,&nbsp;</a><a>wirken,&nbsp;</a><a>aussehen,&nbsp;<a>anhören</a><br></a><br>Und '
    #            'offen gesagt fängst du an ein bisschen verrückt zu '
    #            'klingen.<br><br>Ich will nicht egozentrisch klingen, aber es '
    #            'scheint, du hast nur Augen für mich.<br>'}),
    #
    # ({'Add Reverse': '',
    #   'Back': 'повесить, зависеть, висеть<br><br>Könntest es über den '
    #           'Tresen&nbsp;<em>hängen</em>.<br><br>Ты его '
    #           'можешь&nbsp;<em>повесить</em>&nbsp;над стойкой.&nbsp;<br><br><img '
    #           'src="hängen.jpeg">',
    #   'Front': 'hängen, hing/hängte, hat gehangen/gehängt&nbsp;<br><br>Könntest es '
    #            'über den Tresen&nbsp;<em>hängen</em>.'}),
    #
    # ({'Add Reverse': '',
    #   'Back': '<div>пещера, логово, нора<br><br><font color="#7f7f7f">В горе есть '
    #           'несколько пещер.</font><br></div>',
    #   'Front': 'die&nbsp;Höhle<br><br>Syn: das&nbsp;<a>Loch, '
    #            'die&nbsp;</a><a>Grube, die&nbsp;Grotte<br></a><div><a>\n'
    #            '</a><div><a>\n'
    #            '</a><div><a>\n'
    #            '</a><div><ul><li>Im Berg gibt es mehrere '
    #            'Höhlen.&nbsp;</li><li><br></li><li>Vorsicht! In '
    #            'der&nbsp;<i>Höhle</i>&nbsp;dort lebt ein Bär.</li></ul></div>\n'
    #            '</div>\n'
    #            '</div></div>'}),
    #
    # ({'Перевод': 'растение', 'Слово': 'die Pflanze'}),
    #
    # ({'Вопрос': 'переезжать, переодевать',
    #   'Ответ': 'umziehen, ziehen '
    #            'um[sound:pronunciation_de_umziehen(1).mp3][sound:pronunciation_de_umziehen.mp3]',
    #   'Примеры': ''}),
    #
    # ({'Перевод': 'покупатель', 'Слово': 'der Käufer'}),
])
def test_convert(source_note: {str: str}, expected: GermanNote):
    result = convert(source_note)
    assert result == expected
