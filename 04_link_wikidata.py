import hashlib
import json
import time
from collections import defaultdict
from urllib.error import HTTPError

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SDO, XSD
from SPARQLWrapper import JSON, SPARQLWrapper

import data
from common import EX, LINKS_TTL_FILE, OUT_DIR, NAMESPACES, VOC, WD, WDT, bind_namespaces, load_graph, print_rows

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "SemanticWebLab1/1.0 (student educational project; contact: shchyev@gmail.com)"
CACHE_DIR = OUT_DIR / "wikidata_cache"


def wikidata_query(query: str):
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / (hashlib.md5(query.encode("utf-8")).hexdigest() + ".json")
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    sparql = SPARQLWrapper(WIKIDATA_ENDPOINT, agent=USER_AGENT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    for attempt in range(1, 5):
        try:
            rows = sparql.query().convert()["results"]["bindings"]
            cache_file.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
            return rows
        except HTTPError as exc:
            if exc.code != 429 or attempt == 4:
                raise
            wait = int(exc.headers.get("Retry-After") or 65)
            print(f"   Wikidata обмежує частоту запитів (429). Чекаю {wait} с, спроба {attempt}/4 ...")
            time.sleep(wait + 2)


def fetch_candidates(g: Graph):
    local = {str(g.value(game, SDO.name)): game for game in g.subjects(RDF.type, SDO.VideoGame)}
    values = " ".join('"%s"@en' % name.replace('"', '\\"') for name in local)
    query = f"""
        SELECT DISTINCT ?label ?item ?date ?genre ?genreLabel WHERE {{
            VALUES ?label {{ {values} }}
            ?item rdfs:label|skos:altLabel ?label .
            {{ ?item wdt:P31 wd:Q7889 }} UNION {{ ?item wdt:P178 ?anyDeveloper }}
            OPTIONAL {{ ?item wdt:P577 ?date }}
            OPTIONAL {{ ?item wdt:P136 ?genre .
                        ?genre rdfs:label ?genreLabel . FILTER (LANG(?genreLabel) = "en") }}
        }}
    """
    candidates = defaultdict(lambda: defaultdict(lambda: {"dates": set(), "genres": {}}))
    for row in wikidata_query(query):
        info = candidates[local[row["label"]["value"]]][URIRef(row["item"]["value"])]
        if "date" in row:
            info["dates"].add(row["date"]["value"][:10])
        if "genre" in row:
            info["genres"][URIRef(row["genre"]["value"])] = row["genreLabel"]["value"]
    return candidates


def fetch_details(items):
    values = " ".join("wd:" + str(item).rsplit("/", 1)[-1] for item in sorted(items))
    query = f"""
        SELECT ?item ?date ?genre ?genreLabel WHERE {{
            VALUES ?item {{ {values} }}
            OPTIONAL {{ ?item wdt:P577 ?date }}
            OPTIONAL {{ ?item wdt:P136 ?genre .
                        ?genre rdfs:label ?genreLabel . FILTER (LANG(?genreLabel) = "en") }}
        }}
    """
    details = defaultdict(lambda: {"dates": set(), "genres": {}})
    for row in wikidata_query(query):
        info = details[URIRef(row["item"]["value"])]
        if "date" in row:
            info["dates"].add(row["date"]["value"][:10])
        if "genre" in row:
            info["genres"][URIRef(row["genre"]["value"])] = row["genreLabel"]["value"]
    return details


def build_links(g: Graph, candidates: dict):
    links = bind_namespaces(Graph())
    print("Пошук ігор у Wikidata:")
    for game in sorted(g.subjects(RDF.type, SDO.VideoGame)):
        name, local_year = g.value(game, SDO.name), str(g.value(game, VOC.releaseYear))
        gid = str(game).rsplit("/", 1)[-1]
        cands = candidates.get(game, {})
        if gid in data.MANUAL_WIKIDATA_LINKS:
            links.add((game, OWL.sameAs, WD[data.MANUAL_WIKIDATA_LINKS[gid]]))
            print(f"   ВРУЧНУ {name} ({local_year}) -> {WD[data.MANUAL_WIKIDATA_LINKS[gid]]}")
            continue
        matching = [uri for uri, info in cands.items() if any(d.startswith(local_year) for d in info["dates"])]
        if len(matching) == 1:
            links.add((game, OWL.sameAs, matching[0]))
            print(f"   OK     {name} ({local_year}) -> {matching[0]}  (кандидатів: {len(cands)})")
        else:
            shown = {str(uri): sorted(info["dates"]) for uri, info in cands.items()}
            print(f"   ???    {name} ({local_year}): однозначного збігу немає; кандидати: {shown or 'жодного'}")
            print(f"          знайдіть гру на wikidata.org і впишіть її Q-номер у MANUAL_WIKIDATA_LINKS (data.py), ключ \"{gid}\"")

    for cid, qid in data.COUNTRY_WIKIDATA.items():
        links.add((EX[cid], OWL.sameAs, WD[qid]))
    return links


def external_triples(g_local: Graph, links: Graph):
    external = bind_namespaces(Graph())
    game_items = {item for game, item in links.subject_objects(OWL.sameAs)
                  if (game, RDF.type, SDO.VideoGame) in g_local}
    details = fetch_details(game_items)
    for item in game_items:
        info = details.get(item)
        if info is None:
            continue
        for date in info["dates"]:
            external.add((item, WDT.P577, Literal(date, datatype=XSD.date)))
        for genre, label in info["genres"].items():
            external.add((item, WDT.P136, genre))
            external.add((genre, RDFS.label, Literal(label, lang="en")))
    return external


COMBINED_QUERY = """
SELECT ?name ?localYear (MIN(?wdDate) AS ?wikidataDate)
       (GROUP_CONCAT(DISTINCT ?localGenre; separator=", ") AS ?localGenres)
       (GROUP_CONCAT(DISTINCT ?wdGenre; separator=", ") AS ?wikidataGenres)
WHERE {
    ?game a schema:VideoGame ;
          schema:name ?name ;
          voc:releaseYear ?localYear ;
          voc:hasGenre/schema:name ?localGenre ;
          owl:sameAs ?wd .
    ?wd wdt:P577 ?wdDate .
    OPTIONAL { ?wd wdt:P136/rdfs:label ?wdGenre }
}
GROUP BY ?name ?localYear
ORDER BY ?localYear ?name
"""

FEDERATED_QUERY = """
SELECT ?name ?localYear ?wdDate WHERE {
    ?game a schema:VideoGame ;
          schema:name ?name ;
          voc:releaseYear ?localYear ;
          owl:sameAs ?wd .
    SERVICE <https://query.wikidata.org/sparql> {
        ?wd wdt:P577 ?wdDate .
    }
}
ORDER BY ?localYear
"""

if __name__ == "__main__":
    g_local = load_graph()

    candidates = fetch_candidates(g_local)
    links = build_links(g_local, candidates)
    links.serialize(destination=LINKS_TTL_FILE, format="turtle")
    print(f"\nСтворено зв'язків owl:sameAs: {len(links)} -> {LINKS_TTL_FILE.name}\n")
    print(links.serialize(format="turtle"))

    external = external_triples(g_local, links)
    print(f"Отримано з Wikidata трійок: {len(external)}\n")

    merged = bind_namespaces(Graph())
    for part in (g_local, links, external):
        for triple in part:
            merged.add(triple)

    print("Запит, що поєднує власний граф і дані Wikidata:")
    print(COMBINED_QUERY)
    print_rows(merged.query(COMBINED_QUERY, initNs=NAMESPACES), merged)

    print("Федеративний варіант (SERVICE):")
    print(FEDERATED_QUERY)
    try:
        fed = bind_namespaces(Graph())
        for part in (g_local, links):
            for triple in part:
                fed.add(triple)
        print_rows(fed.query(FEDERATED_QUERY, initNs=NAMESPACES), fed)
    except Exception as exc:
        print(f"   SERVICE-запит не виконано: {type(exc).__name__}: {exc}")
        print("   Це очікувано, якщо точка доступу відхиляє клієнта або обмежує частоту запитів (429);")
        print("   основний результат — запит вище. Можна повторити запуск за кілька хвилин.")
