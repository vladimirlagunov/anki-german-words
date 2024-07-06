from PyQt6 import QtGui
from PyQt6.QtCore import QObject, pyqtSignal

import json
import os.path
import pprint
import re
import urllib.parse
import urllib.request
import webbrowser
from anki.models import NotetypeDict
from aqt import qconnect, dialogs
from aqt.addcards import AddCards
from aqt.browser import Browser
from aqt.utils import showWarning
from german_word_addon import converter
from german_word_addon.converter import html_to_text, get_chatgpt_responses_texts
from typing import Callable, Optional, Dict

universal_german_word_template_name = 'Universal German word template'


def get_universal_german_word_note_type(mw) -> NotetypeDict:
    if (expected_note_type := mw.col.models.by_name(universal_german_word_template_name)) is None:
        showWarning(
            f'There must be a note template called `{universal_german_word_template_name}`. It is used for generating cards.')
    return expected_note_type


def fill_german_word_fields(editor: 'aqt.editor.Editor'):
    # from pprint import pprint
    # pprint(editor.__dict__)
    # pprint(editor.note.__dict__)

    if not (expected_note_type := get_universal_german_word_note_type(editor.mw)):
        return

    note: 'anki.notes.Note' = editor.note
    if note.note_type() is None or note.note_type()['name'] != expected_note_type['name']:
        actual_name = note.note_type()['name'] if note.note_type() else None
        showWarning(f'The note type must be `{universal_german_word_template_name}`, but it is `{actual_name}`.')
        return

    _fill_card(editor)

    # message_box = QMessageBox(editor.mw.app.activeWindow())
    # message_box.setText("Loading...")
    # message_box.show()

    # t = Thread(target=_fill_card, args=(message_box, editor))
    # t.daemon = True
    # t.start()

    # t = QThread()
    # w = _Worker(partial(_fill_card, editor))
    # w.moveToThread(t)
    #
    # t.started.connect(w.run)
    # w.finished.connect(t.quit)
    # w.finished.connect(w.deleteLater)
    # t.finished.connect(t.deleteLater)
    # w.finished.connect(message_box.hide)
    #
    # result = []
    # editor._hacky_data = (t, w, result)
    #
    # t.start()


class _Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, task: Callable[[], None]):
        super().__init__()
        self._task = task

    def run(self):
        try:
            self._task()
        finally:
            self.finished.emit()


def _fill_card(editor: 'aqt.editor.Editor'):
    note: 'anki.notes.Note' = editor.note

    word = note['Word']

    import bs4
    word = bs4.BeautifulSoup(word, 'html.parser').get_text().strip()

    word = (
        word
        .strip()
        .split("\n", 1)[0]
        .removeprefix('der ')
        .removeprefix('die ')
        .removeprefix('das ')
        .rstrip()
    )
    word = re.sub('[-(,].*', '', word)

    note['Word'] = word
    print("Checking word:", word)

    _fill_note_from_wiktionary(note)

    editor.loadNote()
    print("done")


def _fill_note_from_wiktionary(note):
    word = note['Word'].replace("sich", "").strip()
    wiktionary = _wiktionary_entry(word)
    pprint.pprint(wiktionary)

    if not wiktionary:
        return

    new_dict = converter.parse_note_from_wiktionary(wiktionary)
    for k, v in new_dict.items():
        if note[k] and note[k] not in v:
            v.append(note[k])
        if len(v) == 0:
            continue
        elif len(v) == 1:
            note[k] = v[0]
        else:
            v_str = "<ul>\n<li>" + "</li>\n<li>".join(v) + "</li>\n</ul>"
            note[k] = v_str


def _wiktionary_entry(word: str) -> str:
    url = f"https://de.wiktionary.org/w/api.php"
    params = {
        "action": "parse",
        "format": "json",
        "page": word,
        "prop": "wikitext",
        "formatversion": "2",
    }
    data = urllib.parse.urlencode(params)
    data = data.encode('ascii')  # data should be bytes
    req = urllib.request.Request(url, data)
    with urllib.request.urlopen(req) as response:
        return json.load(response).get('parse', {}).get('wikitext')


