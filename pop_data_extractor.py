import csv
from collections import namedtuple

csv.register_dialect('ssb-csv', delimiter=';', quoting=csv.QUOTE_NONE)
pop_triple = namedtuple('pop_triple', ['y2017', 'y2018', 'inc'])

# https://www.ssb.no/befolkning/statistikker/folkemengde/aar-per-1-januar
pop_file = "data/befolkning.csv"

with open(pop_file, mode='r') as f:
    reader = csv.reader(f, dialect="ssb-csv")
    for _ in range(5): next(reader) # The first five rows are the header.

    pop_data = dict()

    # Example row; | indicates separator
    # 01 Østfold | 292 893 | 295 420 | 0,9 |

    for (kommune, pop2017, pop2018, inc, _) in reader: # last cell is empty
        if not kommune: continue # some rows are empty; we skip these

        # change number format
        inc = inc.replace(',', '.')

        # nan are listed as . in the data set
        if inc == '.': inc = 'nan'

        # a kommune cell consists of an id and a name
        kommune_id, kommune_name = kommune.split(maxsplit=1)

        # finally, we add these to the population dictionary
        pop_data[kommune_id] =\
            pop_triple(int(pop2017), int(pop2018), float(inc))


# New kommune-numbering for merged kommunes
merged_kommune_ids = {
    "0712" : ("0709", "0728"),
    "0715" : ("0702", "0714"),
    "0729" : ("0722", "0723"),
    "5054" : ("1624", "1718"),
}

# New kommune-numbering for Trøndelag kommunes
troendelag_kommune_ids = {
    "5001" : "1601",
    "5004" : "1702",
    "5005" : "1703",
    "5011" : "1612",
    "5012" : "1613",
    "5013" : "1617",
    "5014" : "1620",
    "5015" : "1621",
    "5016" : "1622",
    "5017" : "1627",
    "5018" : "1630",
    "5019" : "1632",
    "5020" : "1633",
    "5021" : "1634",
    "5022" : "1635",
    "5023" : "1636",
    "5024" : "1638",
    "5025" : "1640",
    "5026" : "1644",
    "5027" : "1648",
    "5028" : "1653",
    "5029" : "1657",
    "5030" : "1662",
    "5031" : "1663",
    "5032" : "1664",
    "5033" : "1665",
    "5034" : "1711",
    "5035" : "1714",
    "5036" : "1717",
    "5037" : "1719",
    "5038" : "1721",
    "5039" : "1724",
    "5040" : "1725",
    "5041" : "1736",
    "5042" : "1738",
    "5043" : "1739",
    "5044" : "1740",
    "5045" : "1742",
    "5046" : "1743",
    "5047" : "1744",
    "5048" : "1748",
    "5049" : "1749",
    "5050" : "1750",
    "5051" : "1751",
    "5052" : "1755",
    "5053" : "1756",
}

# Kommunesammenslåing-fix
for new, (old1, old2) in merged_kommune_ids.items():
    oldpop = pop_data[old1].y2017 + pop_data[old2].y2017
    
    pop_data[new] = pop_triple(
        oldpop,
        pop_data[new].y2018,
        (oldpop - pop_data[new].y2018) / oldpop*100
    )

# Trøndelag-fix
for new, old in troendelag_kommune_ids.items():
    pop_data[new] = pop_triple(
        pop_data[old].y2017,
        pop_data[new].y2018,
        (pop_data[old].y2017 - pop_data[new].y2018) / pop_data[old].y2017*100
    )
