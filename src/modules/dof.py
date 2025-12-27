import re
from PyPDF2 import PdfReader
import os, glob
import pandas as pd

def limpar_nome(texto: str) -> str:
    # Junta quebras de linha e múltiplos espaços
    return re.sub(r"\s+", " ", texto).strip()


def parse_numero_br(numero_str: str) -> float:
    """
    Converte '35,0000' ou '1.234,56' para float (35.0, 1234.56).
    """
    numero_str = numero_str.replace(".", "").replace(",", ".")
    return numero_str

def extrair_nf(chave_acesso: str) -> str:
    """
    Extrai o número da NF da chave de acesso (posições 26 a 34).
    Exemplo: '35190512345678000123550010000012345678901234' -> '000100000'
    """
    return chave_acesso[25:34]


def extrair_dof(pdf_path: str) -> dict:
    reader = PdfReader(pdf_path)

    # Junta texto de todas as páginas
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() or ""

    
    # -- DATA DE EMISSÃO ---
    
    date_match = re.search(r"Emissão ocorrida em  às . \s*(\d{2}/\d{2}/\d{4})", texto)

    
    # --- NÚMERO DO DOF ---
    num_dof_match = re.search(r"Nº DE SÉRIE:\s*(\d+)", texto, re.S)

    # -- Chave de acesso

    num_chave_match = re.search(r"Nº do Documento Fiscal:\s*((?:\d[\s\r\n]*){44})", texto, re.S)

    num_chave_match = num_chave_match.group(1).replace("\n","").replace(" ","")


    # --- REMETENTE ---
    rem_match = re.search(
        r"REMETENTE\s+Nome:\s*(.+?)CPF/CNPJ:\s*([\d\.\-\/]+)",
        texto,
        re.S
    )

   

    remetente = {
        "nfe":extrair_nf(num_chave_match) if num_chave_match else None,
        "chave":num_chave_match,
        "dof":num_dof_match.group(1) if num_dof_match else None,
        "data_emissao": date_match.group(1) if date_match else None,
        "nome": limpar_nome(rem_match.group(1)) if rem_match else None,
        "cnpj": rem_match.group(2) if rem_match else None,
    }

    
    
    # --- DESTINATÁRIO ---
    dest_match = re.search(
        r"DESTINATÁRIO\s+Nome:\s*(.+?)CPF/CNPJ:\s*([\d\.\-\/]+)",
        texto,
        re.S
    )


    destinatario = {
        "nome": limpar_nome(dest_match.group(1)) if dest_match else None,
        "cnpj": dest_match.group(2) if dest_match else None,
    }

    # --- ITENS: CÓDIGO DE RASTREIO + QUANTIDADE ---
    # Ex.: "PÁTIO-2015.2.2020.273453 35,0000"
    itens = []
    for codigo, quantidade_str in re.findall(
        r"([A-Za-zÀ-ÖØ-öø-ÿ]+-\d[\d\.]+)\s+(\d+,\d+)", texto
    ):
     
        itens.append(
            {
                "codigo_rastreio": codigo,
                "quantidade_m3": quantidade_str,
                "quantidade_str": quantidade_str,  # mantém o texto original se quiser
            }
        )

    return {
    
        "remetente": remetente,
        "destinatario": destinatario,
        "itens": itens,
    }


if __name__ == "__main__":

    data_emissao = []
    rem_dof = []
    rem_cnpj = []
    rem_nome = []
    dest_cnpj = []
    dest_nome = []
    cod_rastreio = []
    volume = []
    rem_chave = []
    rem_nf = []
    
    caminho_pdf = r"F:\BIOMASSA\03. Originação\06. Guias Florestais\DOFs - PARÁ\2025\12"  # ajuste o caminho se necessário
    for file in glob.glob(os.path.join(caminho_pdf, "*.pdf")):
        
        info = extrair_dof(file)

        # print("Remetente:")

        # print(f"  NFe: {info['remetente']['nfe']}")
        # print(f"  Chave: {info['remetente']['chave']}")
        # print(f"  Dof: {info['remetente']['dof']}")
        # print(f"  Data Emissão: {info['remetente']['data_emissao']}")

        # print(f"  Nome: {info['remetente']['nome']}")
        # print(f"  CNPJ: {info['remetente']['cnpj']}")
        # print("\nDestinatário:")
        # print(f"  Nome: {info['destinatario']['nome']}")
        # print(f"  CNPJ: {info['destinatario']['cnpj']}")

        # print("\nItens (código de rastreio / quantidade m³):")

        cod_rastreio_row = []
        volume_row = []
        for item in info["itens"]:
                print(f"  Código: {item['codigo_rastreio']}  |  "f"Qtd (m³): {item['quantidade_m3']} (texto: {item['quantidade_str']})")
                
                item['codigo_rastreio'] = re.sub(r'[^A-Za-zÀ-ÿ]', '', item['codigo_rastreio'])
                cod_rastreio_row.append(item['codigo_rastreio'])
               
                volume_row.append(item['quantidade_m3'])
                


        cod_rastreio.append("#".join(cod_rastreio_row))
        volume.append("#".join(volume_row))
        
        data_emissao.append(info['remetente']['data_emissao'])
        rem_nf.append(info['remetente']['nfe'])
        rem_chave.append(info['remetente']['chave'])
        rem_dof.append(info['remetente']['dof'])
        rem_nome.append(info['remetente']['nome'])
        rem_cnpj.append(info['remetente']['cnpj'])
        dest_nome.append(info['destinatario']['nome'])
        dest_cnpj.append(info['destinatario']['cnpj'])

        cod_rastreio_row.clear()
        volume_row.clear()


        
    data = {
        "NFe":rem_nf,
        "Chave NFe":rem_chave,
        "Dof":rem_dof,
        "Data Emissão":data_emissao,
        "Nome Remetente":rem_nome,
        "CNPJ Rementente":rem_cnpj,
        "Nome Destinatário":dest_nome,
        "CNPJ Destinatário":dest_cnpj,
        "Origem":cod_rastreio,
        "Volume":volume
     }

df = pd.DataFrame(data)
df.to_excel("2025_12_para.xlsx", index=False, engine="xlsxwriter")    
      