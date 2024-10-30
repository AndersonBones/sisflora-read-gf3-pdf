
from modules.GF_Reader import GF_Reader
from modules.Utils import get_dataframe_from_dict, export_to_excel

gf_reader = GF_Reader(r"F:\Programing Projects\Python\sisflora-read-gf3-pdf\src\docs\GFs\Gf Teste.pdf")

doc = gf_reader.get_doc()
pages = gf_reader.get_pages_from_docs(doc)



gf = gf_reader.get_by_label(pages, label="Guia de Transporte")

print(gf)


datetime = gf_reader.get_datetime(pages, label="Data de Validade no Estado")

print(datetime)

placa = gf_reader.get_placa(pages)

print(placa)