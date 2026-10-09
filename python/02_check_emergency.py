import xml.etree.ElementTree as ET

path = "data/raw/emergency.xml"
root = ET.parse(path).getroot()

rows = root.find(".//rows")
if rows is None:
    print("No <rows> element found. Root:", root.tag)
else:
    print("Emergency records:", len(rows.findall("row")))
    if len(rows):
        print("First row fields:", [child.tag for child in rows[0]])