# {{Siehe auch|[[wort]]}}
# {{Wort der Woche|23|2006}}
# == Wort ({{Sprache|Deutsch}}) ==
# === {{Wortart|Substantiv|Deutsch}}, {{n}}, Wörter ===
#
# {{Deutsch Substantiv Übersicht
# |Genus=n
# |Nominativ Singular=Wort
# |Nominativ Plural=Wörter
# |Genitiv Singular=Worts
# |Genitiv Singular*=Wortes
# |Genitiv Plural=Wörter
# |Dativ Singular=Wort
# |Dativ Singular*=Worte
# |Dativ Plural=Wörtern
# |Akkusativ Singular=Wort
# |Akkusativ Plural=Wörter
# }}
#
# {{Anmerkung|zur Trennung der Pluralformen}}
# :Die bedeutungsunterscheidende Trennung der Pluralformen „Wörter“ und „Worte“ kommt im 16. Jahrhundert auf. Nachdem [[w:Justus Georg Schottelius|Schottel]] sie im 17. Jahrhundert zur Norm erhebt, was von nachfolgenden Sprachgelehrten fortgeführt wird, setzt sie sich langsam bis zum 19. Jahrhundert durch. Besonders in informaler Rede wird die Trennung heutzutage allerdings nicht konsequent vollzogen. Dabei ist anzumerken, dass die Pluralform „Worte“ häufiger für die Bedeutungen der anderen Form gebraucht wird als andersherum.<ref>{{Ref-Grimm|Wort|id=GW26937}}</ref><ref>{{Ref-DWDS|Wort}}</ref>
#
# {{Worttrennung}}
# :Wort, {{Pl.}} Wör·ter
#
# {{Aussprache}}
# :{{IPA}} {{Lautschrift|vɔʁt}}
# :{{Hörbeispiele}} {{Audio|De-Wort.ogg}}, {{Audio|De-Wort2.ogg}}
# :{{Reime}} {{Reim|ɔʁt|Deutsch}}
#
# {{Bedeutungen}}
# :[1] {{K|Linguistik}} [[klein]]ste, eine [[selbstständig]]e [[Bedeutung]] [[tragend]]e [[Einheit]] der [[Sprache]], eine [[grammatisch]]e Einheit
# :[2] {{K|Theoretische Informatik|formale Sprachen}} eine endliche [[Folge]] von [[Symbol]]en aus einem [[Alphabet]]
# :[3] {{K|Programmiersprachen|Rechnerarchitektur|ft=Plural auch: „Worte“}} als [[Einheit]] betrachtete [[Kette]] nebeneinanderliegender [[Bit]]s / [[Byte]]s in definierter [[Länge]]
#
# {{Herkunft}}
# :[[mittelhochdeutsch]] ''wort'', [[althochdeutsch]] ''wort'', [[germanisch]] *''wurda-'' „Wort“, [[indogermanisch]] *''werd<sup>h</sup>o-'' „Wort“; das Wort ist seit dem 8. [[Jahrhundert]] belegt.<ref>{{Lit-Kluge: Etymologisches Wörterbuch|A=24}}, Stichwort: „Wort“, Seite 997.</ref>
#
# {{Synonyme}}
# :[1] [[Ausdruck]], [[Begriff]], [[Lexem]], [[Vokabel]]
# :[2] [[Zeichenkette]]
# :[3] [[Binärwort]]
#
# {{Gegenwörter}}
# :[3] [[Doppelwort]], [[Halbwort]], [[Langwort]]
#
# {{Verkleinerungsformen}}
# :[[Wörtchen]], [[Wörtlein]]
#
# {{Oberbegriffe}}
# :[1] [[Lexikon]]
# :[2] [[Zeichenkette]]
# :[3] [[Datenwort]]
#
# {{Unterbegriffe}}
# :[1] [[Abkürzungswort]], [[Allerweltswort]], [[Ankerwort]], [[Anredewort]], [[Artikelwort]], [[Bandwurmwort]], [[Basiswort]], [[Bastardwort]], [[Beispielwort]], [[Bestimmungswort]], [[Beziehungswort]], [[Bezugswort]], [[Bindewort]], [[Brückenwort]], [[Buchstabenwort]], [[Codewort]], [[Dienstwort]], [[Duwort]], [[Echowort]], [[Einleitewort]]/[[Einleitungswort]], [[Einzelwort]], [[Endwort]], [[Erbwort]], [[Fachwort]], [[Farbwort]], [[Formwort]], [[Fragewort]], [[Fremdwort]], [[Füllwort]], [[Funktionswort]], [[Gegenwort]], [[Geruchswort]], [[Gesamtwort]], [[Grundwort]], [[Hehlwort]], [[Hilfswort]], [[Hohnwort]], [[Hüllwort]], [[Inhaltswort]], [[Initialwort]], [[Januswort]], [[Jugendwort]], [[Kennwort]], [[Klappwort]], [[Kofferwort]], [[Kopfwort]], [[Kunstwort]], [[Kurzwort]], [[Lagewort]], [[Lallwort]], [[Leerwort]], [[Lehnwort]], [[Leitwort]], [[Lieblingswort]], [[Lösungswort]], [[Negationswort]], [[Neuwort]], [[Oppositionswort]], [[Passwort]], [[Pluralwort]], [[Pro-Wort]], [[Pseudowort]], [[Raffwort]], [[Reimwort]], [[Rumpfwort]], [[Sanskritwort]], [[Satzwort]], [[Schachtelwort]], [[Schallwort]], [[Scheltwort]], [[Schimpfwort]], [[Schlagwort]], [[Schlüsselwort]], [[Schmähwort]], [[Schmeichelwort]], [[Schwanzwort]], [[Schwurwort]], [[Sichtwort]], [[Siegerwort]], [[Silbenkurzwort]], [[Silbenwort]], [[Slangwort]], [[Spottwort]], [[Stammwort]], [[Steigerungswort]], [[Stichwort]], [[Strukturwort]], [[Stummelwort]], [[Stützwort]], [[Systemwort]], [[Tarnwort]], [[Textwort]], [[Trabantenwort]], [[Übersetzungswort]], [[Unwort]], [[Urwort]], [[Vollwort]], [[Vulgärwort]], [[W-Wort]], [[Zielwort]], [[Zitatwort]], [[Zwillingswort]], [[Zwitterwort]]
# :[1] ''([[Redeteil]]e, [[Wortart]]en)'' [[Ausrufewort]], [[Beiwort]], [[Bindewort]], [[Dingwort]], [[Eigenschaftswort]], [[Fürwort]], [[Geschlechtswort]], [[Hauptwort]], [[Hilfszeitwort]], [[Mittelwort]], [[Namenwort]], [[Nebenwort]], [[Nennwort]], [[Tätigkeitswort]], [[Tuwort]], [[Umstandswort]], [[Verhältniswort]], [[Vorwort]], [[Zahlwort]], [[Zeitwort]]
# :[1] [[Buchstabe]], [[Silbe]], [[Phonem]], [[Wortelement]]
# :[2] [[leeres Wort]]
#
# {{Beispiele}}
# :[1] ''Wörter'' kann man zählen, nach ''Worten'' muss man ringen.
# :[1] Sätze bestehen aus ''Wörtern.''
# :[1] „Mit Selbstverständlichkeit erlernt der Sprecher das ''Wort'' als Grundeinheit der Sprache, als Benennungseinheit, Bedeutungseinheit und Träger zusätzlicher Informationen.“<ref>Thea Schippan: ''Lexikologie der deutschen Gegenwartssprache,'' Niemeyer, Tübingen 1992, Seite 86, ISBN 3-484-73002-1, Gesperrt gedruckt: ''Grundeinheit.''</ref>
# :[1] „Hier soll unter ''Wort'' verstanden werden ein selbständiges Element einer sprachlichen Äußerung, das nicht aus anderen selbständigen Elementen besteht.“<ref>''Kluge. Etymologisches Wörterbuch der deutschen Sprache'', Bearbeitet von Elmar Seebold, 24. durchgesehene und erweiterte Auflage, de Gruyter, Berlin/ New York 2002, S. XIII, ISBN 3-11-017472-3, Fett gedruckt: '''Wort'''.</ref>
# :[1] „Alle ''Wörter'' einer Wortart haben eine bestimmte Art der Bedeutung.“<ref>{{Literatur| Autor=Karl-Dieter Bünting, Dorothea Ader |Titel=Grammatik auf einen Blick |TitelErg= Die deutsche Sprache und ihre Grammatik mit einem Grammatiklexikon|Auflage= |Verlag= Isis |Ort = Chur |Jahr= 1994| Seiten= 33. |ISBN= }}</ref>
# :[1] „''Wörter'' und Wortgruppen, die als Zitate aus einer fremden Sprache angesehen werden, bleiben in der Schreibung meist völlig unverändert <A O (3.1) a>.“<ref>{{Lit-Duden: Rechtschreibung|A=27}}, Seite 44.</ref>
# :[2] Das ''Wort'' <math>w=abab</math> ist ein Wort über dem Alphabet <math>\Sigma = \lbrace a,\, b \rbrace</math>.
# :[3] „Gruppen von 2, 4, oder 8 Bytes werden auch als ''Wort'' (2 Bytes), Doppelwort (4 Bytes) bzw. Langwort (8 Bytes) bezeichnet.“ (aus: „Bytes, ''Worte'' und Dateien“<ref>Universität Bremen, [http://www.informatik.uni-bremen.de/~sbosse/lehre/gdi/Vorlesung02.pdf Grundlagen der Informatik I], Seite 8</ref>)
# :[3] „Neben den üblichen Bezeichnungen verwenden einige Hersteller andere Bezeichnungen. So bezeichnen sie Wortlängen von 16 Bit als Halbwort, 32 Bit als ''Wort'' und 64 Bit Wortlänge als Doppelwort.“<ref> ITwissen.info, Online-Lexikon für Informationstechnologie: „[http://www.itwissen.info/definition/lexikon/Wortlaenge-word-length.html Wortlänge]“</ref>
# :[3] „Bei den Gleitkommazahlen hat man die beiden Varianten von einfacher und doppelter Genauigkeit […], die als ''Wort'' oder als Doppelwort gespeichert werden.“<ref>{{Literatur | Autor=Michael Teuffel, Robert Vaupel | Titel=Das Betriebssystem z/OS und die zSeries | TitelErg=Die Darstellung eines modernen Großrechnersystems | Band= | Verlag=Walter de Gruyter | Jahr=2004 |Seiten=19| Online=Zitiert nach {{GBS|wWLoBQAAQBAJ|PT20|Hervorhebung=Wort}}}}.</ref>
# :[3] „Direkt zugreifbar im Speicher sind das Byte, das ''Wort'' und das Doppelwort, wobei sich deren Adressen, unabhängig von den Datenformaten, üblicherweise auf Bytegrenzen beziehen.“ <ref>{{Literatur | Autor=Thomas Flik, Hans Liebig | Titel=Mikroprozessortechnik: CISC, RISC Systemaufbau Assembler und C | TitelErg= | Band= | Verlag=Springer-Verlag | Jahr=2013 |Seiten=70| Online=Zitiert nach {{GBS|NU6yBgAAQBAJ|PA70|Hervorhebung=Wort}}}}.</ref>
#
# {{Redewendungen}}
# :[1] [[ein Mann, ein Wort|Ein Mann, ein ''Wort'']] ''(manchmal spöttisch ergänzt:'' [[ein Mann, ein Wort, eine Frau, ein Wörterbuch|Ein Mann, ein ''Wort'', eine Frau, ein Wörterbuch]])
# :[1] „Du sprichst ein großes ''Wort'' gelassen aus.“ (Johann Wolfgang von [[Goethe]], ''[[Iphigenie]]'')
#
# {{Charakteristische Wortkombinationen}}
# :[1] ein [[kurz]]es / [[lang]]es ''Wort''; ''Wort'' für ''Wort'' diktieren; ein ''Wort'' falsch / richtig schreiben
# :[1] [[grammatisches Wort]], [[graphematisches Wort]], [[graphisches Wort]], [[lexikalisches Wort]], [[mögliches Wort]], [[morphologisches Wort]], [[motiviertes Wort]], [[orthographisches Wort]], [[phonetisches Wort]], [[phonologisches Wort]], [[potenzielles Wort]], [[semantisches Wort]], [[syntaktisches Wort]]
# :[1] ''[[Linguistik]]:'' das grammatische / lexikalische / orthographische / phonetische ''Wort''
#
# {{Wortbildungen}}
# :''[[Adjektiv]]e/[[Adverb]]ien:''
# :[1] [[wortarm]], [[wortgetreu]], [[wortgewaltig]], [[wortgewandt]], [[wortkarg]], [[wörtlich]], [[wortlos]], [[wortmächtig]], [[wortreich]], [[wortwörtlich]]
# :''[[Substantiv]]e:''
# :[1] [[Einwortsatz]], [[Wortakzent]], [[Wortanfang]], [[Wortarmut]], [[Wortart]], [[Wortartikel]], [[Wortbedeutung]], [[Wortbeitrag]], [[Wortbestand]], [[Wortbetonung]], [[Wortbildung]], [[Wortdauer]], [[Wortdefinition]], [[Wortebene]], [[Wortende]], [[Wortendung]], [[Worterklärung]], [[Wortfindungsstörung]], [[Wörterbuch]], [[Wörterverzeichnis]], [[Wortfamilie]], [[Wortfeld]], [[Wortfetzen]], [[Wortfindung]], [[Wortfolge]], [[Wortform]], [[Wortforschung]], [[Wortfrequenz]], [[Wortgattung]], [[Wortgebrauch]], [[Wortgefecht]], [[Wortgeographie]], [[Wortgeschichte]], [[Wortgrammatik]], [[Wortgrenze]], [[Wortgruppe]], [[Wortgut]], [[Worthäufigkeit]], [[Wortherkunft]], [[Worthülse]], [[Wortkarte]], [[Wortkette]], [[Wortkombination]], [[Wortkonstruktion]], [[Wortkunde]], [[Wortlänge]], [[Wortlaut]], [[Wortliste]], [[Wortmarke]], [[Wortmeldung]], [[Wortmelodie]], [[Wortmodell]], [[Wortnot]], [[Wortpaar]], [[Wortreichtum]], [[Wortschatz]], [[Wortschöpfer]], [[Wortschöpfung]], [[Wortschwall]], [[Wortsemantik]], [[Wortsilbe]], [[Wortsinn]], [[Wortstamm]], [[Wortstellung]], [[Wortstruktur]], [[Wortteil]], [[Worttrenner]], [[Worttrennung]], [[Wortungeheuer]], [[Wortungetüm]], [[Wortverbindung]], [[Wortwahl]], [[Wortwolke]], [[Wortwurzel]], [[Wortzauber]]
# :[1] [[Kreuzwortmosaik]], [[Kreuzworträtsel]]
# :[3] [[Wortbreite]], [[Wortlänge]]
#
# ==== {{Übersetzungen}} ====
# {{Ü-Tabelle|1|G=kleinste, eine selbstständige Bedeutung tragende Einheit der Sprache|Ü-Liste=
# *{{af}}: {{Ü|af|woord}} {{n}}
# *{{sq}}: {{Ü|sq|fjalë}}
# *{{ar|DMG}}:
# **{{MHA}}: {{Üxx4|ar|كلمة|v=كَلِمَة|d=kalima|DMG=0}} {{f}}
# **{{arz}}: {{Üxx4|ar|كلمة|v=كِلْمَة|d=kilma|DMG=0}} {{f}}
# *{{hy}}: {{Üt|hy|բառ|bar}}
# *{{rup}}: {{Üt|rup|збор|zbor}}
# *{{az}}: {{Ü|az|söz}}
# *{{ast}}: {{Ü|ast|pallabra}} {{f}}, {{Ü|ast|verbu}} {{m}}
# *{{eu}}: {{Ü|eu|hitz}}, {{Ü|eu|berba}}
# *{{bn}}: {{Üt|bn|শব্দ|shôbdô}}
# *{{bs}}: {{Üt|bs|ријеч|riječ}} {{f}}
# *{{br}}: {{Ü|br|ger}} {{m}}
# *{{bg}}: {{Üt|bg|дума}} {{f}}
# *{{zh}}:
# **{{zh-tw}}: {{Üt|zh|詞|cí}}
# **{{zh-cn}}: {{Üt|zh|词|cí}}
# *{{da}}: {{Ü|da|ord}} {{n}}
# *{{en}}: {{Ü|en|word}}, {{Ü|en|term}}, {{Ü|en|expression}}
# *{{eo}}: {{Ü|eo|vorto}}
# *{{et}}: {{Ü|et|sõna}}
# *{{fo}}: {{Ü|fo|orð}}
# *{{fi}}: {{Ü|fi|sana}}
# *{{fr}}: {{Ü|fr|mot}} {{m}}
# *{{fur}}: {{Ü|fur|peraule}} {{f}}
# *{{gl}}: {{Ü|gl|palabra}} {{f}}, {{Ü|gl|vocábulo}} {{m}}
# *{{ka}}: {{Üt|ka|სიტყვა|sit'qva}}
# *{{el}}: {{Üt|el|λέξη|léxi}} {{f}}
# *{{kl}}: {{Ü|kl|oqaaseq}}
# *{{gn}}: {{Ü|gn|ñe'ẽ}}
# *{{he}}: {{Üt|he|מלה|mîllá}}
# *{{hil}}: {{Ü|hil|pulong}}
# *{{io}}: {{Ü|io|vorto}}
# *{{ilo}}: {{Ü|ilo|balikas}}
# *{{id}}: {{Ü|id|kata}}
# *{{ia}}: {{Ü|ia|parola}}
# *{{ie}}: {{Ü|ie|parol}}
# *{{ga}}: {{Ü|ga|focal}} {{m}}
# *{{is}}: {{Ü|is|orð}} {{n}}
# *{{it}}: {{Ü|it|parola}} {{f}}, {{Ü|it|vocabolo}} {{m}}, {{Ü|it|termine}} {{m}}
# *{{ja}}: {{Üt|ja|言葉|ことば, kotoba}}, {{Üt|ja|単語|たんご, tango}}, {{Üt|ja|語句|ごく, goku}}
# *{{ca}}: {{Ü|ca|paraula}} {{f}}
# *{{tlh}}: {{Ü|tlh|mu’}}
# *{{ko}}: {{Üt|ko|낱말|}}, {{Üt|ko|단어|}}, {{Üt|ko|말|}}
# *{{kw}}: {{Ü|kw|ger}} {{m}}
# *{{co}}: {{Ü|co|parolla}} {{f}}, {{Ü|co|parodda}} {{f}}
# *{{hr}}: {{Ü|hr|riječ}} {{f}}
# *{{ku}}:
# **{{kmr}}: {{Ü|kmr|peyv}} {{f}}
# *{{la}}: {{Ü|la|verbum}} {{n}}, {{Ü|la|dictio}} {{f}}, {{Ü|la|vox}} {{f}}, {{Ü|la|vocabulum}} {{n}}
# *{{ltg}}: {{Ü|ltg|vuords}}
# *{{lv}}: {{Ü|lv|vārds}} {{m}}
# *{{lt}}: {{Ü|lt|žodis}}
# *{{lb}}: {{Ü|lb|Wuert}} {{f}}
# *{{gv}}: {{Ü|gv|fockle}} {{m}}
# *{{mr}}: {{Üt|mr|शब्द|}} {{m}}
# *{{mk}}: {{Üt|mk|збор|zbor}} {{m}}, {{Üt|mk|реч|reč}} {{f}}
# *{{lus}}: {{Ü|lus|thumal}}
# *{{ne}}: {{Üt|ne|शब्द|}}
# *{{nds}}: {{Ü|nds|Woort}} {{n}}
# *{{nl}}: {{Ü|nl|woord}}
# *{{se}}: {{Ü|se|sátni}}
# *{{no}}: {{Ü|no|ord}} {{n}}
# *{{nov}}: {{Ü|nov|vorde}}
# *{{oc}}: {{Ü|oc|paraula}} {{f}}
# *{{fa}}: {{Üt|fa|واژه|}}, {{Üt|fa|کلمه|}}
# *{{pl}}: {{Ü|pl|słowo}} {{n}}, {{Ü|pl|wyraz}} {{m}}
# *{{pt}}: {{Ü|pt|vocábulo}} {{m}}, {{Ü|pt|palavra}} {{f}}
# *{{rm}}: {{Ü|rm|pled}} {{m}}
# *{{ro}}: {{Ü|ro|cuvânt}} {{n}}
# *{{ru}}: {{Üt|ru|слово}} {{n}}
# *{{gd}}: {{Ü|gd|facal}} {{m}}
# *{{sv}}: {{Ü|sv|ord}} {{n}}
# *{{sco}}: {{Ü|sco|wird}}
# *{{sr}}: {{Üt|sr|реч|reč}} {{f}}, {{va.|:}} {{Üt|sr|збор|zbor}} {{m}}
# *{{sh}}: {{Üt|sh|реч|reč}} {{f}}, {{Üt|sh|ријеч|riječ}} {{f}}
# *{{sd}}: {{Üt|sd|لفظ|}} {{m}}
# *{{sk}}: {{Ü|sk|slovo}} {{n}}
# *{{sl}}: {{Ü|sl|beseda}} {{f}}
# *{{wen}}:
# **{{dsb}}: {{Ü|dsb|słowo}} {{n}}
# **{{hsb}}: {{Ü|hsb|słowo}} {{n}}
# *{{es}}: {{Ü|es|palabra}} {{f}}
# *{{sux}}: {{Ü|sux|inim}}
# *{{tg}}: {{Üt|tg|вожа}}, {{Üt|tg|калима|kalima}}
# *{{th}}: {{Üt|th|คำ|kam}}, {{Üt|th|ศัพท์|sàp}}
# *{{cs}}: {{Ü|cs|slovo}} {{n}}
# *{{tr}}: {{Ü|tr|kelime}}, {{Ü|tr|sözcük}}
# *{{uk}}: {{Üt|uk|слово|slovo}} {{n}}
# *{{hu}}: {{Ü|hu|szó}}
# *{{ur}}: {{Üt|ur|لفظ|}} {{m}}
# *{{vo}}: {{Ü|vo|vöd}}
# *{{cy}}: {{Ü|cy|gair}} {{m}}
# *{{wa}}: {{Ü|wa|mot}} {{m}}
# *{{be}}: {{Üt|be|слово|slovo}} {{n}}
# *{{fy}}: {{Ü|fy|wurd}} {{n}}
# |Dialekttabelle=
# *Bairisch: [?] Wort, ''pl.'' Wörta
# *Elsässisch: [?] Wort, ''pl.'' Werter
# *Kölsch: [?] Woot, ''pl.'' Wöder u. Woot
# *Schwäbisch: [?] Wörtle
# **Ostschwäbisch: [?] (z')Wort, ''Pl.'' (d')Wéérda(r), (z')Wéérdle, ''Pl.'' (d')Wéérdla
# *{{wym}}: [1] {{Ü|wym|wiüt}} {{n}}
# }}
# {{Ü-Tabelle|2|G=eine endliche Folge von Symbolen aus einem Alphabet|Ü-Liste=
# *{{bs}}: {{Üt|bs|ријеч|riječ}} {{f}}
# *{{fr}}: {{Ü|fr|mot}} {{m}}, {{Ü|fr|parole}} {{f}}
# *{{mk}}: {{Üt|mk|збор|zbor}} {{m}}, {{Üt|mk|реч|reč}} {{f}}
# *{{pt}}: {{Ü|pt|palavra}} {{f}}
# *{{ro}}: {{Ü|ro|expresie}} {{f}}
# *{{sv}}: {{Ü|sv|ord}} {{n}}
# *{{sr}}: {{Üt|sr|реч|reč}} {{f}}, {{va.|:}} {{Üt|sr|збор|zbor}} {{m}}
# *{{sh}}: {{Üt|sh|реч|reč}} {{f}}, {{Üt|sh|ријеч|riječ}} {{f}}
# *{{sk}}: {{Ü|sk|slovo}} {{n}}
# *{{cs}}: {{Ü|cs|slovo}} {{n}}
# |Dialekttabelle=
# *Bairisch: [?] Wort, ''pl.'' Wörta
# *Elsässisch: [?] Wort, ''pl.'' Werter
# *Kölsch: [?] Woot, ''pl.'' Wöder u. Woot
# *Schwäbisch: [?] Wörtle
# **Ostschwäbisch: [?] (z')Wort, ''Pl.'' (d')Wéérda(r), (z')Wéérdle, ''Pl.'' (d')Wéérdla
# *{{wym}}: [1] {{Ü|wym|wiüt}} {{n}}
# }}
# {{Ü-Tabelle|3|G=als Einheit betrachtete Kette nebeneinanderliegender Bits / Bytes in definierter Länge|Ü-Liste=
# *{{bs}}: {{Üt|bs|ријечи|riječi}} ''Pl.''
# *{{bg}}: {{Üt|bg|слово|slovo}} {{n}}
# *{{mk}}: {{Üt|sr|зборови|zborovi}} ''Pl.''
# *{{ro}}: {{Ü|ro|expresie}} {{f}}
# *{{sr}}: {{Üt|sr|речи|reči}} ''Pl.''
# *{{sh}}: {{Üt|sh|речи|reči}} ''Pl.'', {{Üt|sh|ријечи|riječi}} ''Pl.''
# *{{sk}}: {{Ü|sk|slovo}} {{n}}
# *{{cs}}: {{Ü|cs|slovo}} {{n}}
# |Dialekttabelle=
# *Bairisch: [?] Wort, ''pl.'' Wörta
# *Elsässisch: [?] Wort, ''pl.'' Werter
# *Kölsch: [?] Woot, ''pl.'' Wöder u. Woot
# *Schwäbisch: [?] Wörtle
# **Ostschwäbisch: [?] (z')Wort, ''Pl.'' (d')Wéérda(r), (z')Wéérdle, ''Pl.'' (d')Wéérdla
# *{{wym}}: [1] {{Ü|wym|wiüt}} {{n}}
# }}
#
# {{Referenzen}}
# :[1] {{Wikipedia|Wort}}
# :[2] {{Wikipedia|Wort (Theoretische Informatik)}}
# :[3] {{Wikipedia|Datenwort}}
# :[1] {{Ref-Grimm|Wort}}
# :[1] {{Ref-DWDS|Wort}}
# :[1] {{Ref-Duden|Wort}}
# :[*] {{Ref-UniLeipzig|Wort}}
#
# {{Quellen}}
#
# === {{Wortart|Substantiv|Deutsch}}, {{n}}, Worte ===
#
# {{Deutsch Substantiv Übersicht
# |Genus=n
# |Nominativ Singular=Wort
# |Nominativ Plural=Worte
# |Genitiv Singular=Worts
# |Genitiv Singular*=Wortes
# |Genitiv Plural=Worte
# |Dativ Singular=Wort
# |Dativ Singular*=Worte
# |Dativ Plural=Worten
# |Akkusativ Singular=Wort
# |Akkusativ Plural=Worte
# }}
#
# {{Worttrennung}}
# :Wort, {{Pl.}} Wor·te
#
# {{Aussprache}}
# :{{IPA}} {{Lautschrift|vɔʁt}}
# :{{Hörbeispiele}} {{Audio|De-Wort.ogg}}, {{Audio|De-Wort2.ogg}}
# :{{Reime}} {{Reim|ɔʁt|Deutsch}}
#
# {{Bedeutungen}}
# :[1] eine (aus Wörtern [[bilden|gebildete]]) [[sinnvoll]]e [[Aussage]]: [[Zitat]], [[Sinnspruch]], [[Aussage]], [[Ausspruch]], [[Aphorismus]], [[Aperçu]]
# :[2] [[Wortlaut]], [[Liedtext]]
# :[3] {{K|kein Plural}} [[Versprechen]], [[Beteuerung]]
# :[4] {{K|Religion}} [[wirkungsmächtig]]e [[Äußerung]]; [[Offenbarung]] [[Gott]]es, [[Heilige Schrift]]; ''im [[Christentum]]'' auch: [[Messias]]
# :[5] [[Ausführung]], [[Rede]]
#
# {{Herkunft}}
# :wie [[#Substantiv,_n,_Wörter|Wort / Wörter]]
#
# {{Synonyme}}
# :[1, 2, 4] [[Losung]]
# :[1–4] [[Spruch]]
# :[1, 4] [[Begriff]]
#
# {{Unterbegriffe}}
# :[1] [[Sprichwort]]
# :[3] [[Ehrenwort]], [[Jawort]]
# :[4] [[Bannwort]], [[Bibelwort]], [[Gotteswort]], [[Losungswort]], [[Zauberwort]]
# :[5] [[Abschiedswort]], [[Antwort]], [[Begrüßungswort]], [[Dankeswort]], [[Geleitwort]], [[Grußwort]], [[Huldigungswort]], [[Liebeswort]], [[Machtwort]], [[Mahnwort]], [[Nachwort]], [[Schlusswort]], [[Trostwort]], [[Vorwort]], [[Widerwort]]
#
# {{Beispiele}}
# :[1] Das war ein „Geflügeltes ''Wort''“.
# :[2] In ''Wort'' und Musik zu Gehör bringen.
# :[2] ''Wort'' für ''Wort''
# :[2] „… stapel tausend wirre ''Worte'' auf, die dich am Ärmel ziehen …“ (Liedtext von „Wir sind Helden“, Nur ein Wort)
# :[2] Die richtigen ''Worte'' finden (um auszudrücken, was man sagen will).
# :[3] Auf dein ''Wort'' will ich's wagen.
# :[4] „Im Anfang war das ''Wort,'' und das ''Wort'' war bei Gott, und Gott war das ''Wort.''“<ref>Bibel: Johannesevangelium 1, 1</ref>
# :[5] Ich werde Dir gleich das ''Wort'' erteilen.
# :[5] Das ist mein letztes ''Wort!''
# :[5] Das ''Wort'' ergreifen.
# :[5] Spar dir deine ''Worte!''
# :[5] Mir fehlen die ''Worte.''
#
# {{Redewendungen}}
# :[3] Genug der ''Worte!'' (Genug geredet, jetzt müssen Taten folgen)
# :[3] jemandem sein ''Wort'' geben
# :[4] ''Wort'' Gottes (''verbum'' Dei)
# :[4] [[das Wort zum Sonntag]]
# :[5] das ''Wort'' erteilen, geben, übergeben
# :[5] „Der ''Worte'' sind genug gewechselt,/ Lasst mich auch endlich Taten sehn!“<ref>{{Lit-Goethe: Faust|V=Beck}}, Vers 214</ref>
# :[5] einer Sache das ''Wort'' reden (gehoben)
#
# {{Sprichwörter}}
# :[1] [[ein Bild sagt mehr als tausend Worte|ein Bild sagt mehr als tausend ''Worte'']]
#
# {{Charakteristische Wortkombinationen}}
# :[1] ''mit [[Adjektiv]]:'' [[geflügelt]]e ''Worte'' ({{Audio|De-geflügelte Worte.ogg|Audio}})
#
# {{Wortbildungen}}
# :[1] [[Wortführer]], [[Wortkunst]], [[Wortspiel]], [[Wortwitz]]
# :[3] [[Wortbruch]]
# :[5] [[Wortmeldung]]
#
# ==== {{Übersetzungen}} ====
# {{Ü-Tabelle|1|G=eine (aus Wörtern gebildete) sinnvolle Aussage|Ü-Liste=
# *{{bg}}: {{Üt|bg|дума|}}
# *{{en}}: {{Ü|en|saying}}
# *{{ka}}: {{Üt|ka|სიტყვა|sit'q'va}}
# *{{el}}: {{Üt|el|λόγος|lógos}} {{m}}, {{Üt|el|λόγια|lója}} {{n}} nur Plural, {{Üt|el|κουβέντα|kouvénda}} {{f}}
# *{{mk}}: {{Üt|mk|реч|reč}} {{f}}
# *{{pt}}: {{Ü|pt|palavra}} {{f}}, {{Ü|pt|dizer}} {{m}}
# *{{ro}}: {{Ü|ro|cuvânt}} {{n}}
# *{{ru}}: {{Üt|ru|слово}} {{n}}, {{Üt|ru|речь}} {{f}}
# *{{sr}}: {{Üt|sr|реч|reč}} {{f}}
# *{{cs}}: {{Ü|cs|slovo}} {{n}}
# *{{tr}}: {{Ü|tr|söz}}
# *{{uk}}: {{Üt|uk|слово|slovo}} {{n}}
# *{{hu}}: {{Ü|hu|szó}}
# *{{vo}}: {{Ü|vo|vöd}}
# *{{cy}}: {{Ü|cy|gair}} {{m}}
# *{{wa}}: {{Ü|wa|mot}} {{m}}
# *{{be}}: {{Üt|be|слова|slova}} {{n}}
# }}
# {{Ü-Tabelle|2|G=Wortlaut, Liedtext|Ü-Liste=
# *{{ka}}: {{Üt|ka|სიტყვა|sit'q'va}}
# *{{el}}: {{Üt|el|λόγος|lógos}} {{m}}, {{Üt|el|λόγια|lója}} {{n}} nur Plural, {{Üt|el|κουβέντα|kouvénda}} {{f}}
# *{{mk}}: {{Üt|mk|реч|reč}} {{f}}
# *{{sr}}: {{Üt|sr|реч|reč}} {{f}}
# *{{cs}}: {{Ü|cs|slovo}} {{n}}
# }}
# {{Ü-Tabelle|3|G=Versprechen, Beteuerung|Ü-Liste=
# *{{ka}}: {{Üt|ka|სიტყვა|sit'q'va}}
# *{{el}}: {{Üt|el|λόγος|lógos}} {{m}}, {{Üt|el|λόγια|lója}} {{n}} nur Plural, {{Üt|el|κουβέντα|kouvénda}} {{f}}
# *{{ru}}: {{Üt|ru|слово}} {{n}}, {{Üt|ru|обещание}} {{n}}
# *{{sr}}: {{Üt|sr|реч|reč}} {{f}}
# *{{cs}}: {{Ü|cs|slovo}} {{n}}
# }}
# {{Ü-Tabelle|4|G=Religion: wirkungsmächtige Äußerung; Offenbarung Gottes|Ü-Liste=
# *{{ka}}: {{Üt|ka|სიტყვა|sit'q'va}}
# *{{el}}: {{Üt|el|λόγος|lógos}} {{m}}, {{Üt|el|λόγια|lója}} {{n}} nur Plural, {{Üt|el|κουβέντα|kouvénda}} {{f}}
# *{{sr}}: {{Üt|sr|реч|reč}} {{f}}
# *{{cs}}: {{Ü|cs|slovo}} {{n}}
# }}
# {{Ü-Tabelle|5|G=Ausführung, Rede|Ü-Liste=
# *{{ka}}: {{Üt|ka|სიტყვა|sit'q'va}}
# *{{el}}: {{Üt|el|λόγος|lógos}} {{m}}, {{Üt|el|λόγια|lója}} {{n}} nur Plural, {{Üt|el|κουβέντα|kouvénda}} {{f}}
# *{{sr}}: {{Üt|sr|реч|reč}} {{f}}
# *{{cs}}: {{Ü|cs|slovo}} {{n}}
# }}
#
# {{Referenzen}}
# :[1–5] {{Ref-Grimm}}
# :[1, 3, 5] {{Ref-DWDS}}
# :[1–5] {{Ref-Duden}}
# :[3, 5] {{Ref-UniLeipzig}}
#
# {{Quellen}}
#
# {{Ähnlichkeiten 1|[[dort]], [[Fort]], [[fort]], [[Hort]], [[Ort]], [[Port]], [[Tort]], [[ward]], [[Wart]], [[wart]], [[Wert]], [[wert]], [[Wirt]], [[wird]], [[Wurt]]}}


