import streamlit as st
import pandas as pd
from utils import parser_xml, parser_invoice, comparador
import io

st.set_page_config(page_title="Confronto XML x Invoice", layout="wide")
st.title("📦 Confronto de XML da NF-e com Invoice (CI)")

# --- Upload dos arquivos ---
st.header("📁 Upload de Arquivos")

col1, col2 = st.columns(2)

with col1:
    xml_file = st.file_uploader("📤 Enviar XML da NF-e", type=["xml"], key="xml")

with col2:
    invoice_file = st.file_uploader("📤 Enviar Planilha da Invoice (aba 'CI')", type=["xlsx", "xls"], key="invoice")

# --- Processamento após upload ---
if xml_file and invoice_file:
    st.success("✅ Arquivos carregados com sucesso.")

    # Parse dos dados
    st.header("🔍 Prévia dos Dados Carregados")

    with st.spinner("Lendo XML..."):
        dados_xml, resumo_xml = parser_xml.processar(xml_file)

    with st.spinner("Lendo Invoice..."):
        dados_invoice, resumo_invoice = parser_invoice.processar(invoice_file)

    # Mostrar resumos
    st.subheader("📑 Resumo do XML")
    st.json(resumo_xml, expanded=False)

    st.subheader("📑 Resumo da Invoice (CI)")
    st.json(resumo_invoice, expanded=False)

    # Mostrar todos os itens
    st.subheader("🔎 Todos os itens do XML")
    st.dataframe(dados_xml, use_container_width=True)

    st.subheader("🔎 Todos os itens da Invoice")
    st.dataframe(dados_invoice, use_container_width=True)

    # Confronto
    if st.button("🚨 Confrontar XML x Invoice"):
        with st.spinner("Comparando os dados..."):
            resultado = comparador.confrontar(dados_xml, dados_invoice)
            st.session_state["resultado"] = resultado
            st.session_state["mostrar_erros"] = False

    # Exibir resultado do confronto (se houver)
    if "resultado" in st.session_state:
        resultado = st.session_state["resultado"]

        st.subheader("📊 Resultado do Confronto")
        if "nItem" in resultado.columns:
            resultado_ordenado = resultado.sort_values("nItem").set_index("nItem")
        else:
            resultado_ordenado = resultado

        st.dataframe(resultado_ordenado, use_container_width=True)

        # --- RESUMO DE ERROS ---
        erros = resultado[
            (resultado["verificação total pares"] != "✅ OK") |
            (resultado["verificação unit price"] != "✅ OK") |
            (resultado["verificação valor total"] != "✅ OK")
        ]
        st.session_state["erros"] = erros
        qtd_erros = len(erros)

        st.markdown("### ❗ Resumo de Divergências")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total de Itens com Erros", qtd_erros)

        with col2:
            if st.button("🔍 Exibir Apenas os Erros"):
                st.session_state["mostrar_erros"] = True

        if st.session_state.get("mostrar_erros", False):
            st.subheader("🧯 Itens com Divergência")
            if "nItem" in erros.columns:
                erros_ordenado = erros.sort_values("nItem").set_index("nItem")
            else:
                erros_ordenado = erros
            st.dataframe(erros_ordenado, use_container_width=True)

        if not erros.empty:
            # Garante que nItem apareça como primeira coluna no Excel
            if "nItem" in erros.columns:
                colunas = ["nItem"] + [col for col in erros.columns if col != "nItem"]
                erros_export = erros[colunas]
            else:
                erros_export = erros.copy()

            buffer = io.BytesIO()
            erros_export.to_excel(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                label="📥 Baixar Erros em Excel",
                data=buffer,
                file_name="erros_confronto.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # --- BOTÃO DE RESET PARA NOVA CONFRONTAÇÃO ---
    st.markdown("---")
    if st.button("🔄 Iniciar Nova Confrontação"):
        st.session_state.clear()
        st.rerun()

else:
    st.warning("⚠️ Envie os dois arquivos para iniciar.")
