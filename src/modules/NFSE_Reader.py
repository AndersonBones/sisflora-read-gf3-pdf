import pymupdf
from tabula import read_pdf
import os
import glob
import fitz
from validate_docbr import CNPJ, CPF

from modules.Utils import date_validate

path = r"C:\Users\anderson.bones\Desktop\Projetos\Python\sisflora-read-gf3-pdf\src\docs\Notas"



class NFSE_Reader():
    def __init__(self, nfse_path):
        self.nfse_path = nfse_path
        os.chdir(self.nfse_path)
        self.nfes_path_list = glob.glob('*.pdf')
        self.NFSe = {
            "Número da nota fiscal":[],
            "Data de Emissão":[],

        }

    def get_nfse_num(self):
        num_nota_cordinate = [23, 500, 52.2, 578]
        num_notas=[]
        for nfse_path in self.nfes_path_list:
            table = read_pdf(nfse_path, pages="1",encoding="utf-8",area=num_nota_cordinate)[0].dropna()
            num_nota = table.iat[0, 0]

            num_notas.append(num_nota)

        return num_notas

    def get_data_emissao(self):
        data_emissao_nota_cordinate = [51.4, 422.4, 80.7, 578]
        datetime = []

        for nfse_path in self.nfes_path_list:
            table = read_pdf(nfse_path, pages="1", encoding="utf-8", area=data_emissao_nota_cordinate)[0].dropna()
            datetime_from_nfse = table.iat[0, 0]

            datetime.append(datetime_from_nfse)

        return datetime

    def get_prestador(self):

        nome_prestador_cordinate = [149.8, 169.6, 423.1, 182]
        cnpj_prestador_cordinate = [119.4, 182, 200.8, 194]

        prestador = {
            "nome_prestador":[],
            "cnpj_prestador":[]
        }

        cnpj = CNPJ()

        for nfse_path in self.nfes_path_list:
            try:
                document = fitz.open(nfse_path)

                page = document[0]

                rect_nome = fitz.Rect(
                    nome_prestador_cordinate[0],
                    nome_prestador_cordinate[1],
                    nome_prestador_cordinate[2],
                    nome_prestador_cordinate[3]
                )
                rect_cpnpj_cpf = fitz.Rect(
                    cnpj_prestador_cordinate[0],
                    cnpj_prestador_cordinate[1],
                    cnpj_prestador_cordinate[2],
                    cnpj_prestador_cordinate[3]
                )
                nome = page.get_text("text", clip=rect_nome)
                cnpj_cpf = page.get_text("text", clip=rect_cpnpj_cpf)

                prestador['nome_prestador'].append(nome.strip())

                if cnpj.validate(cnpj_cpf.strip()) == True:
                    prestador['cnpj_prestador'].append(cnpj_cpf.strip())

            except Exception as e:
                return e

        return prestador


    def get_tomador(self):

        nome_tomador_cordinate = [90.3, 273.3, 364.5, 285.9]
        cnpj_tomador_cordinate = [59.1, 286.5, 162.9, 297.3]

        tomador = {
            "nome_tomador":[],
            "cnpj_tomador":[]
        }

        cnpj = CNPJ()

        for nfse_path in self.nfes_path_list:
            try:
                document = fitz.open(nfse_path)

                page = document[0]

                rect_nome = fitz.Rect(
                    nome_tomador_cordinate[0],
                    nome_tomador_cordinate[1],
                    nome_tomador_cordinate[2],
                    nome_tomador_cordinate[3]
                )
                rect_cpnpj_cpf = fitz.Rect(
                    cnpj_tomador_cordinate[0],
                    cnpj_tomador_cordinate[1],
                    cnpj_tomador_cordinate[2],
                    cnpj_tomador_cordinate[3]
                )
                nome = page.get_text("text", clip=rect_nome)
                cnpj_cpf = page.get_text("text", clip=rect_cpnpj_cpf)

                tomador['nome_tomador'].append(nome.strip())

                if cnpj.validate(cnpj_cpf.strip()) == True:
                    tomador['cnpj_tomador'].append(cnpj_cpf.strip())

            except Exception as e:
                return e

        return tomador


    def get_discriminacao_servicos(self):
        servicos_cordinate = [369, 16.4, 406, 578.5]
        columns_cordinate = [258.3, 335.7, 387.9, 453.3, 540.3, 578]

        servicos = {
            "Valor unitário":[],
            "Qtd":[],
            "Valor do serviço":[],
            "Base de cálculo":[],
            "ISS":[],
        }

        for nfse_path in self.nfes_path_list:

            try:
                table = read_pdf(
                    nfse_path, pages="1",
                    encoding="utf-8",
                    area=servicos_cordinate,
                    columns=columns_cordinate
                )[0].dropna(axis="columns")

                valor_un = table['Valor unitário'].values[0].replace('.', '')
                valor_un = valor_un.replace(",", ".")
                servicos['Valor unitário'].append(float(valor_un))

                valor_servico = table['Valor do serviço'].values[0].replace('.', '')
                valor_servico = valor_servico.replace(",", ".")
                servicos['Valor do serviço'].append(float(valor_servico))

                valor_iss = table['ISS'].values[0].replace('.', '')
                valor_iss = valor_iss.replace(",", ".")
                servicos['ISS'].append(float(valor_iss))

                qtde = table['Qtd'].values[0].replace('.', '')
                qtde = qtde.replace(",", ".")
                servicos['Qtd'].append(float(qtde))

                base_calculo = table['Base de cálculo (%)'].values[0].replace('.', '')
                base_calculo = base_calculo.replace(",", ".")
                base_calculo = base_calculo.replace("=", "")
                servicos['Base de cálculo'].append(base_calculo.strip())

            except Exception as e:
                return e

        return servicos


    def get_forma_pagamento(self):
        table_cordinate = [424, 16.4, 460.1, 578.5]
        columns_cordinate = [16.4, 56, 102.3, 146.1, 213.3 ]

        forma_pagamento = {
            "Parcela": [],
            "Vencimento": [],
            "Tipo": [],
            "Valor": [],
        }

        try:
            for nfse_path in self.nfes_path_list:
                table = read_pdf(
                    nfse_path,
                    pages="1",
                    encoding="utf-8",
                    area=table_cordinate,
                    columns=columns_cordinate
                )[0].dropna(axis="columns")

                data_vencimento = table['Vencimento'].values[0]

                if date_validate(data_vencimento) == True:
                    forma_pagamento['Vencimento'].append(data_vencimento)

                forma_pagamento['Parcela'].append(table['Parcela'].values[0])

                forma_pagamento['Tipo'].append(table['Tipo'].values[0])

                valor_liq = table['Valor (R$)'].values[0].replace('.', '')
                valor_liq = valor_liq.replace(",", ".")
                forma_pagamento['Valor'].append(float(valor_liq))
                
        except Exception as e:
            return e

        return forma_pagamento


    def get_retencoes_federais(self):
        table_cordinate = [472.2, 16.4, 509.5, 578.5]
        columns_cordinate = [16.4, 111.2, 205.3, 300, 394.8, 490.2,578.5]

        impostos = {
            "PIS/PASEP": [],
            "COFINS": [],
            "INSS": [],
            "IR": [],
            "CSLL":[],
            "Outras retenções":[]
        }

        try:
            for nfse_path in self.nfes_path_list:
                table = read_pdf(
                    nfse_path,
                    pages="1",
                    encoding="utf-8",
                    area=table_cordinate,
                    columns=columns_cordinate
                )[0].dropna(axis="columns")


                pis = table['PIS/PASEP'].values[0].replace(".", '')
                pis = pis.replace(",", ".")
                impostos['PIS/PASEP'].append(float(pis))

                cofins = table['COFINS'].values[0].replace(".", '')
                cofins = cofins.replace(",", ".")
                impostos['COFINS'].append(float(cofins))

                inss = table['INSS'].values[0].replace(".", '')
                inss = inss.replace(",", ".")
                impostos['INSS'].append(float(inss))

                ir = table['IR'].values[0].replace(".", '')
                ir = ir.replace(",", ".")
                impostos['IR'].append(float(ir))

                csll = table['CSLL'].values[0].replace(".", '')
                csll = csll.replace(",", ".")
                impostos['CSLL'].append(float(csll))

                outros = table['Outras retenções'].values[0].replace(".", '')
                outros = outros.replace(",", ".")
                impostos['Outras retenções'].append(float(outros))

        except Exception as e:
            return e

        return impostos

    def get_valor_bruto(self):
        valor_bruto_cordinate = [16.4, 509.5, 205.3, 526.3]
        Valor_Bruto = []

        for nfse_path in self.nfes_path_list:
            try:
                document = fitz.open(nfse_path)

                page = document[0]

                rect = fitz.Rect(
                    valor_bruto_cordinate[0],
                    valor_bruto_cordinate[1],
                    valor_bruto_cordinate[2],
                    valor_bruto_cordinate[3]
                )

                valor_bruto = page.get_text("text", clip=rect).split("=")[-1]
                valor_bruto = valor_bruto.replace("R$", "")

                valor_bruto = valor_bruto.replace(".","")
                valor_bruto = valor_bruto.replace(",", ".")


                Valor_Bruto.append(float(valor_bruto))

            except Exception as e:
                return e

        return Valor_Bruto


    def get_valor_liquido(self):
        valor_liquido_cordinate = [205.3, 509.5, 395.4, 526.3]
        valor_liquido = []

        for nfse_path in self.nfes_path_list:
            try:
                document = fitz.open(nfse_path)

                page = document[0]

                rect = fitz.Rect(
                    valor_liquido_cordinate[0],
                    valor_liquido_cordinate[1],
                    valor_liquido_cordinate[2],
                    valor_liquido_cordinate[3]
                )

                valor = page.get_text("text", clip=rect).split("=")[-1]
                valor = valor.replace("R$", "")

                valor = valor.replace(".","")
                valor = valor.replace(",", ".")


                valor_liquido.append(float(valor))

            except Exception as e:
                return e

        return valor_liquido



    def get_docs(self):
        try:
            docs = []
            for nfse_path in self.nfes_path_list:

                docs.append(pymupdf.open(nfse_path))
            return docs
        except:
            return []

    def get_pages_from_docs(self, docs):
        try:
            pages = []
            page = []

            for doc in docs:  # iterate the document pages
                for pg in doc:
                    text = pg.get_text()  # get plain text encoded as UTF-8

                    page.append(text)
                pages.append(sorted(set(page.copy())))
                page.clear()

            return pages

        except:
            return []


nfse = NFSE_Reader(path)


print(nfse.get_valor_bruto())
print(nfse.get_valor_liquido())