# {{Siehe auch|[[Tun]], [[Tun.]], [[tun.]]}}
# == tun ({{Sprache|Deutsch}}) ==
# === {{Wortart|Verb|Deutsch}} ===
#
# {{Deutsch Verb Übersicht
# |Präsens_ich=tue
# |Präsens_ich*=tu
# |Präsens_du=tust
# |Präsens_er, sie, es=tut
# |Präteritum_ich=tat
# |Partizip II=getan
# |Konjunktiv II_ich=täte
# |Imperativ Singular=tue
# |Imperativ Singular*=tu
# |Imperativ Plural=tut
# |Hilfsverb=haben
# }}
#
# {{Nicht mehr gültige Schreibweisen}}
# :[[thun]]
#
# {{Worttrennung}}
# :tun, {{Prät.}} tat, {{Part.}} ge·tan
#
# {{Aussprache}}
# :{{IPA}} {{Lautschrift|tuːn}}
# :{{Hörbeispiele}} {{Audio|De-tun.ogg}}, {{Audio|De-tun2.ogg}}
# :{{Reime}} {{Reim|uːn|Deutsch}}
#
# {{Bedeutungen}}
# *{{trans.}}
# :[1] eine [[Handlung]] ausführen
# ::[a] die zuvor im [[Kontext]] näher [[beschreiben|beschriebene]]
# ::[b] die dem [[vorangehend]]en [[Nomen]] [[entsprechen]]de
# ::[c] dazu [[führen]], dass sich etwas [[ereignen|ereignet]], [[zustande]] kommt
# :[2] ''meist {{ugs.|,}} mit [[Präposition]]:'' etwas in eine bestimmte [[Position]] [[bringen]]
# :[3] {{Dativ|:}} jemanden in einer [a] [[gut]]en oder [b] [[schlecht]]en [[Weise]] [[behandeln]]
#
# *''[[es]] tun''
# :[4] {{ugs.|:}} für den [[vorsehen|vorgesehenen]] [[Zweck]] [[ausreichen]]
# :[5] {{ugs.|,}} ''von [[Gegenstand|Gegenständen]]:'' seine [[Funktion]] [[erfüllen]], vorschriftsmäßig [[arbeiten]]
# :[6] {{ugs.|,}} [[verhüllend]]: (den ersten) [[Geschlechtsverkehr]] haben
#
# *{{intrans.}}
# :[7] ''mit [[nachfolgend]]em [a] [[Adjektiv]] oder [b] [[Verb]] im [[Konjunktiv]]; meist [[abwertend]]:'' eine [[Eigenschaft]] beziehungsweise einen [[Sachverhalt]] anders [[darstellen]], als er [[wirklich]] ist
# :[8] {{ugs.|,}} ''[[landschaftlich]], von Gegenständen:'' seine Funktion erfüllen, vorschriftsmäßig arbeiten
#
# *{{refl.}}
# :[9] {{ugs.|,}} es tut sich etwas/einiges/nichts: es gehen [[entscheidend]]e, [[erwartet]]e [[Änderung]]en vor
#
# {{Herkunft}}
# :[[mittelhochdeutsch]] und [[althochdeutsch]] ''tuon'', seit dem 8.&nbsp;Jahrhundert belegt, über westgermanisch ''*dō-'' von ''*dhē-'' "[[stellen]], [[setzen]], [[legen]]"<ref>{{Ref-DWDS|tun}}</ref>
#
# {{Synonyme}}
# :[1] [[machen]]
# :[1c] [[bringen]]
# :[2] [[platzieren]]
# :[3] [[antun]]
# :[4] [[ausreichen]], [[genügen]], [[langen]]
# :[5] [[funktionieren]], [[gehen]]
# :[6] es [[machen]]; ''siehe auch:'' [[Verzeichnis:Deutsch/Geschlechtsverkehr]]
# :[7a] [[vortäuschen]], … zu sein
# :[7b] [[vortäuschen]], zu …
# :[8] [[funktionieren]], [[gehen]]
# :[9] sich [[ereignen]], [[geschehen]], [[passieren]], [[vorgehen]]
#
# {{Gegenwörter}}
# :[1] [[lassen]], [[sein lassen]]/[[seinlassen]], [[unterlassen]]
# :[2] (stehen) [[lassen]]
# :[7a] [[sein]]
#
# {{Unterbegriffe}}
# :[1] [[treiben]]
# :[1] [[unternehmen]]
# :[2] [[legen]], [[setzen]], [[stellen]], ''regional:'' [[machen]]
# :[3b] [[verletzen]], [[wehtun]]
#
# {{Beispiele}}
# :[1] Was ''tust'' du?
# :[1] Was ihr sagt oder ''tut,'' ist mir egal.
# :[1] Ich würde alles dafür ''tun.''
# :[1] All dies ''tat'' ich für Euch!
# :[1a] Die räumen hier gerade auf, ''tue'' du das nachher bitte auch.
# :[1b] Wir haben all unsere Arbeiten ''getan.''
# :[1c] Deine Hilfen ''tun'' Wunder.
# :[2] ''Tu’s'' wieder dahin zurück, wo es vorher war!
# :[2] Wir ''tun'' das Geld in einen Sparstrumpf.
# :[3a] Ich ''tu'' dir einen Gefallen…
# :[3b] ''Tu'' mir nichts.
# :[3b] Sei vorsichtig, sonst ''tust'' du dir noch was.
# :[4] Die alte Jacke ''tut es'' für die Gartenarbeit.
# :[5] Unser Computer ''tut’s'' nicht mehr.
# :[6] Wir haben ''es'' noch nicht miteinander ''getan.''
# :[7a] ''Tu'' nicht so blöd!
# :[7b] Ich ''tu,'' als sei ich taub.
# :[8] Das Teil ''tut'' nicht mehr gescheit, ich will ein Neues.
# :[9] In den letzten Jahren ''hat sich'' hier einiges ''getan.''
#
# {{Redewendungen}}
# :[1] [[es zu tun haben|es zu ''tun'' haben]]
# :[1] [[es zu tun bekommen|es zu ''tun'' bekommen]]/[[es zu tun kriegen|kriegen]]
# :[1] [[mit etwas ist es getan|mit etwas ist es ''getan'']]/[[mit etwas ist es nicht getan|nicht ''getan'']]
# :[1] [[gesagt, getan|gesagt, ''getan'']]
# :[1] um jemanden/etwas ''[[getan]]'' sein
# :[1c] [[nichts zur Sache tun|nichts zur Sache ''tun'']]
# :[7] [[so tun, als ob|so ''tun'', als ob]]; [[tun, als ob|''tun'', als ob]]; [[nur so tun|nur so ''tun'']]
#
# {{Charakteristische Wortkombinationen}}
# :[1] (viel) zu ''tun'' haben
# :[7b] (nur) so tun; (so) tun, als ob/wenn…; (so) tun, als…
#
# {{Wortbildungen}}
# :*[[abtun]], [[antun]], [[auftun]], [[austun]], [[betun]], [[dartun]], [[dazutun]], [[dicktun]]/[[dicketun]], [[geheimtun]], [[genugtun]], [[gleichtun]], [[großtun]], [[guttun]], [[harttun]], [[heimlichtun]], [[heimtun]], [[heraustun]], [[herumtun]], [[hervortun]], [[hinauftun]], [[hinaustun]], [[hineintun]], [[hintun]], [[hinübertun]], [[hinzutun]], [[kundtun]], [[leichttun]], [[leidtun]], [[mittun]], [[nachtun]], [[nottun]], [[schöntun]], [[schwertun]], [[übeltun]], [[übertun]], [[umtun]], sich [[vertun]], [[wegtun]], [[wehtun]], [[wichtigtun]], [[wiedertun]], [[wohltun]], [[zugutetun]], [[zurücktun]], [[zusammentun]], [[zutun]], [[zuvortun]]
# :*[[Getue]], [[Tat]], [[Tun]], -tuer (→[[Tuerei]]), [[Tuwort]], [[untertan]]
#
# ==== {{Übersetzungen}} ====
# {{Ü-Tabelle|Ü-Liste=
# *{{ar}}: [1] {{Üxx5|ar|faʕala|فَعَلَ|فعل}}
# *{{eu}}: [1] {{Ü|eu|egin}}
# *{{en}}: [1, 3, 4, 6] {{Ü|en|do}}; [2] {{Ü|en|put}}; [5, 8] {{Ü|en|work}}; [7] {{Ü|en|act}}; [9] {{Ü|en|happen}}
# *{{eo}}: [1] {{Ü|eo|fari}}
# *{{fi}}: [1] {{Ü|fi|tehdä}}
# *{{fr}}: [1, 3, 6, 7] {{Ü|fr|faire}}; [2] {{Ü|fr|mettre}}; [4] {{Ü|fr|convenir}}; [5, 8] {{Ü|fr|fonctionner}}; [7] {{Ü|fr|faire semblant}}; [9] {{Ü|fr|arriver}}
# *{{gl}}: [2] {{Ü|gl|poñer}}
# *{{el}}: [1, 3] {{Üt|el|κάνω|káno}}; [2] {{Üt|el|βάζω|vázo}}
# *{{gu}}: [1] {{Üt|gu|કરવું|}}
# *{{ia}}: [1] {{Ü|ia|facer}}
# *{{it}}: [1, 3, 6, 7] {{Ü|it|fare}}; [2] {{Ü|it|mettere}}; [4, 5, 8] {{Ü|it|andare}}, {{Ü|it|funzionare}}; [7] {{Ü|it|atteggiarsi}}, {{Ü|it|fingere}}; [9] {{Ü|it|succedere}}, {{Ü|it|accadere}}
# *{{ja}}: [1] {{Üt|ja|する|suru}}, {{Üt|ja|成す|なす, nasu}}
# *{{ca}}: [1] {{Ü|ca|fer}}
# *{{ku}}:
# **{{kmr}}: [1] {{Ü|kmr|kirin}}
# *{{mr}}: [1] {{Üt|mr|करणे|}}
# *{{nds}}: [1–3, 7] {{Ü|nds|doon}} (Norddeutschland, Münsterland), {{Ü|nds|daun}} (ehem. Vest Recklinghausen); [1, 6] {{Ü|nds|maken}}; [4] {{Ü|nds|langen}}; [6] {{Ü|nds|drieven}}
# *{{no}}: [1] {{Ü|no|gjøre}}
# *{{oc}}: [1] {{Ü|oc|far}}, {{Ü|oc|faire}}
# *{{pl}}: [1] {{Ü|pl|czynić}}
# *{{pt}}: [1] {{Ü|pt|fazer}}; [2] {{Ü|pt|pôr}}; [4] {{Ü|pt|bastar}}; [6] {{Ü|pt|transar}}; [7] {{Ü|pt|fingir}}
# *{{ro}}: [1] {{Ü|ro|face}}
# *{{ru}}: [1] {{Üt|ru|делать}}; [2] {{Üt|ru|класть}}, {{Üt|ru|положить}}, {{Üt|ru|ставить}}, {{Üt|ru|поставить}}; [7] {{Üt|ru|притворяться}}
# *{{sv}}: [1] {{Ü|sv|göra}}
# *{{wen}}:
# **{{hsb}}: [1] {{Ü|hsb|činić}}
# *{{es}}: [1] {{Ü|es|hacer}}; [2] {{Ü|es|poner}}
# *{{sw}}: [1] {{Ü|sw|kufanya}}
# *{{th}}: [1] {{Üt|th|ทำ|tham}}
# *{{cs}}: [1] {{Ü|cs|dělat}}, {{Ü|cs|konat}}, {{Ü|cs|činit}}
# *{{tr}}: [1] {{Ü|tr|yapmak}}
# *{{ur}}: [1] {{Üt|ur|کرنا|}}
# *{{pnb}}: [1] {{Ü|pnb|کرنا}}
# |Dialekttabelle=
# *Alemannisch: [1–6] due/tuä
# *Bairisch: doa
# *Kölsch: dunn
# *Schwäbisch: dua, doa
# }}
#
# {{Referenzen}}
# :[1–7, 9] {{Ref-FreeDictionary|tun}}
# :[1–3, 7, 9] {{Ref-DWDS|tun}}
# :[1–9] {{Ref-Duden|tun_handeln_erledigen|tun (handeln, erledigen)}}
# :[1–9] {{Lit-Duden: Universalwörterbuch|A=6}}, „<sup>1</sup>tun“, Seite 1718-1719
# :[1, 2] {{Ref-Grimm|tun}}
# :[1–2, 7] Institut für Deutsche Sprache: ''Wörterbuch zur Verbvalenz'' [https://grammis.ids-mannheim.de/verbvalenz/400246 "tun"]
# :[*] {{Ref-UniLeipzig|tun}}
#
# {{Quellen}}
#
# === {{Wortart|Hilfsverb|Deutsch}} ===
#
# {{Deutsch Verb Übersicht
# |Präsens_ich=tu
# |Präsens_ich*=tue
# |Präsens_du=tust
# |Präsens_er, sie, es=tut
# |Präteritum_ich=tat
# |Partizip II=getan
# |Konjunktiv II_ich=täte
# |Imperativ Singular=tu
# |Imperativ Singular*=tue
# |Imperativ Plural=tut
# |Hilfsverb=haben
# }}
#
# {{Worttrennung}}
# :tun, {{Prät.}} tat, {{Part.}} ge·tan
#
# {{Aussprache}}
# :{{IPA}} {{Lautschrift|tuːn}}
# :{{Hörbeispiele}} {{Audio|}}
# :{{Reime}} {{Reim|uːn|Deutsch}}
#
# {{Bedeutungen}}
# :[1] ''meist {{ugs.|:}} zur [[Betonung]] des [[Vollverb]]s oder um die [[Konjugation]] desselben zu [[vermeiden]] verwendet''
# ::[a] ''[[nachgestellt]]''
# ::[b] ''[[vorangestellt]]''
# :[2] ''[[landschaftlich]]: [[ersetzen|ersetzt]] den [[Konjunktiv]]''
#
# {{Herkunft}}
# :siehe [[tun#Verb|oben]]
#
# {{Synonyme}}
# :[2] [[werden]]
#
# {{Beispiele}}
# :[1a] Lesen ''tu'' ich auch noch ziemlich gerne.
# :[1b] ''Tut'' er noch schlafen? ''(schläft er noch?)''
# :[2] Wenn du mir doch nur ein bisschen helfen ''tätest… (helfen würdest; hälfest)''
#
# ==== {{Übersetzungen}} ====
# {{Ü-Tabelle|Ü-Liste=
# *{{en}}: [1] {{Ü|en|}}
# *{{fr}}: [1] {{Ü|fr|}}
# }}
#
# {{Referenzen}}
# :[1, 2] {{Lit-Duden: Universalwörterbuch|A=6}}, „<sup>2</sup>tun“, Seite 1719
# :[1a] {{Ref-DWDS|tun}}
# :[1a, 2] {{Ref-FreeDictionary|tun}}
# :[1, 2] {{Ref-Duden|tun_werden|tun (werden)}}
#
# === {{Wortart|Konjugierte Form|Deutsch}} ===
#
# {{Nebenformen}}
# :[[tune]]
#
# {{Worttrennung}}
# :tun
#
# {{Aussprache}}
# :{{IPA}} {{Lautschrift|tjuːn}}
# :{{Hörbeispiele}} {{Audio|}}
# :{{Reime}} {{Reim|uːn|Deutsch}}
#
# {{Grammatische Merkmale}}
# *2. Person Singular Imperativ Präsens Aktiv des Verbs '''[[tunen]]'''
#
# {{Grundformverweis Konj|tunen}}
#
# {{Ähnlichkeiten 1|Anagramme=[[nut]], [[Nut]]}}
#
# == tun ({{Sprache|Ido}}) ==
# === {{Wortart|Personalpronomen|Ido}} ===
# {{Worttrennung}}
# :tun
#
# {{Aussprache}}
# :{{IPA}} {{Lautschrift|tun}}
# :{{Hörbeispiele}} {{Audio|}}
#
# {{Bedeutungen}}
# :[1] [[voranstellen|Vorangestelltes]] Personalpronomen der 2. Person Singular [[Akkusativ]] ‚[[dich]]‘, zum [[hervorheben|Hervorheben]], oder [[vermeiden|Vermeiden]] von [[Verwechslung]]en
#
# {{Herkunft}}
# :[[tu#tu_(Ido)|tu]] mit Akkusativendung -n<ref>{{Literatur | Autor=Ferdinand Weber | Herausgeber=Deutscher Ido-Bund  (Germana Ido-Federuro) E. V. | Titel=Ido por omni. Lehrbuch der Weltsprache | Auflage=Dritte, erweiterte | Verlag=Englert und Schlosser | Ort=Frankfurt am Main | Jahr=1924 | Kapitel=3. Lektion. Deklination der Hauptwörter (deklino dil substantivi) | Seiten=11 | DNB=578242699 | Online=[http://www.idolinguo.de/IdoPorOmni1924/ Online] | Zugriff=2020-11-06}}</ref>
#
# {{Lemmaverweis|tu#tu_(Ido)|tu}}
# {{Quellen}}
#
# == tun ({{Sprache|Tschechisch}}) ==
# === {{Wortart|Deklinierte Form|Tschechisch}} ===
#
# {{Worttrennung}}
# :tun
#
# {{Aussprache}}
# :{{IPA}} {{Lautschrift|tʊn}}
# :{{Hörbeispiele}} {{Audio|}}
# :{{Reime}} {{Reim|ʊn|Tschechisch}}
#
# {{Grammatische Merkmale}}
# *Genitiv Plural des Substantivs '''[[tuna]]'''
#
# {{Grundformverweis Dekl|tuna|spr=cs}}


