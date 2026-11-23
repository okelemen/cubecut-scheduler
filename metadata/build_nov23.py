"""Generate Egg and Hot Dog fixed upload packages in English plus 25 languages."""
import json
from pathlib import Path

ROOT=Path(__file__).parent
base=json.loads((ROOT/'apple.json').read_text(encoding='utf-8'))
source=json.loads((ROOT/'apple-localizations.json').read_text(encoding='utf-8'))
NAMES={
 'es':(('Huevo','Un huevo'),('Perrito caliente','Un perrito caliente')),
 'pt':(('Ovo','Um ovo'),('Cachorro-quente','Um cachorro-quente')),
 'fr':(('Œuf','Un œuf'),('Hot-dog','Un hot-dog')),
 'de':(('Ei','Ein Ei'),('Hotdog','Ein Hotdog')),
 'it':(('Uovo','Un uovo'),('Hot dog','Un hot dog')),
 'tr':(('Yumurta','Bir yumurta'),('Sosisli sandviç','Bir sosisli sandviç')),
 'ru':(('Яйцо','Одно яйцо'),('Хот-дог','Один хот-дог')),
 'ja':(('卵','卵1個'),('ホットドッグ','ホットドッグ1本')),
 'ko':(('달걀','달걀 하나'),('핫도그','핫도그 하나')),
 'pl':(('Jajko','Jedno jajko'),('Hot dog','Jeden hot dog')),
 'nl':(('Ei','Eén ei'),('Hotdog','Eén hotdog')),
 'uk':(('Яйце','Одне яйце'),('Хот-дог','Один хот-дог')),
 'lt':(('Kiaušinis','Vienas kiaušinis'),('Dešrainis','Vienas dešrainis')),
 'ro':(('Ou','Un ou'),('Hot dog','Un hot dog')),
 'sv':(('Ägg','Ett ägg'),('Varmkorv','En varmkorv')),
 'el':(('Αυγό','Ένα αυγό'),('Χοτ ντογκ','Ένα χοτ ντογκ')),
 'cs':(('Vejce','Jedno vejce'),('Hot dog','Jeden hot dog')),
 'hu':(('Tojás','Egy tojás'),('Hot dog','Egy hot dog')),
 'da':(('Æg','Et æg'),('Hotdog','En hotdog')),
 'no':(('Egg','Ett egg'),('Pølse i brød','Én pølse i brød')),
 'fi':(('Kananmuna','Yksi kananmuna'),('Hodari','Yksi hodari')),
 'sk':(('Vajce','Jedno vajce'),('Hot dog','Jeden hot dog')),
 'hr':(('Jaje','Jedno jaje'),('Hot dog','Jedan hot dog')),
 'bg':(('Яйце','Едно яйце'),('Хотдог','Един хотдог')),
 'sr':(('Јаје','Једно јаје'),('Хот-дог','Један хот-дог')),
}
assert len(NAMES)==25 and set(NAMES)==set(source)
for index,(english,count) in enumerate((('Egg',19.2),('Hot Dog',23.7))):
    slug=english.lower().replace(' ','-')
    noun=english.lower()
    hashtag=noun.replace(' ','')
    number=f'{count:.1f}'
    package={
      'title':base['title'].replace('Apple',english),
      'description':base['description'].replace('#apple','#'+hashtag).replace('apple',noun).replace('19.9',number),
      'tags':[tag.replace('apple',noun) for tag in base['tags']],
    }
    locales={}
    for code,old in source.items():
        title_noun,opening=NAMES[code][index]
        title=title_noun+old['title'][old['title'].index(' vs '):]
        delimiter='、' if code=='ja' else ','
        desc=opening+old['description'][old['description'].index(delimiter):]
        desc=desc.replace('19,9',number.replace('.',','))
        desc=desc.replace('19.9',number)
        desc=desc.replace('1,989',f'{round(count*100):,}')
        desc=desc.replace('#apple','#'+hashtag)
        if any(stale in desc for stale in ('19,9','19.9','1,989','#apple')):
            raise ValueError(f'Stale translation in {code}')
        if len(title)>100 or not desc:
            raise ValueError(f'Invalid translation in {code}')
        locales[code]={'title':title,'description':desc}
    (ROOT/(slug+'.json')).write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/(slug+'-localizations.json')).write_text(json.dumps(locales,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(slug,len(locales))
