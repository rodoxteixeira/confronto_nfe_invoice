import pandas as pd

def processar(excel_file):
    try:
        df = pd.read_excel(excel_file, sheet_name="CI", header=None, dtype=str)
    except Exception as e:
        return [], {"erro": f"Erro ao ler a aba 'CI': {str(e)}"}

    linha_inicio = df[df.iloc[:, 0].astype(str).str.strip().str.upper() == "ITEM"].index
    if linha_inicio.empty:
        return [], {"erro": "Não foi encontrada a linha de cabeçalho com 'ITEM'"}

    idx_inicio = linha_inicio[0]
    df_items = df.iloc[idx_inicio + 1:]
    df_items = df_items.reset_index(drop=True)

    colunas_esperadas = [
        "item pedido", "marca", "ref", "ncm", "cor", "bra_dummy",
        "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44",
        "cajas", "total pares", "unit price", "valor total"
    ]

    if df_items.shape[1] < len(colunas_esperadas):
        return [], {"erro": "Planilha com número de colunas inválido. Use o modelo padrão disponível para download."}

    df_items = df_items.iloc[:, :len(colunas_esperadas)]
    df_items.columns = colunas_esperadas

    itens = []
    total_pares = 0
    total_nota = 0.0

    for _, row in df_items.iterrows():
        try:
            ref = str(row["ref"]).strip()
            cor = str(row["cor"]).strip()
            unit_price = float(str(row["unit price"]).replace(",", "."))
            _ = str(row["valor total"]).replace(".", "").replace(",", ".")

            for tamanho in ["34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44"]:
                qtd_str = row.get(tamanho)
                if pd.notnull(qtd_str):
                    qCom = float(str(qtd_str).replace(",", "."))
                    vProd_calc = round(unit_price * qCom, 2)
                    xProd = f"{ref} - {cor} - {tamanho}"

                    item = {
                        "item pedido": int(row["item pedido"]),
                        "ref": ref,
                        "ncm": row["ncm"],
                        "unidade": "PAR",
                        "total pares": qCom,
                        "unit price": unit_price,
                        "valor total": vProd_calc,
                        "xProd": xProd
                    }

                    total_pares += qCom
                    total_nota += vProd_calc
                    itens.append(item)
        except:
            continue

    resumo = {
        "itens": len(itens),
        "total pares": total_pares,
        "valor total calculado": round(total_nota, 2)
    }

    return itens, resumo