# {{Siehe auch|[[Ehrlich]]}}
# == ehrlich ({{Sprache|Deutsch}}) ==
# === {{Wortart|Adjektiv|Deutsch}} ===
#
# {{Deutsch Adjektiv Übersicht
# |Positiv=ehrlich
# |Komparativ=ehrlicher
# |Superlativ=ehrlichsten
# }}
#
# {{Worttrennung}}
# :ehr·lich, {{Komp.}} ehr·li·cher, {{Sup.}} am ehr·lichs·ten
#
# {{Aussprache}}
# :{{IPA}} {{Lautschrift|ˈeːɐ̯lɪç}}
# :{{Hörbeispiele}} {{Audio|De-ehrlich.ogg}}, {{Audio|De-at-ehrlich.ogg|spr=at}}
# :{{Reime}} {{Reim|eːɐ̯lɪç|Deutsch}}
#
# {{Bedeutungen}}
# :[1] der [[Wahrheit]] und [[Wirklichkeit]] entsprechend, nicht [[lügen|gelogen]] oder [[täuschen|vorgetäuscht]]; [[wahr]]
# :[2] ''Charaktereigenschaft:'' [[anständig]] und [[fair]], nie lügend; [[redlich]]
#
# {{Herkunft}}
# :um das Jahr 800, [[althochdeutsch]] ''ērlīh'', [[mittelhochdeutsch]] ''ērlich'' „[[ehrenvoll]], [[ruhmreich]], [[ansehnlich]], [[vornehm]]“<ref>{{Ref-DWDS|ehrlich}}</ref>
#
# {{Synonyme}}
# :[1] [[ungelogen]], [[wirklich]], [[wahr]], [[wahrhaftig]], [[wahrheitsgemäß]]
# :[2] [[anständig]], [[aufrichtig]], [[brav]], [[fair]], [[rechtschaffen]], [[redlich]]
#
# {{Gegenwörter}}
# :[1] [[gelogen]], [[unehrlich]], [[unwirklich]]
# :[1] [[falsch]], [[unanständig]], [[unaufrichtig]], [[unfair]], [[unredlich]]
#
# {{Beispiele}}
# :[1] „Ich bin in dich verliebt.“ - „''Ehrlich''?“
# :[1] Es lag ''ehrliche'' Trauer in ihrer Stimme.
# :[1] „Findest du mich schön? Sei ''ehrlich''!“
# :[2] „Ihm kannst du vertrauen, er ist ein ''ehrlicher'' Mann.“
# :[2] Simone ist eine ''ehrliche'' Seele.
#
# {{Redewendungen}}
# :[2] [[ehrlich währt am längsten|''ehrlich'' währt am längsten]]
#
# {{Charakteristische Wortkombinationen}}
# :[1] [[offen]] und ''ehrlich'' sein
#
# {{Wortbildungen}}
# :[[Ehrlichkeit]]
#
# ==== {{Übersetzungen}} ====
# {{Ü-Tabelle|1|G=der Wahrheit und Wirklichkeit entsprechend, nicht gelogen oder vorgetäuscht; wahr|Ü-Liste=
# *{{en}}: {{Ü|en|real}}, {{Ü|en|really}}
# *{{et}}: {{Ü|et|aus}}
# *{{fi}}: {{Ü|fi|rehellinen}}
# *{{fr}}: {{Ü|fr|honnête}} {{mf}}, {{Ü|fr|honnêtement}}, {{Ü|fr|sincère}} {{mf}}, {{Ü|fr|sincèrement}}, {{Ü|fr|à vrai dire}}, {{Ü|fr|franchement}}
# *{{el}}: {{Üt|el|ειλικρινής|ilikrinís}}
# *{{ia}}: {{Ü|ia|honeste}}
# *{{it}}: {{Ü|it|vero}}
# *{{ja}}: {{Üt|ja|正直|しょうじき, shôjiki}}, {{Üt|ja|忠実|ちゅうじつ, chûjitsu}}, {{Üt|ja|活発|かっぱつ, kappatsu}}
# *{{ko}}: {{Üt|ko|진실된|}}
# *{{mk}}: {{Üt|mk|поштен|pošten}}, {{Üt|mk|честит|čestit}}
# *{{no}}: {{Ü|no|ærlig}}
# *{{pl}}: {{Ü|pl|szczery}}
# *{{pt}}: {{Ü|pt|verdadeiro}}
# *{{ru}}: {{Üt|ru|честный}}
# *{{sv}}: {{Ü|sv|uppriktig}}, {{Ü|sv|ärlig}}
# *{{sr}}: {{Üt|sr|искрен|iskren}}
# *{{sh}}: {{Üt|sh|искрен|iskren}}
# *{{sl}}: {{Ü|sl|iskren}}
# *{{es}}: {{Ü|es|veraz}}, {{Ü|es|verdadero}}, {{Ü|es|fiel}}
# *{{cs}}: {{Ü|cs|poctivý}}
# *{{hu}}: {{Ü|hu|őszinte}}
# }}
#
# {{Ü-Tabelle|2|G=Charaktereigenschaft: anständig und fair, nie lügend; redlich|Ü-Liste=
# *{{en}}: {{Ü|en|honest}}
# *{{et}}: {{Ü|et|aus}}
# *{{fi}}: {{Ü|fi|rehellinen}}
# *{{fr}}: {{Ü|fr|droit}}, {{Ü|fr|probe}} {{m}} {{f}}, {{Ü|fr|honnête}} {{m}} {{f}}
# *{{el}}: {{Üt|el|τίμιος|tímios}}
# *{{it}}: {{Ü|it|onesto}}, {{Ü|it|probo}}
# *{{tlh}}: {{Ü|tlh|yuDHa’}}
# *{{pt}}: {{Ü|pt|honesto}}
# *{{ru}}: {{Üt|ru|честный}}
# *{{sv}}: {{Ü|sv|ärlig}}, {{Ü|sv|hederlig}}
# *{{sr}}: {{Üt|sr|поштен|pošten}}, {{Üt|sr|честит|čestit}}
# *{{sh}}: {{Üt|sh|поштен|pošten}}, {{Üt|sh|честит|čestit}}
# *{{sl}}: {{Ü|sl|pošten}}
# *{{es}}: {{Ü|es|honesto}}, {{Ü|es|probo}}, {{Ü|es|fiel}}
# *{{cs}}: {{Ü|cs|poctivý}}, {{Ü|cs|upřímný}}
# *{{hu}}: {{Ü|hu|őszinte}}
# }}
#
# {{Referenzen}}
# :[1] {{Ref-Grimm|ehrlich}}
# :[1, 2] {{Ref-DWDS|ehrlich}}
# :[*] {{Ref-UniLeipzig|ehrlich}}
#
# {{Quellen}}
#
# {{Ähnlichkeiten 1|[[erbärmlich]]|Anagramme=[[Herlich]]}}


