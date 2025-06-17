import pandas as pd

def processar(excel_file):
    try:
        df = pd.read_excel(excel_file, sheet_name="CI", header=0, dtype=str)
    except Exception as e:
        return [], {"erro": f"Erro ao ler a aba 'CI': {str(e)}"}

    # Padronizar nomes das colunas
    df.columns = [int(col) if str(col).isdigit() else str(col).strip().lower() for col in df.columns]

    # Colunas obrigatórias
    colunas_fixas = ["item", "marca", "ref", "ncm", "cor", "caixas", "total pares", "preco unit", "valor total"]
    tamanhos = list(range(20, 46))

    for col in colunas_fixas + tamanhos:
        if col not in df.columns:
            return [], {"erro": f"Coluna obrigatória ausente: {col}"}

    itens = []
    total_pares = 0
    total_nota = 0.0

    for _, row in df.iterrows():
        ref = str(row.get("ref", "")).strip()
        cor = str(row.get("cor", "")).strip()
        ncm = str(row.get("ncm", "")).strip()

        preco_unit_raw = str(row.get("preco unit", "0")).strip()
        preco_unit_str = preco_unit_raw.replace(",", ".")
        try:
            preco_unit_float = float(preco_unit_str)
        except:
            preco_unit_float = 0.0

        total_item = 0.0

        for tamanho in tamanhos:
            qtd_str = str(row.get(tamanho, "0")).strip()
            qtd = int(qtd_str) if qtd_str.isdigit() else 0

            if qtd > 0:
                valor_total = round(preco_unit_float * qtd, 2)
                itens.append({
                    "ref": ref,
                    "cor": cor,
                    "tamanho": str(tamanho),
                    "ncm": ncm,
                    "quantidade": qtd,
                    "preco_unit": preco_unit_float,
                    "valor_total": valor_total,
                    "xProd": f"{ref} - {cor} - {tamanho}",
                    "total pares": qtd,
                    "unit price": preco_unit_float,
                    "valor total": valor_total
                })
                total_pares += qtd
                total_item += valor_total

        total_nota += total_item

    return itens, {
        "total pares": total_pares,
        "valor total nota": round(total_nota, 2)
    }
