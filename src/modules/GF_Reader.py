import pymupdf
import re
import os
import glob
from validate_docbr import CNPJ, CPF
from modules.Utils import get_value_from_table, placa_validate, get_link_from_gf, date_validate, hour_validate
from modules.Utils import get_nome_remetente_ou__nome_destinatario, get_cnpj_remetente_ou_cnpj_destinatario
from datetime import datetime

class GF_Reader:
    def __init__(self, gf_path) -> None:
        self.gf_title = "Guia Florestal para Transporte de Matéria Prima Florestal Diversa - GF3"
        self.gf_path = gf_path



        self.Gf = {
            "Guia de Transporte": [],
            "Chave de Acesso da NFe": [],
            "Protocolo": [],
            "Nome Remetente": [],
            "CNPJ/CPF Remetente": [],
            "Nome Destinatário": [],
            "CNPJ/CPF Destinatário": [],
            "Produto": [],
            "Volume": [],
            "Preço Unitário": [],
            "Preço Total": [],
            "Placa 1": [],
            "Placa 2": [],
            "Placa 3": [],
            "Placa 4": [],
            "Data de Emissão":[],
            "Hora de Emissão":[],
            "Data de Validade no Estado":[],
            "Hora de Validade no Estado":[],
            "Link de acesso Sema":[]
        }

    def read_table_from_pdf(self, label=""):
        try:
            values = []
            for gf_path in self.gfs_list_path:
                values.append(get_value_from_table(gf_path, label))

            return values
        except:
            return []


    def get_doc(self):
        
        try:
            return pymupdf.open(self.gf_path)
        except Exception as err:
            return None
        

    def get_pages_from_docs(self, doc):
        try:
            pages = []

            for pg in doc:
                text = pg.get_text()  # get plain text encoded as UTF-8
                if self.gf_title in text:
                    pages.append(text)

            return sorted(set(pages))

        except:
            return None
    

    def get_by_label(self, pages, label="Guia de Transporte"): # 

        try:
            guias_florestais = []
            for pg in pages:
                for line in pg.split("\n"):
                    data_label = re.search(label + ":", line)

                    if data_label is not None:
                        gf = line[data_label.end():].replace(" ", "")
                        guias_florestais.append(gf)
            
            guias_florestais = sorted(set(guias_florestais))
            
            if len(guias_florestais) == 1:
                return guias_florestais[0]

            if len(guias_florestais) > 1:
                return guias_florestais
            
            else:
                return None
                
        except:
            return None


    def get_datetime(self, page, label="Data de Emissão"):

        try:
            date = []
            hour = []

            if label == "Data de Emissão" or "Data de Validade no Estado":

                for pg in page:

                    for line in pg.split("\n"):
                        date_label = re.search(label + ":", line)

                        if date_label is not None:

                            date_time = line[date_label.end():].lstrip().split(" ")
                            
                            if date_validate(date_time[0]) == True:
                                date.append(date_time[0])

                            if hour_validate(date_time[1]) == True:
                                hour.append(date_time[1])

                date = sorted(set(date))
                hour = sorted(set(hour))

        
                if len(date) >= 1 or len(hour) >= 1:
                    return {
                        "Data Emissão":date[-1] + " " + hour[-1]
                    }
                 
                else:
                    return {
                        "Data Emissão":None
                    }

        except Exception as e:
            return None

 
        

    def get_placa(self, pages, label=""):
        
        placa1=''
        placa2=''
        placa3=''
        placa4=''

        for pg in pages:
            for line in pg.split("\n"):
                
                try:
                    placa1_match = re.search(r'Placa 1: +([A-Z]{3}[0-9][0-9A-Z][0-9]{2})', line)
                    
                    if placa1_match is not None and placa_validate(placa1_match.group().replace("Placa 1:", "").strip()) == True:
                        placa1 = placa1_match.group().replace("Placa 1:", "").strip()
                except Exception as e:
                    placa1 = ''
                

                try:
                    placa2_match = re.search(r'Placa 2: +([A-Z]{3}[0-9][0-9A-Z][0-9]{2})', line)
                    
                    if placa2_match is not None:
                        placa2 = placa2_match.group().replace("Placa 2:", "").strip()
                except Exception as e:
                    placa2 = ''
                

                try:
                    placa3_match = re.search(r'Placa 3: +([A-Z]{3}[0-9][0-9A-Z][0-9]{2})', line)
                    
                    if placa3_match is not None:
                        placa3 = placa3_match.group().replace("Placa 3:", "").strip()
                except Exception as e:
                    placa3 = ''
                

                try:
                    placa4_match = re.search(r'Placa 4: +([A-Z]{3}[0-9][0-9A-Z][0-9]{2})', line)
                    
                    if placa4_match is not None:
                        placa4 = placa4_match.group().replace("Placa 4:", "").strip()
                except Exception as e:
                    placa4 = ''


            return {
                "Placa 1":placa1,
                "Placa 2":placa2,
                "Placa 3":placa3,
                "Placa 4":placa4
            }




    def get_remetente_ou_destinatario(self, page, option= "Remetente" or "Destinatário"):

        self.cnpj = CNPJ()
        self.cpf = CPF()

        if option == "Remetente":
            cnpj_cpf_list = []
            nome_remetente = []

            data = {
                "Cnpj_Cpf": '',
                "Remetente": ''
            }

            try:
               
                for pg in page:
                    remetente = re.search(option + ":", pg)
                    ie = re.search("Inscrição Estadual", pg)

                    if remetente is not None and ie is not None:
                        if (self.cnpj.validate(get_cnpj_remetente_ou_cnpj_destinatario(pg[remetente.end(): ie.start()])) == True or
                                self.cpf.validate(get_cnpj_remetente_ou_cnpj_destinatario(pg[remetente.end(): ie.start()])) == True):

                            cnpj_cpf_list.append(get_cnpj_remetente_ou_cnpj_destinatario(pg[remetente.end(): ie.start()]))

                        nome_remetente.append(get_nome_remetente_ou__nome_destinatario(pg[remetente.end(): ie.start()]))

                data["Remetente"] = sorted(set(nome_remetente))[-1]
                data["Cnpj_Cpf"] = sorted(set(cnpj_cpf_list))[-1]

                return data
            except:

                return {
                "Cnpj_Cpf": '',
                "Remetente": ''
            }


        if option == "Destinatário":
            cnpj_cpf_list = []
            nome_destinatario = []

            data = {
                "Cnpj_Cpf": [],
                "Destinatário": []
            }

            try:
                for pg in page:
                    destinatario_area = re.search(option + ":", pg)

                    if destinatario_area is not None:
                        destinatario_area_after_laber = pg[destinatario_area.end():]

                        ie = re.search("Inscrição Estadual", destinatario_area_after_laber)

                    if destinatario_area is not None and ie is not None:
                        if (self.cnpj.validate(get_cnpj_remetente_ou_cnpj_destinatario(destinatario_area_after_laber[: ie.start()])) == True or
                                self.cpf.validate(get_cnpj_remetente_ou_cnpj_destinatario(destinatario_area_after_laber[: ie.start()])) == True):

                            cnpj_cpf_list.append(get_cnpj_remetente_ou_cnpj_destinatario(destinatario_area_after_laber[: ie.start()]))

                        nome_destinatario.append(get_nome_remetente_ou__nome_destinatario(destinatario_area_after_laber[: ie.start()]))

                data["Destinatário"] = sorted(set(nome_destinatario))[-1]
                data["Cnpj_Cpf"] = sorted(set(cnpj_cpf_list))[-1]

                return data
            except Exception as e:
                return {
                    "Cnpj_Cpf": '',
                    "Destinatário": ''
                }
        
        else:
           {
               "Cnpj_Cpf": '',
                "Destinatário": ''
           }


    def get_gf_link(self):
        links = []
        for index, file in enumerate(self.gfs_list_path, start=0):
            links.append(get_link_from_gf(file, index, from_image_file=False))
        return links


    def get_values(self,links_sema=False, lote=False, produto=False, essencia=False, placa=False):
        docs = self.get_docs()
        pages = self.get_pages_from_docs(docs)

        try:
            data_emissao = self.get_datetime(pages, label="Data de Emissão")
            data_validade = self.get_datetime(pages, label="Data de Validade no Estado")

            remetente = self.get_remetente_ou_destinatario(pages, option="Remetente")
            destinatario = self.get_remetente_ou_destinatario(pages, option="Destinatário")


            self.Gf["Guia de Transporte"] = self.get_by_label(pages, label="Guia de Transporte")
            self.Gf["Chave de Acesso da NFe"] = self.get_by_label(pages, label="Chave de Acesso da NFe")
            self.Gf["Protocolo"] = self.get_by_label(pages, label="Protocolo")
            self.Gf["Nome Remetente"] = remetente["remetente"]
            self.Gf["CNPJ/CPF Remetente"] = remetente["cnpj_cpf"]
            self.Gf["Nome Destinatário"] = destinatario["destinatário"]
            self.Gf["CNPJ/CPF Destinatário"] = destinatario["cnpj_cpf"]
            self.Gf["Data de Emissão"] = data_emissao['data']
            self.Gf["Hora de Emissão"] = data_emissao['hora']
            self.Gf["Data de Validade no Estado"] = data_validade["data"]
            self.Gf["Hora de Validade no Estado"] = data_validade["hora"]

            self.Gf['Volume'] = self.read_table_from_pdf(label="Volume")
            self.Gf['Preço Unitário'] = self.read_table_from_pdf(label="Preço Unitário")
            self.Gf['Preço Total'] = self.read_table_from_pdf(label="Preço Total")

            if links_sema == True:
                self.Gf['Link de acesso Sema'] = self.get_gf_link()

            if placa == True:
                self.Gf['Placa 1'] = self.get_placa(pages, "Placa 1")
                self.Gf['Placa 2'] = self.get_placa(pages, "Placa 2")
                self.Gf['Placa 3'] = self.get_placa(pages, "Placa 3")
                self.Gf['Placa 4'] = self.get_placa(pages, "Placa 4")

            if essencia == True:
                self.Gf["Essência"] = self.read_table_from_pdf(label="Essência")
            if produto == True:
                self.Gf["Produto"] = self.read_table_from_pdf(label="Produto")
            if lote == True:
                self.Gf["Lote"] = self.read_table_from_pdf(label="Lote")


            return self.Gf
        except:

            return {"null":[]}


