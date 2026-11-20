COUNTRIES = {
    "Poland": "Poland",
    "Ukraine": "Ukraine",
    "Japan": "Japan",
    "USA": "United States of America",
}

COUNTRY_WIKIDATA = {
    "Poland": "Q36",
    "Ukraine": "Q212",
    "Japan": "Q17",
    "USA": "Q30",
}

MANUAL_WIKIDATA_LINKS = {
    "GodOfWar2018": "Q18345138",
    "EldenRing": "Q64826862",
    "Hades": "Q59756366",
    "Metro2033": "Q162751",
    "DarkSouls": "Q1166232",	
}

GENRES = {
    "ActionRPG": "Action role-playing game",
    "FPS": "First-person shooter",
    "SurvivalHorror": "Survival horror",
    "ActionAdventure": "Action-adventure game",
    "Roguelike": "Roguelike",
}

PLATFORMS = {
    "PC": "Microsoft Windows (PC)",
    "PS3": "PlayStation 3",
    "PS4": "PlayStation 4",
    "PS5": "PlayStation 5",
    "Xbox360": "Xbox 360",
    "XboxOne": "Xbox One",
    "Switch": "Nintendo Switch",
}

DEVELOPERS = {
    "CDProjektRed": ("CD Projekt Red", 2002, "Poland"),
    "GSCGameWorld": ("GSC Game World", 1995, "Ukraine"),
    "4AGames": ("4A Games", 2006, "Ukraine"),
    "FromSoftware": ("FromSoftware", 1986, "Japan"),
    "Nintendo": ("Nintendo", 1889, "Japan"),
    "RockstarGames": ("Rockstar Games", 1998, "USA"),
    "SantaMonicaStudio": ("Santa Monica Studio", 1999, "USA"),
    "SupergiantGames": ("Supergiant Games", 2009, "USA"),
}

PERSONS = {
    "KonradTomaszkiewicz": ("Konrad Tomaszkiewicz", "CDProjektRed"),
    "AdamBadowski": ("Adam Badowski", "CDProjektRed"),
    "HidetakaMiyazaki": ("Hidetaka Miyazaki", "FromSoftware"),
    "HidemaroFujibayashi": ("Hidemaro Fujibayashi", "Nintendo"),
    "CoryBarlog": ("Cory Barlog", "SantaMonicaStudio"),
    "GregKasavin": ("Greg Kasavin", "SupergiantGames"),
}

GAMES = [
    {
        "id": "Witcher3",
        "name": "The Witcher 3: Wild Hunt",
        "year": 2015,
        "developer": "CDProjektRed",
        "genres": ["ActionRPG"],
        "platforms": ["PC", "PS4", "XboxOne", "Switch"],
        "director": "KonradTomaszkiewicz",
    },
    {
        "id": "Cyberpunk2077",
        "name": "Cyberpunk 2077",
        "year": 2020,
        "developer": "CDProjektRed",
        "genres": ["ActionRPG"],
        "platforms": ["PC", "PS4", "PS5", "XboxOne"],
        "director": "AdamBadowski",
    },
    {
        "id": "StalkerSoC",
        "name": "S.T.A.L.K.E.R.: Shadow of Chernobyl",
        "year": 2007,
        "developer": "GSCGameWorld",
        "genres": ["FPS", "SurvivalHorror"],
        "platforms": ["PC"],
        "director": None,
    },
    {
        "id": "Metro2033",
        "name": "Metro 2033",
        "year": 2010,
        "developer": "4AGames",
        "genres": ["FPS", "SurvivalHorror"],
        "platforms": ["PC", "Xbox360"],
        "director": None,
    },
    {
        "id": "DarkSouls",
        "name": "Dark Souls",
        "year": 2011,
        "developer": "FromSoftware",
        "genres": ["ActionRPG"],
        "platforms": ["PC", "PS3", "Xbox360"],
        "director": "HidetakaMiyazaki",
    },
    {
        "id": "EldenRing",
        "name": "Elden Ring",
        "year": 2022,
        "developer": "FromSoftware",
        "genres": ["ActionRPG"],
        "platforms": ["PC", "PS4", "PS5", "XboxOne"],
        "director": "HidetakaMiyazaki",
    },
    {
        "id": "ZeldaBotW",
        "name": "The Legend of Zelda: Breath of the Wild",
        "year": 2017,
        "developer": "Nintendo",
        "genres": ["ActionAdventure"],
        "platforms": ["Switch"],
        "director": "HidemaroFujibayashi",
    },
    {
        "id": "RDR2",
        "name": "Red Dead Redemption 2",
        "year": 2018,
        "developer": "RockstarGames",
        "genres": ["ActionAdventure"],
        "platforms": ["PC", "PS4", "XboxOne"],
        "director": None,
    },
    {
        "id": "GodOfWar2018",
        "name": "God of War",
        "year": 2018,
        "developer": "SantaMonicaStudio",
        "genres": ["ActionAdventure"],
        "platforms": ["PC", "PS4"],
        "director": "CoryBarlog",
    },
    {
        "id": "Hades",
        "name": "Hades",
        "year": 2020,
        "developer": "SupergiantGames",
        "genres": ["Roguelike", "ActionRPG"],
        "platforms": ["PC", "PS4", "PS5", "XboxOne", "Switch"],
        "director": "GregKasavin",
    },
]
