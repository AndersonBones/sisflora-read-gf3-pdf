from Utils import get_codinate_from_pdf
from tabula import read_pdf
import pypdf

path = r"C:\Users\anderson.ebones\Desktop\Py\sisflora-read-gf3-pdf\src\docs\dof.pdf"

reader = pypdf.PdfReader(open(path, mode='rb' ))
n = reader.get_num_pages()

print(n)

pages = get_codinate_from_pdf(path, label="DETALHAMENTO DOS PRODUTOS TRANSPORTADOS", num_pages=n)


table = read_pdf(
        path, pages=n,
        encoding="latin-1",
        area=[220, 64, 775, 553],
)

col = table[1].dropna()

print(col)
print(col.iat[1, 1])