# == genommen ({{Sprache|Deutsch}}) ==
# === {{Wortart|Partizip II|Deutsch}} ===
#
# {{Worttrennung}}
# :ge·nom·men
#
# {{Aussprache}}
# :{{IPA}} {{Lautschrift|ɡəˈnɔmən}}
# :{{Hörbeispiele}} {{Audio|De-genommen.ogg}}, {{Audio|De-at-genommen.ogg|spr=at}}
# :{{Reime}} {{Reim|ɔmən|Deutsch}}
#
# {{Grammatische Merkmale}}
# * Partizip Perfekt des Verbs '''[[nehmen]]'''
#
# {{Grundformverweis Konj|nehmen}}


def add_my_buttons(buttons, editor):
    buttons.append(editor.addButton(
        icon=None,
        cmd="myButton",
        func=lambda s=editor: fill_german_word_fields(s),
        label="Fill German word fields from Wiktionary"
    ))

    buttons.append(editor.addButton(
        icon=None,
        cmd="googleTranslate",
        func=lambda s=editor: fill_card_with_chatgpt(s, "gpt-3.5-turbo"),
        label="ChatGPT examples",
    ))

    buttons.append(editor.addButton(
        icon=None,
        cmd="googleTranslate",
        func=lambda s=editor: fill_card_with_chatgpt(s, "gpt-4o"),
        label="GPT-4 examples",
    ))

    buttons.append(editor.addButton(
        icon=None,
        cmd="wiktionary",
        func=lambda s=editor: webbrowser.open("https://de.wiktionary.org/wiki/" + urllib.parse.quote(s.note['Word'])),
        label="Wiktionary",
    ))

    buttons.append(editor.addButton(
        icon=None,
        cmd="dwds",
        func=lambda s=editor: webbrowser.open("https://www.dwds.de/wb/" + urllib.parse.quote(s.note['Word'])),
        label="DWDS",
    ))

    buttons.append(editor.addButton(
        icon=None,
        cmd="reverso",
        func=lambda s=editor: webbrowser.open(
            "https://context.reverso.net/translation/german-russian/" + urllib.parse.quote(s.note['Word'])),
        label="Reverso",
    ))

    return buttons


