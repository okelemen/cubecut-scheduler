"""Generate the 24 November English upload packages and 25 localizations."""

import json
from pathlib import Path


ROOT = Path(__file__).parent
base = json.loads((ROOT / "egg.json").read_text(encoding="utf-8"))
source = json.loads((ROOT / "egg-localizations.json").read_text(encoding="utf-8"))

# (localized title noun, localized opening noun phrase) for chocolate and cake.
NAMES = {
    "es": (("Chocolate de pistacho y kataifi", "Un chocolate de pistacho y kataifi"), ("Tarta Selva Negra", "Una tarta Selva Negra")),
    "pt": (("Chocolate de pistáchio e kataifi", "Um chocolate de pistáchio e kataifi"), ("Bolo Floresta Negra", "Um bolo Floresta Negra")),
    "fr": (("Chocolat pistache-kadaïf", "Une tablette de chocolat pistache-kadaïf"), ("Gâteau Forêt-Noire", "Un gâteau Forêt-Noire")),
    "de": (("Pistazien-Kadayif-Schokolade", "Eine Pistazien-Kadayif-Schokolade"), ("Schwarzwälder Kirschtorte", "Eine Schwarzwälder Kirschtorte")),
    "it": (("Cioccolato al pistacchio e kataifi", "Una tavoletta di cioccolato al pistacchio e kataifi"), ("Torta Foresta Nera", "Una torta Foresta Nera")),
    "tr": (("Fıstıklı Kadayıflı Çikolata", "Fıstıklı kadayıflı bir çikolata"), ("Kara Orman Pastası", "Bir Kara Orman pastası")),
    "ru": (("Шоколад с фисташкой и катаифи", "Одна плитка шоколада с фисташкой и катаифи"), ("Торт Чёрный лес", "Один торт Чёрный лес")),
    "ja": (("ピスタチオカダイフチョコ", "ピスタチオカダイフチョコ1枚"), ("黒い森のケーキ", "黒い森のケーキ1個")),
    "ko": (("피스타치오 카다이프 초콜릿", "피스타치오 카다이프 초콜릿 하나"), ("블랙 포레스트 케이크", "블랙 포레스트 케이크 하나")),
    "pl": (("Czekolada pistacjowa z kataifi", "Jedna czekolada pistacjowa z kataifi"), ("Tort Czarny Las", "Jeden tort Czarny Las")),
    "nl": (("Pistache-kataifi-chocolade", "Eén pistache-kataifi-chocoladereep"), ("Zwartewoudtaart", "Eén Zwartewoudtaart")),
    "uk": (("Шоколад із фісташкою та катаїфі", "Одна плитка шоколаду з фісташкою та катаїфі"), ("Торт Чорний ліс", "Один торт Чорний ліс")),
    "lt": (("Pistacijų ir kataifi šokoladas", "Vienas pistacijų ir kataifi šokoladas"), ("Juodojo miško tortas", "Vienas Juodojo miško tortas")),
    "ro": (("Ciocolată cu fistic și kataifi", "O ciocolată cu fistic și kataifi"), ("Tort Pădurea Neagră", "Un tort Pădurea Neagră")),
    "sv": (("Pistage- och kataifichoklad", "En pistage- och kataifichoklad"), ("Schwarzwaldtårta", "En Schwarzwaldtårta")),
    "el": (("Σοκολάτα με φιστίκι και κανταΐφι", "Μία σοκολάτα με φιστίκι και κανταΐφι"), ("Τούρτα Μέλανας Δρυμός", "Μία τούρτα Μέλανας Δρυμός")),
    "cs": (("Pistáciová čokoláda s kataifi", "Jedna pistáciová čokoláda s kataifi"), ("Schwarzwaldský dort", "Jeden Schwarzwaldský dort")),
    "hu": (("Pisztáciás kadaif csokoládé", "Egy pisztáciás kadaif csokoládé"), ("Fekete-erdő torta", "Egy Fekete-erdő torta")),
    "da": (("Pistacie-kataifi-chokolade", "En pistacie-kataifi-chokolade"), ("Schwarzwalderkage", "En Schwarzwalderkage")),
    "no": (("Pistasj- og kataifisjokolade", "Én pistasj- og kataifisjokolade"), ("Schwarzwaldkake", "Én Schwarzwaldkake")),
    "fi": (("Pistaasi-kataifi-suklaa", "Yksi pistaasi-kataifi-suklaa"), ("Schwarzwaldinkakku", "Yksi Schwarzwaldinkakku")),
    "sk": (("Pistáciová čokoláda s kataifi", "Jedna pistáciová čokoláda s kataifi"), ("Schwarzwaldská torta", "Jedna Schwarzwaldská torta")),
    "hr": (("Čokolada s pistacijama i kadaifom", "Jedna čokolada s pistacijama i kadaifom"), ("Schwarzwald torta", "Jedna Schwarzwald torta")),
    "bg": (("Шоколад с шамфъстък и кадаиф", "Един шоколад с шамфъстък и кадаиф"), ("Торта Шварцвалд", "Една торта Шварцвалд")),
    "sr": (("Чоколада с пистаћима и кадаифом", "Једна чоколада с пистаћима и кадаифом"), ("Шварцвалд торта", "Једна Шварцвалд торта")),
}

assert set(NAMES) == set(source) and len(NAMES) == 25

for index, (english, count) in enumerate((("Pistachio Kataifi Chocolate Bar", 36.3), ("Black Forest Cake", 23.3))):
    slug = english.lower().replace(" ", "-")
    hashtag = english.lower().replace(" ", "")
    package = {
        "title": base["title"].replace("Egg", english),
        "description": base["description"].replace("One egg", "One " + english.lower())
            .replace("#egg", "#" + hashtag).replace("egg", english.lower())
            .replace("19.2", f"{count:.1f}"),
        "tags": [tag.replace("egg", english.lower()) for tag in base["tags"]],
    }
    locales = {}
    for code, old in source.items():
        title_noun, opening = NAMES[code][index]
        title = title_noun + " vs " + old["title"].split(" vs ", 1)[1]
        old_lines = old["description"].splitlines()
        delimiter = "、" if code == "ja" else ","
        old_first = old_lines[0]
        if code == "ja":
            rest = old_first.split(delimiter, 1)[1]
        else:
            rest = old_first.split(delimiter, 1)[1]
        first = opening + delimiter + rest
        count_local = f"{count:.1f}".replace(".", ",")
        first = first.replace("19,2", count_local)
        first = first.replace("1,920", f"{round(count * 100):,}")
        description = "\n".join([first] + old_lines[1:]).replace("#egg", "#" + hashtag)
        if "19,2" in description or "1,920" in description or "#egg" in description:
            raise ValueError(f"Stale egg text in {code}")
        if len(title) > 100 or not description:
            raise ValueError(f"Invalid localization in {code}: title length {len(title)}")
        locales[code] = {"title": title, "description": description}
    (ROOT / (slug + ".json")).write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / (slug + "-localizations.json")).write_text(json.dumps(locales, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(slug, len(locales))
