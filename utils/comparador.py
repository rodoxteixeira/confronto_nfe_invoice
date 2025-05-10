import pandas as pd
import unicodedata

def normalizar(texto):
    """Remove acentos e normaliza texto para comparação."""
    if isinstance(texto, str):
        return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').strip().lower()
    return texto

def confrontar(itens_xml, itens_invoice):
    if not itens_xml or not itens_invoice:
        return pd.DataFrame([{"Erro": "Itens vazios em um dos arquivos"}])

    df_xml = pd.DataFrame(itens_xml)
    df_invoice = pd.DataFrame(itens_invoice)

    df_xml['xProd_normalizado'] = df_xml['xProd'].apply(normalizar)
    df_invoice['xProd_normalizado'] = df_invoice['xProd'].apply(normalizar)

    df_merged = pd.merge(
        df_xml, df_invoice,
        left_on="xProd_normalizado",
        right_on="xProd_normalizado",
        suffixes=('_xml', '_invoice'),
        how='outer',
        indicator=True
    )

    def verificar_diferenca(linha, campo):
        val_xml = linha.get(f"{campo}_xml")
        val_inv = linha.get(f"{campo}_invoice")
        if pd.isnull(val_xml) or pd.isnull(val_inv):
            return "⚠️ Ausente"
        elif round(val_xml, 2) != round(val_inv, 2):
            return f"❌ {val_xml} ≠ {val_inv}"
        else:
            return "✅ OK"

    for campo in ["total pares", "unit price", "valor total"]:
        df_merged[f"verificação {campo}"] = df_merged.apply(lambda row: verificar_diferenca(row, campo), axis=1)

    df_merged["xProd_exibicao"] = df_merged["xProd_xml"].combine_first(df_merged["xProd_invoice"])

    colunas_final = [
        "nItem",  # ← AQUI INCLUÍDO
        "xProd_exibicao",
        "ref_xml", "total pares_xml", "unit price_xml", "valor total_xml",
        "ref_invoice", "total pares_invoice", "unit price_invoice", "valor total_invoice",
        "verificação total pares", "verificação unit price", "verificação valor total",
        "_merge"
    ]

    df_final = df_merged[colunas_final].copy()
    df_final.rename(columns={
        "xProd_exibicao": "xProd",
        "_merge": "origem"
    }, inplace=True)

    return df_final
