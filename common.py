from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import FOAF, OWL, RDF, RDFS, SDO, XSD

BASE_DIR = Path(__file__).parent
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(exist_ok=True)

TTL_FILE = OUT_DIR / "games.ttl"
EDITED_TTL_FILE = OUT_DIR / "games_edited.ttl"
LINKS_TTL_FILE = OUT_DIR / "wikidata_links.ttl"

EX = Namespace("http://example.org/games/resource/")
VOC = Namespace("http://example.org/games/vocab#")

WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")

NAMESPACES = {
    "ex": EX,
    "voc": VOC,
    "schema": SDO,
    "foaf": FOAF,
    "owl": OWL,
    "rdf": RDF,
    "rdfs": RDFS,
    "xsd": XSD,
    "wd": WD,
    "wdt": WDT,
}


def bind_namespaces(g: Graph):
    for prefix, ns in NAMESPACES.items():
        g.bind(prefix, ns, override=True)
    return g


def load_graph(path: Path = TTL_FILE):
    if not path.exists():
        raise SystemExit(f"Файл {path} не знайдено. Спершу запустіть 01_build_graph.py")
    g = Graph()
    g.parse(path, format="turtle")
    return bind_namespaces(g)


def short(g: Graph, term):
    try:
        return term.n3(g.namespace_manager)
    except Exception:
        return str(term)


def print_rows(result, g: Graph):
    def cell_text(cell) -> str:
        if cell is None:
            return ""
        if isinstance(cell, URIRef):
            return short(g, cell)
        return str(cell)

    headers = [str(v) for v in result.vars]
    rows = [[cell_text(cell) for cell in row] for row in result]
    widths = [max([len(h)] + [len(r[i]) for r in rows]) for i, h in enumerate(headers)]
    line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(line)
    print("-+-".join("-" * w for w in widths))
    for r in rows:
        print(" | ".join(c.ljust(w) for c, w in zip(r, widths)))
    print(f"({len(rows)} рядків)\n")
