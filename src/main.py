
from modules.GF_Reader import GF_Reader
from modules.Utils import get_value_from_table
import glob, os

path = r"C:\Users\Anderson Bones\Desktop\Read GF\sisflora-read-gf3-pdf\src\docs\GFs"
gf_reader = GF_Reader(path)

doc = gf_reader.get_doc()
pages = gf_reader.get_pages_from_docs(doc)





os.chdir(path)
pdfs = []
for file in glob.glob("*.pdf"):
       
    lote = get_value_from_table(file, label="Lote")
    print(f"{file} - {lote}")
    pdfs.append(lote)
    

print(len(pdfs))




