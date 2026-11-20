"""Generate fixed English and 25-language packages for 22 Nov objects."""

import json
from pathlib import Path

ROOT = Path(__file__).parent
base = json.loads((ROOT / "apple.json").read_text(encoding="utf-8"))
translated = json.loads((ROOT / "apple-localizations.json").read_text(encoding="utf-8"))

# (cucumber title, cucumber opening), (red bell pepper title, opening).
NAMES = {
    "es": (("Pepino", "Un pepino"), ("Pimiento rojo", "Un pimiento rojo")),
    "pt": (("Pepino", "Um pepino"), ("Pimentão vermelho", "Um pimentão vermelho")),
    "fr": (("Concombre", "Un concombre"), ("Poivron rouge", "Un poivron rouge")),
    "de": (("Gurke", "Eine Gurke"), ("Rote Paprika", "Eine rote Paprika")),
    "it": (("Cetriolo", "Un cetriolo"), ("Peperone rosso", "Un peperone rosso")),
    "tr": (("Salatalık", "Bir salatalık"), ("Kırmızı dolmalık biber", "Bir kırmızı dolmalık biber")),
    "ru": (("Огурец", "Один огурец"), ("Красный болгарский перец", "Один красный болгарский перец")),
    "ja": (("キュウリ", "キュウリ1本"), ("赤パプリカ", "赤パプリカ1個")),
    "ko": (("오이", "오이 하나"), ("빨간 피망", "빨간 피망 하나")),
    "pl": (("Ogórek", "Jeden ogórek"), ("Czerwona papryka", "Jedna czerwona papryka")),
    "nl": (("Komkommer", "Eén komkommer"), ("Rode paprika", "Eén rode paprika")),
    "uk": (("Огірок", "Один огірок"), ("Червоний болгарський перець", "Один червоний болгарський перець")),
    "lt": (("Agurkas", "Vienas agurkas"), ("Raudonoji paprika", "Viena raudonoji paprika")),
    "ro": (("Castravete", "Un castravete"), ("Ardei gras roșu", "Un ardei gras roșu")),
    "sv": (("Gurka", "En gurka"), ("Röd paprika", "En röd paprika")),
    "el": (("Αγγούρι", "Ένα αγγούρι"), ("Κόκκινη πιπεριά", "Μία κόκκινη πιπεριά")),
    "cs": (("Okurka", "Jedna okurka"), ("Červená paprika", "Jedna červená paprika")),
    "hu": (("Uborka", "Egy uborka"), ("Piros kaliforniai paprika", "Egy piros kaliforniai paprika")),
    "da": (("Agurk", "En agurk"), ("Rød peberfrugt", "En rød peberfrugt")),
    "no": (("Agurk", "En agurk"), ("Rød paprika", "En rød paprika")),
    "fi": (("Kurkku", "Yksi kurkku"), ("Punainen paprika", "Yksi punainen paprika")),
    "sk": (("Uhorka", "Jedna uhorka"), ("Červená paprika", "Jedna červená paprika")),
    "hr": (("Krastavac", "Jedan krastavac"), ("Crvena paprika", "Jedna crvena paprika")),
    "bg": (("Краставица", "Една краставица"), ("Червена чушка", "Една червена чушка")),
    "sr": (("Краставац", "Један краставац"), ("Црвена паприка", "Једна црвена паприка")),
}
assert set(NAMES) == set(translated) and len(NAMES) == 25

for index, (english, count) in enumerate((("Cucumber", 24.6), ("Red Bell Pepper", 13.0))):
    slug = english.lower().replace(" ", "-")
    noun = english.lower()
    hashtag = noun.replace(" ", "")
    number = f"{count:.1f}"
    description = base["description"].replace("#apple", "#" + hashtag)
    description = description.replace("apple", noun).replace("19.9", number)
    package = {
        "title": base["title"].replace("Apple", english),
        "description": description,
        "tags": [tag.replace("apple", noun) for tag in base["tags"]],
    }
    locales = {}
    for code, old in translated.items():
        title_noun, opening = NAMES[code][index]
        title = title_noun + old["title"][old["title"].index(" vs "):]
        old_desc = old["description"]
        delimiter = "、" if code == "ja" else ","
        desc = opening + old_desc[old_desc.index(delimiter):]
        desc = desc.replace("19,9", number.replace(".", ","))
        desc = desc.replace("19.9", number)
        desc = desc.replace("1,989", f"{round(count * 100):,}")
        desc = desc.replace("#apple", "#" + hashtag)
        if any(stale in desc for stale in ("19,9", "19.9", "1,989", "#apple")):
            raise ValueError(f"Stale source metadata in {code}")
        if len(title) > 100 or not desc:
            raise ValueError(f"Invalid localization in {code}")
        locales[code] = {"title": title, "description": desc}
    (ROOT / (slug + ".json")).write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / (slug + "-localizations.json")).write_text(json.dumps(locales, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(slug, len(locales))
