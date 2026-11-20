import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import FOAF, OWL, RDF, RDFS, SDO, XSD
import data
from common import EX, OUT_DIR, TTL_FILE, VOC, bind_namespaces


def add_vocabulary(g: Graph):
    
    classes = {
        VOC.Developer: ("Developer", SDO.Organization),
        VOC.Genre: ("Genre", None),
        VOC.Platform: ("Platform", None),
    }

    for cls, (label, parent) in classes.items():
        g.add((cls, RDF.type, RDFS.Class))
        g.add((cls, RDFS.label, Literal(label, lang="en")))
        if parent is not None:
            g.add((cls, RDFS.subClassOf, parent))

    properties = {
        VOC.developedBy: ("developed by", SDO.VideoGame, VOC.Developer),
        VOC.hasGenre: ("has genre", SDO.VideoGame, VOC.Genre),
        VOC.releaseYear: ("release year", SDO.VideoGame, XSD.integer),
        VOC.foundingYear: ("founding year", VOC.Developer, XSD.integer),
    }

    for prop, (label, domain, range_) in properties.items():
        g.add((prop, RDF.type, RDF.Property))
        g.add((prop, RDFS.label, Literal(label, lang="en")))
        g.add((prop, RDFS.domain, domain))
        g.add((prop, RDFS.range, range_))


def build_graph():
    
    g = bind_namespaces(Graph())
    add_vocabulary(g)

    for cid, name in data.COUNTRIES.items():
        g.add((EX[cid], RDF.type, SDO.Country))
        g.add((EX[cid], SDO.name, Literal(name, lang="en")))

    for gid, name in data.GENRES.items():
        g.add((EX[gid], RDF.type, VOC.Genre))
        g.add((EX[gid], SDO.name, Literal(name, lang="en")))

    for pid, name in data.PLATFORMS.items():
        g.add((EX[pid], RDF.type, VOC.Platform))
        g.add((EX[pid], SDO.name, Literal(name, lang="en")))

    for did, (name, year, country) in data.DEVELOPERS.items():
        g.add((EX[did], RDF.type, VOC.Developer))
        g.add((EX[did], SDO.name, Literal(name, lang="en")))
        g.add((EX[did], VOC.foundingYear, Literal(year, datatype=XSD.integer)))
        g.add((EX[did], SDO.foundingLocation, EX[country]))

    for pid, (name, employer) in data.PERSONS.items():
        g.add((EX[pid], RDF.type, FOAF.Person))
        g.add((EX[pid], FOAF.name, Literal(name)))
        g.add((EX[pid], SDO.worksFor, EX[employer]))

    for game in data.GAMES:
        s = EX[game["id"]]
        g.add((s, RDF.type, SDO.VideoGame))
        g.add((s, SDO.name, Literal(game["name"], lang="en")))
        g.add((s, VOC.releaseYear, Literal(game["year"], datatype=XSD.integer)))
        g.add((s, VOC.developedBy, EX[game["developer"]]))
        for genre in game["genres"]:
            g.add((s, VOC.hasGenre, EX[genre]))
        for platform in game["platforms"]:
            g.add((s, SDO.gamePlatform, EX[platform]))
        if game["director"]:
            g.add((s, SDO.director, EX[game["director"]]))
    return g


TYPE_COLORS = {
    SDO.VideoGame: "#4C78A8",
    VOC.Developer: "#F58518",
    VOC.Genre: "#54A24B",
    VOC.Platform: "#B279A2",
    SDO.Country: "#E45756",
    FOAF.Person: "#9D755D",
}

TYPE_LABELS = {
    SDO.VideoGame: "Гра (schema:VideoGame)",
    VOC.Developer: "Розробник (voc:Developer)",
    VOC.Genre: "Жанр (voc:Genre)",
    VOC.Platform: "Платформа (voc:Platform)",
    SDO.Country: "Країна (schema:Country)",
    FOAF.Person: "Людина (foaf:Person)",
}


def visualize(g: Graph, path):
    node_type = {s: t for s, t in g.subject_objects(RDF.type) if t in TYPE_COLORS}
    G = nx.DiGraph()
    for node in node_type:
        G.add_node(node)
    for s, p, o in g:
        if isinstance(o, URIRef) and s in node_type and o in node_type and p != OWL.sameAs:
            G.add_edge(s, o, label=g.namespace_manager.normalizeUri(p))


    def local(uri):
        return str(uri).rsplit("/", 1)[-1]

    plt.figure(figsize=(20, 14))
    rings = [[SDO.VideoGame], [VOC.Developer, FOAF.Person], [SDO.Country, VOC.Genre, VOC.Platform]]
    shells = [sorted(n for n in G.nodes if node_type[n] in ring) for ring in rings]
    pos = nx.shell_layout(G, nlist=shells)
    nx.draw_networkx_nodes(G, pos, node_size=1500, node_color=[TYPE_COLORS[node_type[n]] for n in G.nodes], alpha=0.95)
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=14, edge_color="#999999", width=1.0, node_size=1500)
    nx.draw_networkx_labels(G, pos, labels={n: local(n) for n in G.nodes}, font_size=8)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, "label"), font_size=6, font_color="#555555", rotate=False)
    handles = [plt.Line2D([0], [0], marker="o", linestyle="", markersize=12, color=c, label=TYPE_LABELS[t]) for t, c in TYPE_COLORS.items()]
    plt.legend(handles=handles, loc="upper left", fontsize=10)
    plt.title("RDF-граф предметної області «Комп'ютерні ігри»", fontsize=15)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def print_stats(g: Graph):
    instances = {s for s, t in g.subject_objects(RDF.type) if t in TYPE_COLORS}
    used_types = {t for s, t in g.subject_objects(RDF.type) if t in TYPE_COLORS}
    object_props = {p for s, p, o in g if s in instances and o in instances}
    print(f"Трійок у графі:               {len(g)}")
    print(f"Типів сутностей:              {len(used_types)}")
    print(f"Екземплярів сутностей:        {len(instances)}")
    print(f"Типів зв'язків між сутностями: {len(object_props)}")
    for p in sorted(object_props):
        print(f"   - {g.namespace_manager.normalizeUri(p)}")


if __name__ == "__main__":
    graph = build_graph()
    print_stats(graph)

    graph.serialize(destination=TTL_FILE, format="turtle")
    graph.serialize(destination=OUT_DIR / "games.rdf", format="xml")
    graph.serialize(destination=OUT_DIR / "games.jsonld", format="json-ld", indent=2)
    print(f"\nЗбережено: {TTL_FILE.name}, games.rdf, games.jsonld")

    visualize(graph, OUT_DIR / "graph.png")
    print("Візуалізацію збережено: output/graph.png")
