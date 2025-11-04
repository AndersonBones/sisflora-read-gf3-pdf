
from modules.GF_Reader import GF_Reader
from modules.Utils import get_value_from_table


path = r"C:\Users\Anderson Bones\Desktop\Read GF\sisflora-read-gf3-pdf\src\docs\GFs\GF2.pdf"
gf_reader = GF_Reader(path)

doc = gf_reader.get_doc()
pages = gf_reader.get_pages_from_docs(doc)


lote = get_value_from_table(path, label="Lote")

print(lote)
