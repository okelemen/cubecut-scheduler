"""Locked CubeCut English package and 25 localized titles/descriptions for Nov 20."""

import json
from pathlib import Path

ROOT = Path(__file__).parent
base = json.loads((ROOT / "apple.json").read_text(encoding="utf-8"))
translated = json.loads((ROOT / "apple-localizations.json").read_text(encoding="utf-8"))

# (title noun, grammatical opening clause); banana, peach.
NAMES = {
    "es": (("Plátano", "Un plátano"), ("Melocotón", "Un melocotón")),
    "pt": (("Banana", "Uma banana"), ("Pêssego", "Um pêssego")),
    "fr": (("Banane", "Une banane"), ("Pêche", "Une pêche")),
    "de": (("Banane", "Eine Banane"), ("Pfirsich", "Ein Pfirsich")),
    "it": (("Banana", "Una banana"), ("Pesca", "Una pesca")),
    "tr": (("Muz", "Bir muz"), ("Şeftali", "Bir şeftali")),
    "ru": (("Банан", "Один банан"), ("Персик", "Один персик")),
    "ja": (("バナナ", "バナナ1本"), ("桃", "桃1個")),
    "ko": (("바나나", "바나나 하나"), ("복숭아", "복숭아 하나")),
    "pl": (("Banan", "Jeden banan"), ("Brzoskwinia", "Jedna brzoskwinia")),
    "nl": (("Banaan", "Eén banaan"), ("Perzik", "Eén perzik")),
    "uk": (("Банан", "Один банан"), ("Персик", "Один персик")),
    "lt": (("Bananas", "Vienas bananas"), ("Persikas", "Vienas persikas")),
    "ro": (("Banană", "O banană"), ("Piersică", "O piersică")),
    "sv": (("Banan", "En banan"), ("Persika", "En persika")),
    "el": (("Μπανάνα", "Μία μπανάνα"), ("Ροδάκινο", "Ένα ροδάκινο")),
    "cs": (("Banán", "Jeden banán"), ("Broskev", "Jedna broskev")),
    "hu": (("Banán", "Egy banán"), ("Őszibarack", "Egy őszibarack")),
    "da": (("Banan", "En banan"), ("Fersken", "En fersken")),
    "no": (("Banan", "En banan"), ("Fersken", "En fersken")),
    "fi": (("Banaani", "Yksi banaani"), ("Persikka", "Yksi persikka")),
    "sk": (("Banán", "Jeden banán"), ("Broskyňa", "Jedna broskyňa")),
    "hr": (("Banana", "Jedna banana"), ("Breskva", "Jedna breskva")),
    "bg": (("Банан", "Един банан"), ("Праскова", "Една праскова")),
    "sr": (("Банана", "Једна банана"), ("Бресква", "Једна бресква")),
}
assert set(NAMES) == set(translated) and len(NAMES) == 25

for index, (english, count) in enumerate((("Banana", 15.2), ("Peach", 19.7))):
    slug = english.lower()
    english_number = f"{count:.1f}"
    package = {
        "title": base["title"].replace("Apple", english),
        "description": base["description"].replace("apple", slug).replace("19.9", english_number),
        "tags": [tag.replace("apple", slug) for tag in base["tags"]],
    }
    locales = {}
    for code, old in translated.items():
        noun, clause = NAMES[code][index]
        title = noun + old["title"][old["title"].index(" vs "):]
        old_desc = old["description"]
        delimiter = "、" if code == "ja" else ","
        desc = clause + old_desc[old_desc.index(delimiter):]
        desc = desc.replace("19,9", english_number.replace(".", ","))
        desc = desc.replace("19.9", english_number)
        desc = desc.replace("1,989", f"{round(count*100):,}")
        desc = desc.replace("#apple", "#" + slug)
        if "19,9" in desc or "19.9" in desc or "1,989" in desc or "#apple" in desc:
            raise ValueError(f"Stale number or hashtag in {code}")
        if len(title) > 100 or not desc:
            raise ValueError(f"Invalid localized title/description in {code}")
        locales[code] = {"title": title, "description": desc}
    (ROOT / (slug + ".json")).write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / (slug + "-localizations.json")).write_text(json.dumps(locales, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(slug, len(locales))
