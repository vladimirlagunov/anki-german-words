import pytest

from german_word_addon.converter import convert, GermanNote, parse_note_from_wiktionary


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

    ({'Вопрос': 'der Frosch -:e', 'Ответ': 'лягушка'},
     GermanNote(word='Frosch', translation='лягушка')),

    ({'Add Reverse': '',
      'Back': 'претензия,&nbsp;иск<br><br>Отель расположен в центре города. Вот '
              'почему вы не имеете права на проездные деньги.',
      'Front': '<div>\n'
               '<div>\n'
               '<div>\n'
               '<div>\n'
               '<div>der Anspruch&nbsp;<br><br><div>\n'
               '<div>\n'
               '<div>\n'
               '<div>\n'
               '<div>Sie wohnen im Stadtzentrum. Deshalb\n'
               'haben Sie keinen Anspruch auf\n'
               'Fahrgeld.&nbsp;</div>\n'
               '</div>\n'
               '</div>\n'
               '</div></div></div>\n'
               '</div>\n'
               '</div>\n'
               '</div></div>'},
     GermanNote(word='Anspruch', translation='претензия, иск', examples=[
         ('Sie wohnen im Stadtzentrum. Deshalb haben Sie keinen Anspruch auf Fahrgeld.',
          'Отель расположен в центре города. Вот почему вы не имеете права на проездные деньги.')
     ]))

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


