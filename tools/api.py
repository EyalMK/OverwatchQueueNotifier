from flask import Flask, jsonify

app = Flask(__name__)

# Heroes
tanks = {
    "D.Va": ["D.Va", "d.va", "dva", "Dva"],
    "Doomfist": ["Doom", "doom", "DF", "df", "doomfist", "Doomfist"],
    "Junker Queen": ["Junker Queen", "JQ", "Queen", "queen", "junker", "jq"],
    "Orisa": ["orisa", "Orisa", "horse"],
    "Ramattra": ["Ramattra", "Ram", "ram"],
    "Reinhardt": ["Reinhardt", "Rein", "rein"],
    "Roadhog": ["Roadhog", "road", "hog", "Hog"],
    "Sigma": ["Sigma", "sigma", "sig", "Sig"],
    "Winston": ["Winston", "winston", "monkey", "winton", "Winton"],
    "Wrecking Ball": ["Wrecking Ball", "wrecking ball", "Ball", "ball", "hamster", "Hamster", "Hammond", "hammond"],
    "Zarya": ["Zarya", "zarya"],
    # "Mauga": ["Mauga", "mauga", "mau", "Mau"]
}

dps = {
    "Ashe": ["Ashe", "ashe"],
    "Bastion": ["Bastion", "bastion", "bast", "Bast"],
    "Cassidy": ["Cassidy", "cassidy", "Cree", "cree"],
    "Echo": ["Echo", "echo"],
    "Genji": ["Genji", "genji", "genju"],
    "Hanzo": ["Hanzo", "hanzo"],
    "Junkrat": ["Junkrat", "junkrat", "Junk", "junk"],
    "Mei": ["Mei", "mei", "the devil"],
    "Pharah": ["Pharah", "pharah", "phara", "Phara"],
    "Reaper": ["Reaper", "reaper", "reap"],
    "Sojourn": ["Sojourn", "sojourn", "Soj", "soj"],
    "Soldier: 76": ["Soldier: 76", "soldier: 76", "Soldier", "soldier", "sold", "Sold", "legs", "Legs"],
    "Sombra": ["Sombra", "sombra", "somb"],
    "Symmetra": ["Symmetra", "symmetra", "sym", "Symetra", "symetra"],
    "Torbjorn": ["Torbjorn", "torbjorn", "Torb", "torb"],
    "Tracer": ["Tracer", "tracer", "tr"],
    "Widowmaker": ["Widowmaker", "widowmaker", "Widow", "widow"]
}

supports = {
    "Ana": ["Ana", "ana"],
    "Baptiste": ["Baptiste", "baptiste", "bap", "Bap"],
    "Brigette": ["Brigette", "brigette", "brig", "Brig"],
    "Illari": ["Illari", "illari"],
    "Kiriko": ["Kiriko", "kiriko", "Kiri", "kiri"],
    "Lifeweaver": ["Lifeweaver", "lifeweaver", "life", "Life", "Weaver", "weaver", "wifeleaver", "Wifeleaver"],
    "Lucio": ["Lucio", "lucio"],
    "Mercy": ["Mercy", "mercy"],
    "Moira": ["Moira", "moira"],
    "Zenyatta": ["Zenyatta", "zenyatta", "Zen", "zen"]
}

heroes_coordinates_1920x1080 = {
    # Tanks
    "D.Va": [250, 830],
    "Doomfist": [320, 830],
    "Junker Queen": [370, 830],
    "Orisa": [440, 830],
    "Ramattra": [500, 830],
    "Reinhardt": [570, 830],
    "Roadhog": [320, 890],
    "Sigma": [370, 890],
    "Winston": [440, 890],
    "Wrecking Ball": [500, 890],
    "Zarya": [570, 890],
    # "Mauga": [440, 830],
    # "Orisa": [500, 830],
    # "Ramattra": [570, 830],
    # "Reinhardt": [250, 890],

    # Dps'
    "Ashe": [740, 830],
    "Bastion": [800, 830],
    "Cassidy": [860, 830],
    "Echo": [920, 830],
    "Genji": [990, 830],
    "Hanzo": [1060, 830],
    "Junkrat": [1120, 830],
    "Mei": [1180, 830],
    "Pharah": [1250, 830],
    "Reaper": [770, 890],
    "Sojourn": [830, 890],
    "Soldier: 76": [890, 890],
    "Sombra": [960, 890],
    "Symmetra": [1020, 890],
    "Torbjorn": [1090, 890],
    "Tracer": [1150, 890],
    "Widowmaker": [1220, 890],

    # Supports
    "Ana": [1410, 830],
    "Baptiste": [1480, 830],
    "Brigette": [1530, 830],
    "Illari": [1600, 830],
    "Kiriko": [1660, 830],
    "Lifeweaver": [1410, 890],
    "Lucio": [1480, 890],
    "Mercy": [1530, 890],
    "Moira": [1600, 890],
    "Zenyatta": [1660, 890]
}

