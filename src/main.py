
from modules.GF_Reader import GF_Reader
from modules.Utils import get_value_from_table, get_tipo_lote
import glob, os
import shutil
import pandas as pd
from threading import Thread
import time




def run_read_pdf(path="", file_name=""):
 
    data_emissao = []
    essencias = []
    lotes = []
    tipo_lote = []
    rem_cnpj = []
    rem_nome = []
    dest_cnpj = []
    dest_nome = []
    num_gf = []
    qtde_gf = []
    chaves = []
    nf = []
    i = 0
    
    start_time = time.time()

    # Usa caminhos absolutos em vez de mudar diretório
    for file in glob.glob(os.path.join(path, "*.pdf")):
        i+=1   
        
        gf_reader = GF_Reader(file)
        doc = gf_reader.get_doc()
        pages = gf_reader.get_pages_from_docs(doc)

        gf = gf_reader.get_by_label(pages, "Guia de Transporte")
        num_gf.append(gf)

        data_emissao.append(gf_reader.get_datetime(pages,"Data de Emissão")["Data Emissão"])
        rem_cnpj.append(gf_reader.get_remetente_ou_destinatario(pages,"Remetente")["cnpj_cpf"])
        dest_cnpj.append(gf_reader.get_remetente_ou_destinatario(pages,"Destinatário")["cnpj_cpf"])
        rem_nome.append(gf_reader.get_remetente_ou_destinatario(pages,"Remetente")["remetente"])
        dest_nome.append(gf_reader.get_remetente_ou_destinatario(pages,"Destinatário")["destinatário"])

        chave_nf = gf_reader.get_by_label(pages, "Chave de Acesso da NFe")
        chaves.append(chave_nf) 
        nf.append(chave_nf[25:34])  # Extrai o número da NF da chave de acesso

        lote = get_value_from_table(file, label="Lote")
        essencia = get_value_from_table(file, label="Essência")
        qtde = get_value_from_table(file, label="Volume")
        qtde_gf.append(qtde)


        lotes.append(lote)
        essencias.append(essencia)

        tipo_lote.append(get_tipo_lote(lote))
        

        print(f"Pasta: {os.path.basename(path)} - Index: {i} - File: {os.path.basename(file)} - N° GF:{gf} Lote: {lote.split('#')} - Volume: {qtde.split('#')}")
     
        doc.close()

   
    
    data = {
            "N° NF":nf,
            "Chave NFe":chaves,
            'N° GF':num_gf,
            "Data Emissão":data_emissao,
            'Nome Remetente': rem_nome,
            'CNPJ Remetente': rem_cnpj,
             'Nome Destinatário': dest_nome,
             'CNPJ Destinatário':dest_cnpj,
            "Tipo Lote":tipo_lote,
            "Volume":qtde_gf
            }
    df = pd.DataFrame(data)


    df.to_excel(fr"{file_name}", index=False, engine="xlsxwriter")

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Print the execution time
    print(f"Execution time: {elapsed_time:.4f} seconds")



# path1 = r"C:\Users\anderson.ebones\Desktop\Py\2025\SRS - OK\06 - OK"
path2 = r"F:\BIOMASSA\03. Originação\06. Guias Florestais\2024 - OK\SRS - OK\10 - OK"

# Cria as dois threads
# thr1 = Thread(target=run_read_pdf, args=[path1, "srs_06_2025.xlsx"])
thr2 = Thread(target=run_read_pdf, args=[path2, "srs_10_2024.xlsx"])


# Inicia as dois threads
# thr1.start()
thr2.start()

# Espera todas terminarem
# thr1.join()
thr2.join()

   