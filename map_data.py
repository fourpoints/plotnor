import xml.etree.ElementTree as ET
from connector import connect_paths
from itermore import pairwise

### Kartverket XML data

# metadata
#http://sosi.geonorge.no/Produktspesifikasjoner/Produktspesifikasjon_Kartverket_N50Kartdata_versjon20170401.pdf
#https://kartkatalog.geonorge.no/metadata/kartverket/n5000-kartdata/c777d53d-8916-4d9d-bae4-6d5140e0c569

# data files
area_file = "data/Basisdata_0000_Norge_25833_N5000Arealdekke_GML.gml"
admt_file = "data/Basisdata_0000_Norge_25833_N5000AdministrativeOmrader_GML.gml"

namespaces = {
    "gts" : "http://www.isotc211.org/2005/gts",
    "gsr" : "http://www.isotc211.org/2005/gsr",
    "gss" : "http://www.isotc211.org/2005/gss",
    "gmd" : "http://www.isotc211.org/2005/gmd",
    "app" : "http://skjema.geonorge.no/SOSI/produktspesifikasjon/N5000/20170701/",
    "sc" : "http://www.interactive-instruments.de/ShapeChange/AppInfo",
    "xlink" : "http://www.w3.org/1999/xlink",
    "gco" : "http://www.isotc211.org/2005/gco",
    "gml" : "http://www.opengis.net/gml/3.2",
    "id" : "id1d310479-3093-46ff-b1d1-665693382364",
}

### Coastal and island border

area_tree = ET.parse(area_file)
area_root = area_tree.getroot()

admt_tree = ET.parse(admt_file)
admt_root = admt_tree.getroot()

coast_xpath = '/'.join((
    "gml:featureMember",
    "app:Kystkontur",
    "app:grense",
    "gml:LineString",
    "gml:posList",
))

border_xpath = '/'.join((
    "gml:featureMember",
    "app:Riksgrense",
    "app:grense",
    "gml:LineString",
    "gml:posList",
))

# - connected_coast contains the islands
# - disconnected_coast contains the sea-land border
connected_coast, disconnected_coast =\
    connect_paths(area_root, coast_xpath, namespaces)

# - connected_border is empty
# - disconnected_border contains the NOR-SWE border
connected_border, disconnected_border =\
    connect_paths(admt_root, border_xpath, namespaces)

# Connect coastline with the NOR-SWE border
disconnected_border[0].reverse() # correct orientation
inland_border = list(disconnected_coast[0]) + list(disconnected_border[0])[:-1]

# Combine the island and the inland_border
land_borders = connected_coast.copy()
land_borders.add(tuple(inland_border))


### Kommune areas

kommune_xpath = '/'.join(("gml:featureMember", "app:Kommune"))
kommune_area_xpath = '/'.join((
    "app:område",
    "gml:Surface",
    "gml:patches",
    "gml:PolygonPatch",
    "gml:exterior",
    "gml:LinearRing",
    "gml:posList",
))
kommune_name_xpath = '/'.join((
    "app:navn",
    "app:AdministrativEnhetNavn",
    "app:navn"
))
kommune_number_xpath = "app:kommunenummer"

kommunes = dict()
for kommune in admt_root.iterfind(kommune_xpath, namespaces=namespaces):
    # Name of the kommune
    kommune_name = kommune.find(kommune_name_xpath, namespaces=namespaces).text
    kommune_id = kommune.find(kommune_number_xpath, namespaces=namespaces).text
    kommune_pts = kommune.find(kommune_area_xpath, namespaces=namespaces).text

    kommune_loop = list(pairwise(map(float, kommune_pts.split())))

    kommunes[kommune_id] = kommune_loop