heroes_coordinates_2560x1440 = {hero: [int(coord[0] * 1.3333), int(coord[1] * 1.3333)] for hero, coord in
                                heroes_coordinates_1920x1080.items()}

maps = {
    # Escort
    "Dorado": ["dorado", "dor", "ado", "rado", "orado", "orad"],
    "Junkertown": ["junkertown", "junker", "junkt", "town", "ertown", "unker"],
    "Rialto": ["rialto", "ial", "rial", "alto"],
    "Route 66": ["route", "route 66", "66"],
    "Watchpoint: Gibraltar": ["watchpoint", "watchpoint:", "gibraltar", "watchpoint: gibraltar", "watch", "gibra",
                              "gibralt", "gibral",
                              "point", "gibralta"],
    "Circuit Royal": ["circuit royal", "circuit", "royal"],
    "Havana": ["havana"],
    "Shambali Monastery": ["shambali monastery", "shambali", "shamba", "shambal", "monastery", "monast", "monas"],

    # Hybrid
    "Blizzard World": ["blizzard world", "blizzard", "world", "blizz", "blizzar", "blizza"],
    "Eichenwalde": ["eichenwalde", "eichen", "eich", "wald", "walde"],
    "Hollywood": ["hollywood", "holly", "wood"],
    "King's Row": ["king's row", "kings row", "king's", "kings", "row", "king"],
    "Numbani": ["numbani", "numb", "ani"],
    "Adlersbrunn": ["adlersbrunn", "adlers", "brunn"],
    "Paraiso": ["paraiso", "para", "iso"],
    "Midtown": ["midtown", "mid", "town"],

    # Control
    "Antarctic Peninsula": ["antarctic peninsula", "ant", "antar", "antarctic", "peninsula", "penin", "sula",
                            "arctic"],
    "Busan": ["busan", "bus", "busa", "downtown", "meka base", "meka", "base", "sanctuary"],
    "Ilios": ["ilios", "ili", "ios", "lighthouse", "house", "light", "well", "ruins"],
    "Lijiang Tower": ["lijiang tower", "lijiang", "tower", "lij", "jiang", "iang", "ijiang", "control", "center",
                      "control cent", "garden", "night market", "night", "market"],
    "Nepal": ["nepal", "village", "shrine", "sanctum"],
    "Oasis": ["oasis", "city center", "city", "gardens", "university"],
    "Samoa": ["samoa", "volcano", "beach"],

    # Push
    "Colosseo": ["colosseo", "colo", "sseo"],
    "Esperanca": ["esperanca", "esper", "anca"],
    "New Queen Street": ["new queen street", "new queen", "queen", "street"],

    # Flashpoint
    "New Junk City": ["new junk city", "new junk", "junk", "junk city", "city"],
    "Suravasa": ["suravasa", "sura", "vasa", "surava"],

    # Clash
    "Hanaoka": ["hanaoka", "hana", "oka"],
}


@app.route('/api/maps', methods=['GET'])
def get_maps():
    return jsonify(maps)


@app.route('/api/heroes/', methods=['GET'])
def get_all_heroes():
    heroes = [item for hero in [tanks, dps, supports] for values in hero.values() for item in values]
    return jsonify(heroes)


@app.route('/api/heroes/tanks', methods=['GET'])
def get_tank_heroes():
    return jsonify(tanks)


@app.route('/api/heroes/dps', methods=['GET'])
def get_dps_heroes():
    return jsonify(dps)


@app.route('/api/heroes/supports', methods=['GET'])
def get_support_heroes():
    return jsonify(supports)


@app.route('/api/heroes/coordinates_1920x1080', methods=['GET'])
def get_heroes_coordinates_1920x1080():
    return jsonify(heroes_coordinates_1920x1080)


@app.route('/api/heroes/coordinates_2560x1440', methods=['GET'])
def get_heroes_coordinates_2560x1440():
    return jsonify(heroes_coordinates_2560x1440)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