def fill_card_with_chatgpt(editor: 'aqt.editor.Editor', gpt_model: str):
    note = editor.note

    if note["Word"] and not note['WordTranslation']:
        request = (f'Опиши краткий перевод немецкого слова {note["Word"]} на русский язык.'
                   f' Только перевод слова, никаких дополнительных текстов. Если слово имеет много значений,'
                   f' то перечисли переводы через запятую.')
        response = list(get_chatgpt_responses_texts(_chatgpt_request(request, gpt_model)))
        if response:
            note['WordTranslation'] = response[0]
        del request
        del response

    suffixes_to_fill = []
    suffixes_to_translate = []

    for suffix in ['', '2', '3']:
        front_example = html_to_text(note[f'FrontExample{suffix}'] or '').strip()
        back_example = html_to_text(note[f'BackExample{suffix}'] or '').strip()
        if front_example and not back_example:
            suffixes_to_translate.append(suffix)
        elif not front_example and not back_example:
            suffixes_to_fill.append(suffix)

    request = ''
    if suffixes_to_fill:
        if word := note['Word']:
            request += f"Приведи {len(suffixes_to_fill)} пример(а) использования немецкого слова \"{word}\"" \
                        " и переводы примеров на русский язык. Только примеры с переводами, без вводных текстов."
            for level in ['A1', 'A2', 'B1', 'B2']:
                if level in note.tags or level.lower() in note.tags:
                    break
            else:
                level = None
            if level:
                request = f'{request} Примеры должны быть понятны ученикам на уровне {level}.'
        else:
            showWarning("No word")
            return

    if suffixes_to_translate:
        if request:
            request += '\n\nИ ещё: '
        request += ('Переведи следующие предложения на русский язык. Формат должен быть следующий: исходное предложение'
                    ' на немецком языке, затем перевод предложения на русский язык.'
                    ' Модифицировать исходные предложения не следует.\n\nСписок предложений:\n')
        for s in suffixes_to_translate:
            request += '* ' + note[f'FrontExample{s}'] + '\n'

    if request:
        request += ('\nПримеры должны быть выведены в формате csv, в виде таблицы из двух столбцов без заголовков, где'
                    ' первый столбец это фраза на немецком языке, а второй столбец это фраза на русском языке.')
        response = _chatgpt_request(request, gpt_model)

        if response:
            for de_example, ru_example in converter.examples_from_chatgpt_responses(response):
                translated = False
                for suffix in suffixes_to_translate:
                    if de_example == note[f'FrontExample{suffix}']:
                        note[f'BackExample{suffix}'] = ru_example
                        translated = True
                        break

                if not translated and suffixes_to_fill:
                    suffix, suffixes_to_fill = suffixes_to_fill[0], suffixes_to_fill[1:]
                    note[f'FrontExample{suffix}'] = de_example
                    note[f'BackExample{suffix}'] = ru_example

    if 'chatgpt' not in note.tags:
        note.tags.append('chatgpt')
    editor.loadNote()


