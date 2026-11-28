"""Prepare 29 November packages from the approved 25-language templates."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPECS = {
    "salted-caramel-pretzel-chocolate-bar": {
        "template": "honeycomb-crunch-chocolate-bar",
        "plan": Path(r"C:\Users\eleme\kesim-sayaci-nov29-salted\plan-salted-caramel-pretzel-chocolate-bar.json"),
        "name": "Salted Caramel Pretzel Chocolate Bar",
        "names": {
            "es":"Tableta de chocolate con caramelo salado y pretzel",
            "pt":"Barra de chocolate com caramelo salgado e pretzel",
            "fr":"Tablette de chocolat au caramel salé et bretzel",
            "de":"Schokoladentafel mit Salzkaramell und Brezel",
            "it":"Tavoletta di cioccolato con caramello salato e pretzel",
            "tr":"Tuzlu Karamelli Pretzelli Çikolata",
            "ru":"Шоколадная плитка с солёной карамелью и кренделем",
            "ja":"塩キャラメルとプレッツェルのチョコレートバー",
            "ko":"솔티드 캐러멜 프레첼 초콜릿 바",
            "pl":"Tabliczka czekolady ze słonym karmelem i preclem",
            "nl":"Chocoladereep met gezouten karamel en pretzel",
            "uk":"Шоколадна плитка із солоною карамеллю та кренделем",
            "lt":"Šokolado plytelė su sūdyta karamele ir riestainiu",
            "ro":"Tabletă de ciocolată cu caramel sărat și covrig",
            "sv":"Chokladkaka med salt karamell och pretzel",
            "el":"Πλάκα σοκολάτας με αλατισμένη καραμέλα και πρέτσελ",
            "cs":"Čokoládová tabulka se slaným karamelem a preclíkem",
            "hu":"Sós karamellás pereces csokoládétábla",
            "da":"Chokoladeplade med saltkaramel og pretzel",
            "no":"Sjokoladeplate med salt karamell og pretzel",
            "fi":"Suolakaramelli-pretzelsuklaalevy",
            "sk":"Čokoládová tabuľka so slaným karamelom a praclíkom",
            "hr":"Čokoladna ploča sa slanom karamelom i perecom",
            "bg":"Шоколад със солен карамел и претцел",
            "sr":"Чоколадна табла са сланим карамелом и перецом",
        },
    },
    "basque-burnt-cheesecake": {
        "template": "galaxy-mirror-glaze-cake",
        "plan": Path(r"C:\Users\eleme\kesim-sayaci-nov29-basque\plan-basque-burnt-cheesecake.json"),
        "name": "Basque Burnt Cheesecake",
        "names": {
            "es":"Tarta de queso vasca quemada",
            "pt":"Cheesecake basca queimada",
            "fr":"Cheesecake basque brûlé",
            "de":"Baskischer Käsekuchen mit dunkler Kruste",
            "it":"Cheesecake basca bruciata",
            "tr":"Yanık Bask Cheesecake",
            "ru":"Баскский жжёный чизкейк",
            "ja":"バスクチーズケーキ",
            "ko":"바스크 번트 치즈케이크",
            "pl":"Baskijski sernik z przypieczonym wierzchem",
            "nl":"Baskische gebrande cheesecake",
            "uk":"Баскський підпалений чізкейк",
            "lt":"Baskiškas apskrudęs sūrio pyragas",
            "ro":"Cheesecake basc ars",
            "sv":"Baskisk bränd cheesecake",
            "el":"Βασκικό καμένο τσιζκέικ",
            "cs":"Baskický připálený cheesecake",
            "hu":"Baszk égetett sajttorta",
            "da":"Baskisk brændt cheesecake",
            "no":"Baskisk brent ostekake",
            "fi":"Baskilainen poltettu juustokakku",
            "sk":"Baskický pripálený cheesecake",
            "hr":"Baskijska zapečena torta od sira",
            "bg":"Баски изгорял чийзкейк",
            "sr":"Баскијски загорели чизкејк",
        },
    },
}

for slug, spec in SPECS.items():
    old = spec["template"]
    old_tag = old.replace("-", "")
    new_tag = spec["name"].lower().replace(" ", "")
    source = json.loads((ROOT / f"{old}.json").read_text(encoding="utf-8"))
    old_loc = json.loads((ROOT / f"{old}-localizations.json").read_text(encoding="utf-8"))
    n = json.loads(spec["plan"].read_text(encoding="utf-8"))["turlar"][-1]["kup"]
    old_m = re.search(r"about (\d+\.\d+) million cubes", source["description"]).group(1)
    new_m = f"{n/1_000_000:.1f}"
    old_name = source["title"].split(" vs ")[0]
    result = {
        "title": source["title"].replace(old_name, spec["name"], 1),
        "description": source["description"].replace(old_name.lower(), spec["name"].lower(), 1).replace(f"about {old_m} million cubes", f"about {new_m} million cubes").replace(old_tag,new_tag),
        "tags": [t.replace(old_name.lower(),spec["name"].lower()).replace(old_tag,new_tag) for t in source["tags"]],
    }
    old_count = "3,630" if old.startswith("honeycomb") else "2,935"
    new_count = f"{round(n/10000):,}"
    loc = {}
    for lang,item in old_loc.items():
        prior=item["title"].split(" vs ")[0]
        product=spec["names"][lang]
        title=item["title"].replace(prior,product,1)
        desc,replaced=re.subn(re.escape(prior),lambda _: product,item["description"],count=1,flags=re.IGNORECASE)
        if not replaced and lang=="lt":
            desc=re.sub(r"^Vienas [^,]+","Vienas "+product.casefold(),desc,count=1)
        elif not replaced and lang=="hu":
            desc=re.sub(r"^Egy [^,]+","Egy "+product.casefold(),desc,count=1)
        elif not replaced:
            raise ValueError((slug,lang,prior))
        if lang in ("ja","ko"):
            desc=desc.replace(old_count,new_count,1)
        else:
            desc=desc.replace(old_m.replace(".",","),new_m.replace(".",","),1)
        desc=desc.replace(old_tag,new_tag)
        if len(title)>100:
            title=title.replace(" #oddlysatisfying","")
        loc[lang]={"title":title,"description":desc}
    assert len(loc)==25 and all(len(x["title"])<=100 for x in loc.values())
    assert len(result["title"])<=100
    (ROOT/f"{slug}.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (ROOT/f"{slug}-localizations.json").write_text(json.dumps(loc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(slug,n,len(loc))
