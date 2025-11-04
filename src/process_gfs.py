import os
import glob
import pandas as pd
from modules.GF_Reader import GF_Reader
from modules.Utils import get_value_from_table


GFS_DIR = os.path.join(os.path.dirname(__file__), "docs", "GFs")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def process_all_gfs(gfs_dir=GFS_DIR):
    pdf_paths = sorted(glob.glob(os.path.join(gfs_dir, "*.pdf")))
    results = []

    if not pdf_paths:
        print(f"No PDF files found in {gfs_dir}")
        return results

    for path in pdf_paths:
        print(f"Processing: {os.path.basename(path)}")
        try:
            reader = GF_Reader(path)

            doc = reader.get_doc()
            if doc is None:
                print(f"  -> failed to open: {path}")
                continue

            pages = reader.get_pages_from_docs(doc) or []

            # Extract simple labels from page text
            guia = reader.get_by_label(pages, label="Guia de Transporte")
            chave = reader.get_by_label(pages, label="Chave de Acesso da NFe")
            protocolo = reader.get_by_label(pages, label="Protocolo")

            remetente = reader.get_remetente_ou_destinatario(pages, option="Remetente")
            destinatario = reader.get_remetente_ou_destinatario(pages, option="Destinatário")

            placas = reader.get_placa(pages)

            # Dates: reader.get_datetime returns a dict or None; capture raw
            data_emissao = reader.get_datetime(pages, label="Data de Emissão")
            data_validade = reader.get_datetime(pages, label="Data de Validade no Estado")

            # Tables: use get_value_from_table directly (works per-file)
            volume = get_value_from_table(path, label="Volume")
            preco_unitario = get_value_from_table(path, label="Preço Unitário")
            preco_total = get_value_from_table(path, label="Preço Total")
            produto = get_value_from_table(path, label="Produto")
            essencia = get_value_from_table(path, label="Essência")
            lote = get_value_from_table(path, label="Lote")

            record = {
                "file": os.path.basename(path),
                "Guia de Transporte": guia,
                "Chave de Acesso da NFe": chave,
                "Protocolo": protocolo,
                "Nome Remetente": remetente.get("Remetente") if isinstance(remetente, dict) else remetente,
                "CNPJ/CPF Remetente": remetente.get("Cnpj_Cpf") if isinstance(remetente, dict) else None,
                "Nome Destinatário": destinatario.get("Destinatário") if isinstance(destinatario, dict) else destinatario,
                "CNPJ/CPF Destinatário": destinatario.get("Cnpj_Cpf") if isinstance(destinatario, dict) else None,
                "Placa 1": placas.get("Placa 1") if isinstance(placas, dict) else None,
                "Placa 2": placas.get("Placa 2") if isinstance(placas, dict) else None,
                "Placa 3": placas.get("Placa 3") if isinstance(placas, dict) else None,
                "Placa 4": placas.get("Placa 4") if isinstance(placas, dict) else None,
                "Data Emissão (raw)": data_emissao,
                "Data Validade (raw)": data_validade,
                "Volume": volume,
                "Preço Unitário": preco_unitario,
                "Preço Total": preco_total,
                "Produto": produto,
                "Essência": essencia,
                "Lote": lote,
            }

            results.append(record)

        except Exception as e:
            print(f"  -> error processing {path}: {e}")

    # ensure output dir exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "gfs_summary.csv")

    try:
        df = pd.DataFrame(results)
        df.to_csv(out_path, index=False)
        print(f"Wrote summary to {out_path}")
    except Exception as e:
        print(f"Failed to write CSV: {e}")

    return results


if __name__ == "__main__":
    process_all_gfs()