def test_wiktionary_verb_omonyms():
    wiktionary = (
        '{{Siehe auch|[[Hängen]]}}\n'
        '== hängen ({{Sprache|Deutsch}}) ==\n'
        "=== {{Wortart|Verb|Deutsch}}, ''transitiv'' ===\n"
        '\n'
        '{{Deutsch Verb Übersicht\n'
        '|Präsens_ich=hänge\n'
        '|Präsens_du=hängst\n'
        '|Präsens_er, sie, es=hängt\n'
        '|Präteritum_ich=hängte\n'
        '|Partizip II=gehängt\n'
        '|Konjunktiv II_ich=hängte\n'
        '|Imperativ Singular=hänge\n'
        '|Imperativ Singular*=häng\n'
        '|Imperativ Plural=hängt\n'
        '|Hilfsverb=haben\n'
        '}}\n'
        '\n'
        '{{Worttrennung}}\n'
        ':hän·gen, {{Prät.}} häng·te, {{Part.}} ge·hängt\n'
        '\n'
        '{{Aussprache}}\n'
        ':{{IPA}} {{Lautschrift|ˈhɛŋən}}\n'
        ':{{Hörbeispiele}} {{Audio|De-hängen.ogg}}, {{Audio|De-hängen2.ogg}}\n'
        ':{{Reime}} {{Reim|ɛŋən|Deutsch}}\n'
        '\n'
        '{{Bedeutungen}}\n'
        ':[1] {{K|trans.}} etwas an einem festen Punkt (durch das Eigengewicht nach '
        'unten baumelnd) befestigen\n'
        ':[2] {{K|trans.}} jemanden oder sich [[aufhängen]], '
        '[[töten]]/[[exekutieren]]\n'
        '\n'
        '{{Herkunft}}\n'
        ":mittelhochdeutsch ''hāhen,'' althochdeutsch ''hāhan,'' germanisch "
        "*''han-ha-'' „hängen“, „hängen lassen“. Das Wort ist seit dem 9. Jahrhundert "
        'belegt.<ref>{{Lit-Kluge: Etymologisches Wörterbuch|A=24}}, Stichwort: '
        '„hängen“, Seite 390.</ref> Die Entwicklung ist durch Koexistenz und '
        'Interferenz mit mehreren, ähnlich klingenden Verben charakterisiert. Die '
        'heutige standardsprachliche Verteilung, dass das transitive Verb schwach, '
        'das intransitive aber stark konjugiert wird, hat sich erst im 19. '
        'Jahrhundert herausgebildet.<ref>{{Literatur|Autor=Wolfgang Pfeifer '
        '[Leitung]|Titel=Etymologisches Wörterbuch des Deutschen|Auflage=2. '
        'durchgesehene und erweiterte|Verlag=Deutscher Taschenbuch '
        'Verlag|Ort=München|Jahr=1993|ISBN=3-423-03358-4}}, Stichwort „hängen“.</ref> '
        'Umgangssprachlich werden aber auch heute noch nicht selten die starken '
        'Formen auch bei transitivem Gebrauch verwendet.<ref>Vgl. etwa: „Während für '
        'mich klar war, dass ‚das Bild hängte an der Wand‘ falsch ist, war das bei '
        '‚Ich hing das Bild an die Wand‘ durchaus nicht klar. Erst in Grammatiken '
        'fand ich, dass ‚Ich hing das Bild an die Wand‘ standardsprachlich falsch '
        'ist. Trotzdem wird es offensichtlich umgangssprachlich verwendet.“ Auf: '
        'WordReference.com, Eintrag vom 20.&nbsp;Dezember 2012.</ref>\n'
        '\n'
        '{{Synonyme}}\n'
        ':[1] [[fixieren]]\n'
        ':[2] [[aufhängen]], [[aufknüpfen]], [[henken]], [[strangulieren]]\n'
        '\n'
        '{{Gegenwörter}}\n'
        ':[1] [[abhängen]], [[entfernen]], [[wegnehmen]]\n'
        '\n'
        '{{Unterbegriffe}}\n'
        ':[1] [[abhängen]], [[anhängen]], [[aufhängen]], [[aushängen]], [[behängen]], '
        '[[einhängen]], [[durchhängen]], [[herabhängen]], [[heraushängen]], '
        '[[hinaushängen]], [[raushängen]], [[reinhängen]], [[überhängen]], '
        '[[umhängen]], [[verhängen]], [[vorhängen]], [[weghängen]], '
        '[[zusammenhängen]]\n'
        ':[2] [[aufhängen]], [[erhängen]] (beides für [[strangulieren]]), '
        '[[mithängen]]\n'
        '\n'
        '{{Beispiele}}\n'
        ":[1] Ich ''hänge'' die Lampe zwischen die zwei Bilder.\n"
        ":[1] Ich ''hängte'' die Lampe an einen Haken am Türpfosten.\n"
        ':[1] „Während man jedoch beim Segelfliegen in einem kleinen Cockpit hockt, '
        "beim Gleitschirmfliegen in einem Sitz schaukelt, ''hängt'' der "
        'Drachenflieger unter der Tragfläche, Kopf voraus.“<ref>{{Internetquelle|url= '
        'https://www.ingenieur.de/technik/fachbereiche/raumfahrt/der-flug-drachen/|autor= '
        'Ingenieur.de|titel= Der Flug mit dem Drachen| tag= 12|monat= 11|jahr=1999 '
        '|zugriff= 2020-02-18}}</ref>\n'
        ":[2] Der Henker ''hängte'' den Dieb.\n"
        ':[2] Von nun an kann er einerseits ganz legal diejenigen verfolgen und '
        "töten, die ihn ''hängen'' wollten, andererseits wird er vom Richter "
        'verpflichtet, sich für Recht und Gesetz einzusetzen.\n'
        '\n'
        '{{Redewendungen}}\n'
        ":[1] [[mit Hängen und Würgen|mit ''Hängen'' und Würgen]]&nbsp;— mit Mühe, "
        'mit Hängenbleiben unterwegs, mit letzter Kraft\n'
        ':[2] [[mitgegangen, mitgefangen, mitgehangen|mitgegangen, mitgefangen, '
        "''mitgehangen'']]<!-- ad-hoc-Kompositum --> (statt korrekt ''mitgehängt'' – "
        'des Klanges wegen)\n'
        '\n'
        '{{Charakteristische Wortkombinationen}}\n'
        ":[1] [[an]] die [[Wand]] ''hängen'', [[auf]] einen [[Haken]] ''hängen'', "
        "[[über]] den [[Eingang]] ''hängen'', [[unter]] die [[Decke]] ''hängen'', "
        "[[zwischen]] etwas ''hängen''\n"
        '\n'
        '{{Wortbildungen}}\n'
        ':[[Hängegleiter]], [[Hängelippe]]\n'
        '\n'
        '==== {{Übersetzungen}} ====\n'
        '{{Ü-Tabelle|1|G=|Ü-Liste=\n'
        '*{{ar|DMG}}:\n'
        '**{{MHA}}: {{Üxx4|ar|علق|v=عَلَّقَ|d=ʿallaqa|DMG=0}}\n'
        '*{{en}}: {{Ü|en|hang}}\n'
        '*{{eo}}: {{Ü|eo|pendigi}}\n'
        '*{{fi}}: {{Ü|fi|ripustaa}}\n'
        '*{{fr}}: {{Ü|fr|accrocher}}, {{Ü|fr|pendre}}\n'
        '*{{el|iU}}: {{Üt|el|κρεμώ|kremó}}\n'
        '*{{ia}}: {{Ü|ia|appender}}\n'
        '*{{is}}: {{Ü|is|hengja}}\n'
        '*{{it}}: {{Ü|it|appendere}}\n'
        '*{{ca}}: {{Ü|ca|penjar}}, {{Ü|ca|suspendre}}\n'
        '*{{tlh}}: {{Ü|tlh|HuS}}\n'
        '*{{lv}}: {{Ü|lv|karāties}}\n'
        '*{{nds}}: {{Ü|nds|hangen}}\n'
        '*{{no}}: {{Ü|no|henge}}\n'
        '*{{pl}}: {{Ü|pl|wieszać}}\n'
        '*{{pt}}: {{Ü|pt|pender}}\n'
        '*{{ro}}: {{Ü|ro|atârna}}, {{Ü|ro|spânzura}}\n'
        '*{{ru}}: {{Üt|ru|вешать}}\n'
        '*{{sv}}: {{Ü|sv|hänga}}\n'
        '*{{wen}}:\n'
        "**{{hsb}}: {{Ü|hsb|pójsnyć}} ''perfektiv'', {{Ü|hsb|pójšeć}} "
        "''imperfektiv'', {{Ü|hsb|wěšeć}} ''imperfektiv''\n"
        '*{{es}}: {{Ü|es|colgar}}, {{Ü|es|ahorcar}}, {{Ü|es|fijar}}, '
        '{{Ü|es|enganchar}}\n'
        '*{{cs}}: {{Ü|cs|pověsit}}\n'
        '*{{hu}}: {{Ü|hu|felakaszt}} valamit\n'
        '|Dialekttabelle=\n'
        '*Alemannisch: hänke\n'
        '}}\n'
        '\n'
        '{{Ü-Tabelle|2|G=transitiv: jemanden oder sich aufhängen, '
        'töten/exekutieren|Ü-Liste=\n'
        '*{{ar|DMG}}:\n'
        '**{{MHA}}: {{Üxx4|ar|شنق|v=شَنَقَ|d=šanaqa|DMG=0}}\n'
        '*{{en}}: {{Ü|en|hang}}\n'
        '*{{fi}}: {{Ü|fi|hirttää}}\n'
        '*{{fr}}: {{Ü|fr|pendre}}\n'
        "*{{el|iU}}: ''<small>nicht reflexiv:</small>'' {{Üt|el|κρεμώ|kremó}}\n"
        '*{{it}}: {{Ü|it|impiccare}}\n'
        '*{{ca}}: {{Ü|ca|penjar}}, {{Ü|ca|enforcar}}\n'
        '*{{nds}}: {{Ü|nds|hangen}}, {{Ü|nds|opbummeln}}\n'
        '*{{pl}}: {{Ü|pl|wieszać}}\n'
        '*{{pt}}: {{Ü|pt|enforcar}}\n'
        '*{{ro}}: {{Ü|ro|spânzura}}\n'
        '*{{ru}}: {{Üt|ru|вешать}}\n'
        '*{{sv}}: {{Ü|sv|hänga}}\n'
        '*{{hu}}: {{Ü|hu|felakasztja magát}}, {{Ü|hu|felköti magát}}\n'
        '|Dialekttabelle=\n'
        '*Alemannisch: hänke\n'
        '}}\n'
        '\n'
        '{{Referenzen}}\n'
        ':[1, 2] {{Ref-Duden|haengen_verbinden_befestigen}}\n'
        ':[*] {{Ref-UniLeipzig}}\n'
        ':[1, 2] {{Ref-Grimm}}\n'
        '\n'
        '{{Quellen}}\n'
        '\n'
        "=== {{Wortart|Verb|Deutsch}}, ''intransitiv'' ===\n"
        '\n'
        '{{Deutsch Verb Übersicht\n'
        '|Präsens_ich=hänge\n'
        '|Präsens_du=hängst\n'
        '|Präsens_er, sie, es=hängt\n'
        '|Präteritum_ich=hing\n'
        '|Partizip II=gehangen\n'
        '|Konjunktiv II_ich=hinge\n'
        '|Imperativ Singular=hänge\n'
        '|Imperativ Singular*=häng\n'
        '|Imperativ Plural=hängt\n'
        '|Hilfsverb=haben\n'
        '|Hilfsverb*=sein\n'
        "|Bild=Vogelfutternetz_(fcm).jpg|mini|1|[[Plastikmüll]] ''hängt'' weiter im "
        '[[Strauch]], auch wenn die [[Vogel|Vögel]] den [[Meisenknödel]] [[längst]] '
        '[[fressen|gefressen]] haben.\n'
        '}}\n'
        '\n'
        '{{Anmerkung}}\n'
        ':Neben dem Hilfsverb „haben“ ist insbesondere in Süddeutschland, Österreich '
        "und der Schweiz auch die Verwendung des Hilfsverbs „sein“ gebräuchlich: ''er "
        "ist gehangen'' (neben ''er hat gehangen)'' und so weiter.\n"
        ':In der Schweiz kommt neben „hängen“ auch „[[hangen]]“ vor (mit Umlautung in '
        'der 2. und 3. Person Singular Präsens).<ref>{{Lit-Meyer: Schweizer '
        'Wörterbuch|J=2006}}, Seite 145, mit Belegen aus Max Frisch, Friedrich '
        'Dürrenmatt und der Neuen Zürcher Zeitung; {{Lit-Duden: '
        'Schweizerhochdeutsch|A=1}}, Seite 37.</ref>\n'
        '\n'
        '{{Worttrennung}}\n'
        ':hän·gen, {{Prät.}} hing, {{Part.}} ge·han·gen\n'
        '\n'
        '{{Aussprache}}\n'
        ':{{IPA}} {{Lautschrift|ˈhɛŋən}}\n'
        ':{{Hörbeispiele}} {{Audio|De-hängen.ogg}}, {{Audio|De-hängen2.ogg}}\n'
        ':{{Reime}} {{Reim|ɛŋən|Deutsch}}\n'
        '\n'
        '{{Bedeutungen}}\n'
        ':[1] {{K|intrans.}} an einem festen Punkt [wegen des Eigengewichts] nach '
        'unten baumelnd befestigt sein\n'
        ':[2] {{K|intrans.|ft=an jemandem/etwas hängen}} sehr gern haben, nicht auf '
        'die Person/Sache verzichten wollen\n'
        ':[3] {{K|intrans.|umgangssprachlich}} keine [[Fortschritt]]e [mehr] machen, '
        'nicht weitergehen\n'
        '\n'
        '{{Herkunft}}\n'
        ":mittelhochdeutsch ''hāhen,'' althochdeutsch ''hāhan,'' germanisch "
        "*''han-ha-'' „hängen“, „hängen lassen“. Das Wort ist seit dem 9. Jahrhundert "
        'belegt.<ref>{{Lit-Kluge: Etymologisches Wörterbuch|A=24}}, Stichwort: '
        '„hängen“, Seite 390.</ref> Die Entwicklung ist durch Koexistenz und '
        'Interferenz mit mehreren, ähnlich klingenden Verben charakterisiert.  Die '
        'heutige standardsprachliche Verteilung, dass das transitive Verb schwach, '
        'das intransitive aber stark konjugiert wird, hat sich erst im 19. '
        'Jahrhundert herausgebildet.<ref>{{Literatur|Autor=Wolfgang Pfeifer '
        '[Leitung]|Titel=Etymologisches Wörterbuch des Deutschen|Auflage=2. '
        'durchgesehene und erweiterte|Verlag=Deutscher Taschenbuch '
        'Verlag|Ort=München|Jahr=1993|ISBN=3-423-03358-4}}, Stichwort '
        '„hängen“.</ref>\n'
        '\n'
        '{{Synonyme}}\n'
        ':[1] [[baumeln]]\n'
        ':[3] [[aufhängen]], [[festfahren]], [[pausieren]], [[stagnieren]], '
        '[[stocken]]\n'
        '\n'
        '{{Unterbegriffe}}\n'
        ':[1] [[abhängen]] (jugendsprachlich: [[verweilen]]), [[anhängen]], '
        '[[herabhängen]], [[herunterhängen]], [[hinabhängen]], [[hinunterhängen]], '
        '[[überhängen]], [[zusammenhängen]]\n'
        ':[2] [[mithängen]]\n'
        ':[3] [[nachhängen]]\n'
        '\n'
        '{{Beispiele}}\n'
        ":[1] Die Lampe ''hängt'' zwischen den zwei Bildern.\n"
        ":[1] Die Lampe ''hing'' am Balken im Stall.\n"
        ':[1] [Schlagzeile:] „Energiepreise zu hoch: Apfelbauern lassen viele Äpfel '
        "''hängen''“<ref>{{Per-Norddeutscher Rundfunk | "
        'Online=https://www.ndr.de/nachrichten/info/Energiepreise-zu-hoch-Apfelbauern-lassen-viele-Aepfel-haengen,apfelernte544.html '
        '| Autor=Astrid Kühn | Titel=Energiepreise zu hoch: Apfelbauern lassen viele '
        'Äpfel hängen | TitelErg= | Tag=04 | Monat=11 | Jahr=2022 | '
        'Zugriff=2022-11-04 | Kommentar= }}</ref>\n'
        ":[1] Der Mörder ''hing'' am Galgen.\n"
        ":[2] Siehst du, so haben wir an dir ''gehangen,'' und dafür willst du uns "
        "schon nach ein paar Tagen den Rücken kehren!<ref>Hermann Sudermann, ''Der "
        "Katzensteg'' (Kurzausgabe, redigiert von Benjamin W. Wells, 1899), Seite "
        '7</ref>\n'
        ":[2] ''österreichisch:'' „Er ''ist an dir gehangen,'' wie selten ein Sohn "
        "''an seiner Mutter hängt''.“<ref>[[w:Dolores Viesèr|Dolores Viesèr]], "
        "''Kleiner Bruder'' (1956), Seite 75</ref>\n"
        ":[3] Das Programm ''hängt'' immer mal wieder kurz.\n"
        ':[3] Sag das Gedicht noch einmal auf, nicht dass du morgen '
        "''hängenbleibst!''\n"
        ":[3] Die ganze Vorbereitung der Feier ''hängt,'' weil Tobias unbedingt jetzt "
        'Urlaub machen muss.\n'
        '\n'
        '{{Redewendungen}}\n'
        ":[[den Kopf hängen lassen|den Kopf ''hängen'' lassen]]\n"
        ":[[jemanden hängen lassen|jemanden ''hängen'' lassen]] – jemanden im Stich "
        'lassen\n'
        ":[[der Haussegen hängt schief|der Haussegen ''hängt'' schief]]\n"
        ":[[an einem seidenen Faden hängen|an einem seidenen Faden ''hängen'']] – "
        'sich in einer knappen, ungewissen [[Situation]] befinden\n'
        '\n'
        '{{Charakteristische Wortkombinationen}}\n'
        ":[1] [[auf]], [[über]], [[unter]], [[zwischen]] etwas ''hängen;'' nach "
        "[[links]], [[rechts]], [[oben]], [[unten]] ''hängen''\n"
        ":[3] ''hängen'' [[bleiben]] (feststecken)\n"
        '\n'
        '{{Wortbildungen}}\n'
        ':[[Gehänge]], [[Hängebrücke]], [[Hängebrust]], [[Hängebusen]], '
        '[[Hängedach]], [[Hängeschrank]], [[Hängetitten]]\n'
        ':[[verhangen]]\n'
        '\n'
        '==== {{Übersetzungen}} ====\n'
        '{{Ü-Tabelle|1|G=|Ü-Liste=\n'
        '*{{en}}: {{Ü|en|hang}}\n'
        '*{{eo}}: {{Ü|eo|pendi}}\n'
        '*{{fi}}: {{Ü|fi|riippua}}, {{Ü|fi|roikkua}}\n'
        '*{{fr}}: {{Ü|fr|être suspendu}}\n'
        '*{{el}}: {{Üt|el|κρέμομαι|krémome}}\n'
        '*{{is}}: {{Ü|is|hanga}}\n'
        '*{{it}}: {{Ü|it|pendere}}\n'
        '*{{ca}}: {{Ü|ca|penjar}}, {{Ü|ca|estar penjat}}\n'
        '*{{lt}}: {{Ü|lt|kabėti}}\n'
        '*{{nds}}: {{Ü|nds|hangen}}, {{Ü|nds|bummeln}}\n'
        '*{{pdt}}: {{Ü|pdt|henjen}}\n'
        '*{{pl}}: {{Ü|pl|wisieć}}\n'
        '*{{ro}}: {{Ü|ro|atârna}}\n'
        '*{{ru}}: {{Üt|ru|висеть}}\n'
        '*{{sv}}: {{Ü|sv|hänga}}\n'
        '*{{wen}}:\n'
        '**{{dsb}}: {{Ü|dsb|wisaś}}\n'
        '**{{hsb}}: {{Ü|hsb|wisać}}\n'
        '*{{es}}: {{Ü|es|colgar}}, {{Ü|es|suspender}}\n'
        '*{{cs}}: {{Ü|cs|viset}}\n'
        '|Dialekttabelle=\n'
        '*Alemannisch: hange\n'
        '}}\n'
        '\n'
        '{{Ü-Tabelle|2|G=|Ü-Liste=\n'
        '*{{en}}: {{Ü|en|be fond of}}, {{Ü|en|love}}\n'
        '*{{it}}: {{Ü|it|attaccarsi}}, {{Ü|it|affezionarsi}}\n'
        '*{{ca}}: {{Ü|ca|dependre}}\n'
        '*{{ro}}: {{Ü|ro|lega}}, {{Ü|ro|atașa}}\n'
        '*{{sv}}: {{Ü|sv|vara fäst vid}}\n'
        '*{{cs}}: {{Ü|cs|viset}}\n'
        '|Dialekttabelle=\n'
        '*Alemannisch: hange\n'
        '}}\n'
        '\n'
        '{{Ü-Tabelle|3|G=|Ü-Liste=\n'
        '*{{en}}: {{Ü|en|hang}}\n'
        '*{{it}}: {{Ü|it|bloccarsi}}, {{Ü|it|fermarsi}}\n'
        '*{{ro}}: {{Ü|ro|bloca}}\n'
        '*{{sv}}: {{Ü|sv|hänga}}\n'
        '*{{cs}}: {{Ü|cs|viset}}\n'
        '}}\n'
        '\n'
        '{{Referenzen}}\n'
        ':[1–3] {{Ref-Grimm}}\n'
        ':[1–3] {{Ref-DWDS}}\n'
        ':[*] {{Ref-UniLeipzig}}\n'
        '\n'
        '{{Quellen}}\n'
        '\n'
        '{{Ähnlichkeiten 1|[[hangeln]], [[henken]]|Anagramme=[[gähnen]]}}'
    )

    note = parse_note_from_wiktionary(wiktionary)

    assert note == {
        'DrittenPerson': {'hängt'},
        'Perfekt': {'haben gehangen', 'haben gehängt'},
        'Präteritum': {'hängte', 'hing'},
        'WordTranslation': {'висеть', 'вешать'},
    }
