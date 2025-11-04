import re
import fitz
import numpy
from PIL import Image
import io
import pandas as pd
from tabula import read_pdf
import locale
import os

import validators
from spire.pdf import *
# qreader / pyzbar is optional: try to import, otherwise we'll use an OpenCV fallback
try:
    from qreader import QReader
    HAS_QREADER = True
except Exception:
    QReader = None
    HAS_QREADER = False

import cv2


def to_brl_currency(valor):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    valor = locale.currency(valor, grouping=True, symbol=None)
    return valor


def placa_validate(placa) -> bool:

    placa = placa.replace("-", "") # remove o traço

    if len(placa) == 7: # se possui 7 caracteres
        contLetra = 0
        contNum = 0

        for i, caractere in enumerate(placa): # laço pela string
            if caractere.isalpha() and (i == 0 or i == 1 or i == 2 or i == 4):
                contLetra += 1
            elif caractere.isdigit() and (i == 3 or i == 4 or i == 5 or i == 6):
                contNum += 1
            else:
                return False

        # identifica se a placa possui o padrão mercosul ou padrão antigo
        if (contLetra == 3 and contNum == 4) or (contLetra == 4 and contNum == 3):
            return True
                 
        else:
            return False
    else:
        return False


def get_codinate_from_pdf(path="", label="Memorial descritivo de transporte"):
    try:
        # Create a PdfDocument object
        doc = PdfDocument()

        # Load a PDF document
        doc.LoadFromFile(path)

        # Get a specific page
        page = doc.Pages[0]

        # Create a PdfTextFinder object
        textFinder = PdfTextFinder(page)

        # Search for the string "PRIVACY POLICY" within the page
        findResults = textFinder.Find(label)

        # Get the first instance of the results
        result = findResults[0]

        # Get X/Y coordinates of the found text
        x = int(result.Positions[0].X)
        y = int(result.Positions[0].Y)

        return {"x":x, "y":y}
    except:
        return {"x":0, "y":0}


def get_value_from_table(path="", label=""):

    cordinate_top_table = get_codinate_from_pdf(path, label="Espécies e seus correspondentes volumes")
    cordinate_bottom_table = get_codinate_from_pdf(path, label="Unidade") if get_codinate_from_pdf(path, label="Unidade")['y'] > 0 else get_codinate_from_pdf(path, label="Memorial descritivo de transporte")

    # localização das tabelas dos lotes na GF
    top_cordinate = cordinate_top_table['y']+10 # parte superior da tabela
    bottom_cordinate = cordinate_bottom_table['y'] # parte inferior da tabela


    table = read_pdf(
        path, pages="1",
        encoding="latin-1",
        area=[top_cordinate, 36.9, bottom_cordinate, 552.1],
        columns=[36.2, 180.6, 297.4, 360.9, 425.1, 496.3, 552.8]
    )[0]
    column = table[label].dropna()


    match label:

        case "Volume":
            column = column.str.replace(",", ".")
            column = column.astype(float).fillna(0.0).tolist()

            return sum(column)


        case "Preço Unitário":
            column = column.str.replace("R$", "")
            column = column.str.replace(",", ".", 1)
            column = column.astype(float).fillna(0.0).tolist()

            return sum(column) / len(column)

        case "Preço Total":

            column = column.str.replace(".", "")

            column = column.str.replace(",", ".")

            column = column.str.cat().split("R$")
            column.remove("")

            df = pd.DataFrame({label: column}).astype(float).fillna(0.0)

            df_list = df[label].to_list()

            return sum(df_list)

        case "Lote":

            lote_from_line = ""
            lotes_from_page=""

            
            for index in range(0, len(column.tolist())-1, 2):
                if len(column.tolist()) % 2 == 0:
                    lote_from_line = f"{column[index]+column[index+1]}| "
                else:
                    lote_from_line = f"|{column[index] + column[index + 1]} + {column[index + 2]} " 

                lotes_from_page+=lote_from_line
                lote_from_line = ""

            return lotes_from_page



        case "Essência":
            return column.str.cat(sep=" / ")


        case "Produto":
            return column.str.cat(sep=" / ")





