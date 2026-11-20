from rdflib import Literal
from rdflib.namespace import RDF, SDO
from common import EDITED_TTL_FILE, EX, TTL_FILE, VOC, load_graph, short


def print_triples(g, triples, limit=None):
    for i, (s, p, o) in enumerate(sorted(triples, key=lambda t: tuple(str(x) for x in t))):
        if limit is not None and i >= limit:
            print(f"   ... (показано {limit})")
            break
        print(f"   {short(g, s)}  {short(g, p)}  {short(g, o)}")


if __name__ == "__main__":
    g = load_graph(TTL_FILE)
    print(f"1) Прочитано {TTL_FILE.name}: {len(g)} трійок\n")


    print("2) Вибрані трійки (усі ?game schema:name ?name для ігор):")
    for game in sorted(g.subjects(RDF.type, SDO.VideoGame)):
        for name in g.objects(game, SDO.name):
            print(f"   {short(g, game)}  schema:name  {short(g, name)}")


    print("\n3) Перші 15 трійок графу (відсортовано):")
    print_triples(g, g, limit=15)


    entity = EX.FromSoftware
    print(f"\n4) Сутність {short(g, entity)}")
    print("   а) трійки, де вона є суб'єктом:")
    print_triples(g, g.triples((entity, None, None)))
    print("   б) трійки, де вона є об'єктом:")
    print_triples(g, g.triples((None, None, entity)))


    print("\n5) Ручні зміни у Turtle:")
    if not EDITED_TTL_FILE.exists():
        print(f"   Файл {EDITED_TTL_FILE.name} ще не створено — виконайте кроки з шапки цього скрипта.")
    else:
        edited = load_graph(EDITED_TTL_FILE)
        added = set(edited) - set(g)
        removed = set(g) - set(edited)
        print(f"   У відредагованому файлі {len(edited)} трійок (було {len(g)}).")
        print(f"   Додано вручну: {len(added)}")
        print_triples(edited, added)
        print(f"   Видалено вручну: {len(removed)}")
        print_triples(g, removed)


    print("\n6) Програмна зміна графу (для порівняння з ручною):")
    g.add((EX.Witcher3, VOC.hasGenre, EX.ActionAdventure))
    g.set((EX.CDProjektRed, SDO.name, Literal("CD PROJEKT RED", lang="en")))
    print_triples(g, g.triples((EX.Witcher3, VOC.hasGenre, None)))
    print_triples(g, g.triples((EX.CDProjektRed, SDO.name, None)))
