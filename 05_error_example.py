from rdflib import Graph, Literal
from rdflib.namespace import RDF, SDO, XSD

from common import EX, NAMESPACES, VOC, bind_namespaces

WRONG_QUERY = """
SELECT ?gameName ?year WHERE {
    ?game a schema:VideoGame ; schema:name ?gameName ; voc:releaseYear ?year ; voc:developedBy ?dev .
    ?dev schema:name "CD Projekt Red" .
}
ORDER BY ?year
"""

FIXED_QUERY = """
SELECT ?gameName ?year WHERE {
    ?game a schema:VideoGame ; schema:name ?gameName ; voc:releaseYear ?year ; voc:developedBy ?dev .
    ?dev schema:name "CD Projekt Red"@en .
}
ORDER BY ?year
"""


GAMES = [
    ("Witcher3", "The Witcher 3: Wild Hunt", 2015, "CDProjektRed"),
    ("Cyberpunk2077", "Cyberpunk 2077", 2020, "CDProjektRed"),
    ("EldenRing", "Elden Ring", 2022, "FromSoftware"),
]
DEVELOPERS = {"CDProjektRed": "CD Projekt Red", "FromSoftware": "FromSoftware"}


def make_graph():
    g = bind_namespaces(Graph())
    for did, name in DEVELOPERS.items():
        g.add((EX[did], RDF.type, VOC.Developer))
        g.add((EX[did], SDO.name, Literal(name, lang="en")))
    for gid, name, year, developer in GAMES:
        g.add((EX[gid], RDF.type, SDO.VideoGame))
        g.add((EX[gid], SDO.name, Literal(name, lang="en")))
        g.add((EX[gid], VOC.releaseYear, Literal(year, datatype=XSD.integer)))
        g.add((EX[gid], VOC.developedBy, EX[developer]))
    return g


def run(g: Graph, label: str, query: str):
    print(label)
    print(query.strip())
    rows = list(g.query(query, initNs=NAMESPACES))
    print(f"Результат: {len(rows)} рядків")
    for game_name, year in rows:
        print(f"   {game_name} — {year}")
    print()


if __name__ == "__main__":
    g = make_graph()
    print("Як назва студії збережена в графі:")
    for name in g.objects(EX.CDProjektRed, SDO.name):
        print(f"   ex:CDProjektRed schema:name {name.n3()}\n")

    run(g, 'ПОМИЛКОВИЙ запит (назва без мовної позначки)', WRONG_QUERY)
    run(g, 'ВИПРАВЛЕНИЙ запит (назва з позначкою @en)', FIXED_QUERY)