def _chatgpt_request(text: str, gpt_model: str) -> Optional[Dict]:
    token_file_name = os.path.expanduser("~/.anki-german-words-chatgpt-token.txt")
    try:
        with open(token_file_name) as f:
            token = f.read().strip()
    except Exception:
        showWarning("Get the token there: https://platform.openai.com/account/api-keys\n"
                    f"and put the token there: {token_file_name}")
        return

    params = {
        "model": gpt_model,
        "messages": [
            {
                "role": "user",
                "content": text,
            }
        ]
    }

    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        },
        data=json.dumps(params).encode('utf-8')
    )
    with urllib.request.urlopen(req) as response:
        response = json.load(response)
        pprint.pprint(response)
        return response


# TODO Delete me.
def on_setup_webview(editor):
    # editor._links['myButton'] = fill_german_word_fields
    pass


def on_browser_setup_menus(browser: Browser):
    browser.form.menu_Notes.addSeparator()

    action = QtGui.QAction(parent=browser)
    action.setText("Make Universal German Card")
    action.setShortcut("Meta+G")
    qconnect(action.triggered, lambda: on_make_universal_german_card(browser))

    browser.form.menu_Notes.addAction(action)


def on_make_universal_german_card(browser: Browser):
    if not (card := browser.card):
        return

    mw = browser.mw
    if not (note_type := get_universal_german_word_note_type(mw)):
        return

    old_note = card.note()
    if old_note.note_type() == note_type:
        new_note = old_note
    else:
        new_note = mw.col.new_note(note_type)
        old_note.tags.append("delete")
        old_note.col.update_note(old_note)

    old_note_dict = dict(old_note.items())
    pprint.pprint(old_note_dict)
    german_note = converter.convert(old_note_dict)
    pprint.pprint(german_note)
    if not german_note:
        return

    new_note['Word'] = new_note['Word'] or german_note.word
    new_note['WordTranslation'] = new_note['WordTranslation'] or german_note.translation
    new_note['Explanation'] = new_note['Explanation'] or german_note.explanation

    for de, ru in german_note.examples:
        for suffix in ['', '2', '3']:
            if not new_note[f'FrontExample{suffix}'] and not new_note[f'BackExample{suffix}']:
                new_note[f'FrontExample{suffix}'] = de
                new_note[f'BackExample{suffix}'] = ru
                break
        else:
            break

    _fill_note_from_wiktionary(new_note)

    add_cards_dialog: AddCards = dialogs.open("AddCards", mw)
    add_cards_dialog.set_note(new_note, None)
