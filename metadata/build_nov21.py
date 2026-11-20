"""Generate the fixed English package and 25 translations for 21 Nov."""

import json
from pathlib import Path

ROOT = Path(__file__).parent
base = json.loads((ROOT / "apple.json").read_text(encoding="utf-8"))
translated = json.loads((ROOT / "apple-localizations.json").read_text(encoding="utf-8"))

# Each pair is (translated title noun, natural opening clause).
NAMES = {
    "es": (("Granada", "Una granada"), ("Tomate", "Un tomate")),
    "pt": (("Romã", "Uma romã"), ("Tomate", "Um tomate")),
    "fr": (("Grenade", "Une grenade"), ("Tomate", "Une tomate")),
    "de": (("Granatapfel", "Ein Granatapfel"), ("Tomate", "Eine Tomate")),
    "it": (("Melagrana", "Una melagrana"), ("Pomodoro", "Un pomodoro")),
    "tr": (("Nar", "Bir nar"), ("Domates", "Bir domates")),
    "ru": (("Гранат", "Один гранат"), ("Помидор", "Один помидор")),
    "ja": (("ザクロ", "ザクロ1個"), ("トマト", "トマト1個")),
    "ko": (("석류", "석류 하나"), ("토마토", "토마토 하나")),
    "pl": (("Granat", "Jeden granat"), ("Pomidor", "Jeden pomidor")),
    "nl": (("Granaatappel", "Eén granaatappel"), ("Tomaat", "Eén tomaat")),
    "uk": (("Гранат", "Один гранат"), ("Помідор", "Один помідор")),
    "lt": (("Granatas", "Vienas granatas"), ("Pomidoras", "Vienas pomidoras")),
    "ro": (("Rodie", "O rodie"), ("Roșie", "O roșie")),
    "sv": (("Granatäpple", "Ett granatäpple"), ("Tomat", "En tomat")),
    "el": (("Ρόδι", "Ένα ρόδι"), ("Ντομάτα", "Μία ντομάτα")),
    "cs": (("Granátové jablko", "Jedno granátové jablko"), ("Rajče", "Jedno rajče")),
    "hu": (("Gránátalma", "Egy gránátalma"), ("Paradicsom", "Egy paradicsom")),
    "da": (("Granatæble", "Et granatæble"), ("Tomat", "En tomat")),
    "no": (("Granateple", "Et granateple"), ("Tomat", "En tomat")),
    "fi": (("Granaattiomena", "Yksi granaattiomena"), ("Tomaatti", "Yksi tomaatti")),
    "sk": (("Granátové jablko", "Jedno granátové jablko"), ("Paradajka", "Jedna paradajka")),
    "hr": (("Nar", "Jedan nar"), ("Rajčica", "Jedna rajčica")),
    "bg": (("Нар", "Един нар"), ("Домат", "Един домат")),
    "sr": (("Нар", "Један нар"), ("Парадајз", "Један парадајз")),
}
assert set(NAMES) == set(translated) and len(NAMES) == 25

for index, (english, count) in enumerate((("Pomegranate", 17.6), ("Tomato", 18.0))):
    slug = english.lower()
    number = f"{count:.1f}"
    package = {
        "title": base["title"].replace("Apple", english),
        "description": base["description"].replace("apple", slug).replace("19.9", number),
        "tags": [tag.replace("apple", slug) for tag in base["tags"]],
    }
    locales = {}
    for code, old in translated.items():
        noun, clause = NAMES[code][index]
        title = noun + old["title"][old["title"].index(" vs "):]
        old_desc = old["description"]
        delimiter = "、" if code == "ja" else ","
        desc = clause + old_desc[old_desc.index(delimiter):]
        desc = desc.replace("19,9", number.replace(".", ","))
        desc = desc.replace("19.9", number)
        desc = desc.replace("1,989", f"{round(count * 100):,}")
        desc = desc.replace("#apple", "#" + slug)
        if any(stale in desc for stale in ("19,9", "19.9", "1,989", "#apple")):
            raise ValueError(f"Stale apple metadata in {code}")
        if len(title) > 100 or not desc:
            raise ValueError(f"Invalid localization in {code}")
        locales[code] = {"title": title, "description": desc}
    (ROOT / (slug + ".json")).write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / (slug + "-localizations.json")).write_text(json.dumps(locales, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(slug, len(locales))