def get_nome_remetente_ou__nome_destinatario(text):
    try:
        nome_label_position = re.search("Nome", text).end()
        cnpj_label_position = re.search("CNPJ/CPF", text).start()

        if text[nome_label_position:cnpj_label_position] is not None:
            return text[nome_label_position:cnpj_label_position].replace(",", "").strip()
    except:
        return ""
    


def get_cnpj_remetente_ou_cnpj_destinatario(text):
    try:
        cnpj_label_position = re.search("CNPJ/CPF n°", text).end()

        if text[cnpj_label_position:] is not None:
            return text[cnpj_label_position:].strip()
    except:
        return ""


def get_link_from_gf(file, index, from_image_file=False):
    try:
        pdf_file = fitz.open(file)
        page = pdf_file[-1] # get last page from pdf
        qr_code = page.get_images()[-1] # get last image (qr) from last page
        xref = qr_code[0]

        base_image = pdf_file.extract_image(xref)

        image_bytes = base_image["image"]
        image_ext = base_image["ext"]

        # Create a PIL Image object from the image bytes
        pil_image = Image.open(io.BytesIO(image_bytes))

        if pil_image.size[0] == 91 and pil_image.size[1] == 91:
            if from_image_file == True:
                image_path = create_temporary_files("images") + f"/image_{index}.{image_ext}"
                pil_image.save(image_path)
                return read_qr(image_path, from_image_file)

            else:
                return read_qr(pil_image, from_image_file)
    except:
        return None

def create_temporary_files(folder="images"):
    username = os.getenv('username')
    temp_dir = os.path.join(f"C:/Users/{username}/AppData/Local/Temp/", f"GF_Reader/{folder}")

    if os.path.exists(temp_dir) == False:
        os.mkdir(temp_dir)
        return temp_dir
    else:
        return temp_dir


def validade_url(url_string: str) -> bool:
    result = validators.url(url_string)
    return  result

def read_qr(file, from_image_file):
    # If qreader (pyzbar wrapper) is available use it; otherwise use OpenCV as fallback
    if HAS_QREADER:
        # Create a QReader instance
        qreader = QReader()

        if from_image_file == True:
            # Get the image that contains the QR code (cv2.imread returns BGR)
            image = cv2.imread(file)
        else:
            # Convert PIL Image or array-like to BGR for OpenCV
            image = numpy.array(file)
            # If image appears to be RGB (PIL -> numpy), convert to BGR
            if image.shape[-1] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Use the detect_and_decode function to get the decoded QR data
        decoded_text = qreader.detect_and_decode(image=image)

        if isinstance(decoded_text, (list, tuple)) and len(decoded_text) >= 1:
            return decoded_text[0]
        elif isinstance(decoded_text, str) and decoded_text:
            return decoded_text
        else:
            return None

    # Fallback using OpenCV's QRCodeDetector (no native zbar dependency)
    try:
        detector = cv2.QRCodeDetector()

        if from_image_file == True:
            img = cv2.imread(file)
        else:
            img = numpy.array(file)
            # convert RGB->BGR if needed
            if img is not None and img.ndim == 3 and img.shape[-1] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        if img is None:
            return None

        # Try multi decode first (OpenCV 4.7+), otherwise single decode
        if hasattr(detector, 'detectAndDecodeMulti'):
            ok, decoded_infos, points, straight_qrcodes = detector.detectAndDecodeMulti(img)
            if ok and decoded_infos:
                # return first non-empty result
                for d in decoded_infos:
                    if d:
                        return d
                return None
        # single
        data, points, _ = detector.detectAndDecode(img)
        if data:
            return data
        return None
    except Exception:
        return None


def date_validate(data):
    if re.match("^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}$", data):
        return True
    else:
        return False

def hour_validate(hour):
    if re.match("^([0-1][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$", hour):
        return True
    else:
        return False

def get_dataframe_from_dict(data:dict):
    try:
        return pd.DataFrame.from_dict(data, orient="index").transpose()
    except:
        return []

def export_to_excel(df:pd.DataFrame, output_path="", sheet_name="Sheet1"):
    try:
        df.to_excel(output_path, index=False, sheet_name=sheet_name, engine="xlsxwriter")
    except Exception as e:
        return e