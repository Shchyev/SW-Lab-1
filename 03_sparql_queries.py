from common import NAMESPACES, load_graph, print_rows

QUERIES = [
    (
        "Q1. Які ігри розробила студія CD Projekt Red? (зв'язок гра → розробник)",
        """
        SELECT ?gameName ?year WHERE {
            ?game a schema:VideoGame ;
                  schema:name ?gameName ;
                  voc:releaseYear ?year ;
                  voc:developedBy ?dev .
            ?dev schema:name "CD Projekt Red"@en .
        }
        ORDER BY ?year
        """,
    ),
    (
        "Q2. Які ігри вийшли після 2015 року? (FILTER + сортування)",
        """
        SELECT ?gameName ?year WHERE {
            ?game a schema:VideoGame ;
                  schema:name ?gameName ;
                  voc:releaseYear ?year .
            FILTER (?year > 2015)
        }
        ORDER BY DESC(?year) ?gameName
        """,
    ),
    (
        "Q3. Скільки ігор кожного розробника є у графі і хто має найбільше? (COUNT, GROUP BY)",
        """
        SELECT ?devName (COUNT(?game) AS ?games) (MIN(?year) AS ?firstRelease) WHERE {
            ?game a schema:VideoGame ;
                  voc:developedBy ?dev ;
                  voc:releaseYear ?year .
            ?dev schema:name ?devName .
        }
        GROUP BY ?devName
        ORDER BY DESC(?games) ?devName
        """,
    ),
    (
        "Q4. Ігри яких жанрів доступні на Nintendo Switch? (гра ↔ платформа ↔ жанр)",
        """
        SELECT DISTINCT ?genreName ?gameName WHERE {
            ?game a schema:VideoGame ;
                  schema:name ?gameName ;
                  schema:gamePlatform ex:Switch ;
                  voc:hasGenre ?genre .
            ?genre schema:name ?genreName .
        }
        ORDER BY ?genreName ?gameName
        """,
    ),
    (
        "Q5. Хто керував розробкою ігор, створених студіями з Японії? "
        "(3 зв'язки: людина ← director — гра — developedBy → студія — foundingLocation → країна)",
        """
        SELECT ?personName ?gameName ?devName WHERE {
            ?game schema:director ?person ;
                  schema:name ?gameName ;
                  voc:developedBy ?dev .
            ?dev schema:foundingLocation ?country ;
                 schema:name ?devName .
            ?country schema:name "Japan"@en .
            ?person foaf:name ?personName .
        }
        ORDER BY ?personName ?gameName
        """,
    ),
    (
        "Q6. На яких платформах доступні ігри студій, заснованих в Україні? "
        "(3 зв'язки: платформа ← гра → студія → країна; агрегація)",
        """
        SELECT ?platformName (COUNT(DISTINCT ?game) AS ?games)
               (GROUP_CONCAT(DISTINCT ?gameName; separator="; ") AS ?titles) WHERE {
            ?game schema:gamePlatform ?platform ;
                  schema:name ?gameName ;
                  voc:developedBy ?dev .
            ?dev schema:foundingLocation ex:Ukraine .
            ?platform schema:name ?platformName .
        }
        GROUP BY ?platformName
        ORDER BY DESC(?games) ?platformName
        """,
    ),
    (
        "Q7. Середній рік виходу ігор та їх кількість за країною розробника (AVG, HAVING)",
        """
        SELECT ?countryName (COUNT(?game) AS ?games) (AVG(?year) AS ?avgYear) WHERE {
            ?game voc:developedBy ?dev ;
                  voc:releaseYear ?year .
            ?dev schema:foundingLocation ?country .
            ?country schema:name ?countryName .
        }
        GROUP BY ?countryName
        HAVING (COUNT(?game) >= 2)
        ORDER BY ?countryName
        """,
    ),
]

if __name__ == "__main__":
    g = load_graph()
    for title, query in QUERIES:
        print("=" * 100)
        print(title)
        print(query.rstrip())
        print("\nРезультат:")
        print_rows(g.query(query, initNs=NAMESPACES), g)
