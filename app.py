import streamlit as st
import pandas as pd
import io
import re
import base64
import time
import os
from concurrent.futures import ProcessPoolExecutor
import threading

# =============================================================================
# CONFIGURAÇÕES DA PÁGINA E CSS
# =============================================================================
st.set_page_config(layout="wide", page_title="Auditor Fiscal-Contábil")

def load_css():
    st.markdown("""
    <style>
        /* 1. Esconde o botão secundário "Browse files" */
        [data-testid="stFileUploader"] section button {
            display: none !important;
        }

        section[data-testid="stSidebar"] { display: none !important; }
        .block-container {
            padding-top: 2rem; padding-bottom: 2rem; padding-left: 5rem; padding-right: 5rem;
        }
        .header-container {
            display: flex; align-items: center; gap: 15px; margin-bottom: 20px;
            padding-bottom: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .header-container img { height: 50px; }
        .header-container h1 { margin: 0; font-size: 2.2em; }
        
        /* ESTILO DO BOTÃO DE INÍCIO */
        div[data-testid="stButton"] > button {
            background-color: #1a1a1a;
            color: #FAFAFA;
            border: none;
            padding: 12px 28px;
            border-radius: 8px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
            transition: all 0.2s ease-in-out;
        }
        div[data-testid="stButton"] > button:hover {
            box-shadow: 0 6px 20px rgba(255, 140, 0, 0.4);
            transform: translateY(-2px);
        }
        div[data-testid="stButton"] > button:disabled {
            background-color: #1a1a1a;
            color: #555;
            box-shadow: none;
        }
        
        /* --- NOVA UI DO FILE UPLOADER PARA PARECER UM BOTÃO --- */
        [data-testid="stFileUploader"] {
            padding: 1rem;
            border-radius: 8px;
            background-color: #1a1a1a;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
            transition: all 0.2s ease-in-out;
            text-align: center;
        }
        [data-testid="stFileUploader"]:hover {
            box-shadow: 0 6px 20px rgba(255, 140, 0, 0.4);
            transform: translateY(-2px);
        }
        [data-testid="stFileUploader"] section { padding: 0; }
        [data-testid="stFileUploader"] section > div { min-height: 50px; display: flex; align-items: center; justify-content: center; }
    
        
        /* ALINHAMENTO E TAMANHO DE FONTE DA PRÉ-ANÁLISE */
        .preview-container {
            display: flex;
            align-items: flex-start; /* Alinha os blocos pelo topo */
        }
        .preview-title {
            font-size: 0.9rem;
            color: #aaa;
            margin-bottom: 0px; /* Reduz o espaçamento */
        }
        .preview-value {
            font-size: 1.5rem;
            font-weight: 600;
            color: #FAFAFA;
            padding-top: 0px;
        }
        .preview-checkbox {
             font-size: 1rem; /* Tamanho consistente com o título */
        }

    </style>
    """, unsafe_allow_html=True)

load_css()

# --- CABEÇALHO PERSONALIZADO ---
logo_path = 'logo_empresa.png'
header_html = '<div class="header-container">'
if os.path.exists(logo_path):
    img_bytes = open(logo_path, 'rb').read()
    img_b64 = base64.b64encode(img_bytes).decode()
    header_html += f'<img src="data:image/png;base64,{img_b64}" alt="Logo Empresa">'
header_html += '<h1>🤖 Auditor Automático Fiscal-Contábil</h1></div>'
st.markdown(header_html, unsafe_allow_html=True)

# =============================================================================
# FUNÇÕES DE ANÁLISE (Otimizadas com @st.cache_data)
# =============================================================================

@st.cache_data
def get_sheet_names(_file_content):
    try:
        xls = pd.ExcelFile(io.BytesIO(_file_content))
        return xls.sheet_names
    except Exception as e:
        st.error(f"Não foi possível ler o arquivo Excel. Erro: {e}")
        return []

# (As demais funções de análise permanecem as mesmas, com o decorator @st.cache_data)
@st.cache_data
def load_excel_data(_file_content, sheet_name):
    try:
        return pd.read_excel(io.BytesIO(_file_content), sheet_name=sheet_name, engine='pyxlsb')
    except Exception: return pd.DataFrame()
@st.cache_data
def criar_resumo_fiscal(_file_content, auxiliar_sheet_name):
    df_auxiliar = load_excel_data(_file_content, auxiliar_sheet_name)
    if df_auxiliar.empty or 'CFOP' not in df_auxiliar.columns or 'Valor ICMS' not in df_auxiliar.columns: return pd.DataFrame()
    df_auxiliar['Valor ICMS'] = pd.to_numeric(df_auxiliar['Valor ICMS'], errors='coerce').fillna(0)
    resumo_fiscal = df_auxiliar.groupby('CFOP').agg(Valor_Fiscal_Auto=('Valor ICMS', 'sum')).reset_index()
    resumo_fiscal.rename(columns={'CFOP': 'Codigo'}, inplace=True)
    return resumo_fiscal
@st.cache_data
def criar_resumo_contabil(_file_content, razao_sheet_name):
    df_razao = load_excel_data(_file_content, razao_sheet_name)
    if df_razao.empty or 'CFOP' not in df_razao.columns or 'Montante em moeda interna' not in df_razao.columns: return pd.DataFrame()
    df_razao['Montante em moeda interna'] = pd.to_numeric(df_razao['Montante em moeda interna'], errors='coerce').fillna(0)
    resumo_contabil = df_razao.groupby('CFOP').agg(Valor_Contabil_Auto=('Montante em moeda interna', 'sum')).reset_index().copy()
    resumo_contabil.rename(columns={'CFOP': 'Codigo'}, inplace=True)
    resumo_contabil = resumo_contabil[resumo_contabil['Codigo'].astype(str).str.match(r'^\d{4}/[A-Z]{2}$', na=False)]
    return resumo_contabil
@st.cache_data
def executar_conciliacao_automatizada(resumo_fiscal, resumo_contabil):
    if resumo_fiscal.empty or resumo_contabil.empty: return pd.DataFrame()
    df_reconciliacao_auto = pd.merge(resumo_fiscal, resumo_contabil, on='Codigo', how='outer').fillna(0)
    df_reconciliacao_auto['Diferenca'] = df_reconciliacao_auto['Valor_Contabil_Auto'] - df_reconciliacao_auto['Valor_Fiscal_Auto']
    df_divergencias_auto = df_reconciliacao_auto[abs(df_reconciliacao_auto['Diferenca']) > 0.01].copy()
    return df_divergencias_auto.sort_values(by='Diferenca', key=abs, ascending=False)
@st.cache_data
def reconciliar_por_nf(_file_content, auxiliar_sheet, razao_sheet):
    df_auxiliar_detalhado = load_excel_data(_file_content, auxiliar_sheet)
    df_razao_detalhado = load_excel_data(_file_content, razao_sheet)
    if df_auxiliar_detalhado.empty or df_razao_detalhado.empty or 'Nº da Nota Fiscal' not in df_auxiliar_detalhado.columns or 'Referência' not in df_razao_detalhado.columns: return pd.DataFrame()
    df_fiscal_por_nf = df_auxiliar_detalhado.groupby('Nº da Nota Fiscal').agg(Valor_ICMS_Fiscal=('Valor ICMS', 'sum')).reset_index()
    df_razao_detalhado['Nº da Nota Fiscal'] = df_razao_detalhado['Referência'].astype(str).str.extract(r'(\d+)')
    df_razao_detalhado.dropna(subset=['Nº da Nota Fiscal'], inplace=True)
    df_razao_detalhado['Nº da Nota Fiscal'] = df_razao_detalhado['Nº da Nota Fiscal'].astype(int)
    df_contabil_por_nf = df_razao_detalhado.groupby('Nº da Nota Fiscal').agg(Valor_ICMS_Contabil=('Montante em moeda interna', 'sum')).reset_index()
    df_reconciliacao_nf = pd.merge(df_fiscal_por_nf, df_contabil_por_nf, on='Nº da Nota Fiscal', how='outer').fillna(0)
    df_reconciliacao_nf['Diferenca_NF'] = df_reconciliacao_nf['Valor_ICMS_Fiscal'] - df_reconciliacao_nf['Valor_ICMS_Contabil']
    df_divergencias_nf = df_reconciliacao_nf[abs(df_reconciliacao_nf['Diferenca_NF']) > 0.01].copy()
    return df_divergencias_nf.sort_values(by='Diferenca_NF', key=abs, ascending=False)
@st.cache_data
def justificar_divergencias(df_divergencias_geral, df_divergencias_nf):
    if df_divergencias_geral.empty: return pd.DataFrame()
    causas_provaveis = []
    for _, row in df_divergencias_geral.iterrows():
        causa = "Investigação Manual Necessária"
        if not df_divergencias_nf.empty:
            nf_correspondente = df_divergencias_nf[abs(df_divergencias_nf['Diferenca_NF'] + round(row['Diferenca'], 2)) < 0.01]
            if not nf_correspondente.empty:
                num_nf = int(nf_correspondente.iloc[0]['Nº da Nota Fiscal'])
                causa = f"Possível erro de lançamento na NF {num_nf}."
        causas_provaveis.append(causa)
    df_justificado = df_divergencias_geral.copy()
    df_justificado['Causa_Provavel'] = causas_provaveis
    return df_justificado
def processar_tipo(file_content_bytes, tipo):
    if tipo == 'Entradas':
        resumo_fiscal = criar_resumo_fiscal(file_content_bytes, 'Auxiliar entradas')
        resumo_contabil = criar_resumo_contabil(file_content_bytes, '1106010001 ICMS A RECUPERAR')
        conciliacao = executar_conciliacao_automatizada(resumo_fiscal, resumo_contabil)
        divergencias_nf = reconciliar_por_nf(file_content_bytes, 'Auxiliar entradas', '1106010001 ICMS A RECUPERAR')
        return justificar_divergencias(conciliacao, divergencias_nf), divergencias_nf
    elif tipo == 'Saídas':
        resumo_fiscal = criar_resumo_fiscal(file_content_bytes, 'Auxiliar Saídas')
        resumo_contabil = criar_resumo_contabil(file_content_bytes, '2102010001 ICMS A PAGAR')
        conciliacao = executar_conciliacao_automatizada(resumo_fiscal, resumo_contabil)
        divergencias_nf = reconciliar_por_nf(file_content_bytes, 'Auxiliar Saídas', '2102010001 ICMS A PAGAR')
        return justificar_divergencias(conciliacao, divergencias_nf), divergencias_nf

# =============================================================================
# FLUXO PRINCIPAL DA APLICAÇÃO
# =============================================================================

st.markdown("<p style='font-size: 1.1em; color: #aaa;'>Faça o upload do seu arquivo de apuração (<b style='color: #eee;'>.xlsb</b>).</p>", unsafe_allow_html=True)
uploaded_file = st.file_uploader(" ", type=['xlsb'], label_visibility="collapsed")

if 'processing' not in st.session_state: st.session_state.processing = False

if uploaded_file is not None:
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<p class='preview-title'>Tamanho do Arquivo</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='preview-value'>{uploaded_file.size / (1024 * 1024):.2f} MB</p>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<p class='preview-title'>Estrutura do Arquivo</p>", unsafe_allow_html=True)
        sheet_names = get_sheet_names(uploaded_file.getvalue())
        abas_necessarias = ['Auxiliar entradas', 'Auxiliar Saídas', '1106010001 ICMS A RECUPERAR', '2102010001 ICMS A PAGAR']
        abas_encontradas = {aba: (aba in sheet_names) for aba in abas_necessarias}
        
        sub_cols = st.columns(2)
        for i, (aba, encontrada) in enumerate(abas_encontradas.items()):
            sub_cols[i % 2].markdown(f"<span class='preview-checkbox'>{'✅' if encontrada else '❌'} `{aba}`</span>", unsafe_allow_html=True)
    
    st.write("") # Espaçamento
    if all(abas_encontradas.values()):
        if st.button("▶️ Iniciar Análise Completa", use_container_width=True, disabled=st.session_state.processing):
            st.session_state.processing = True
            st.session_state.results = None
            if 'total_time' in st.session_state: del st.session_state.total_time
            st.rerun()

    if st.session_state.processing:
        # (A lógica de processamento e exibição de resultados permanece a mesma)
        status_area = st.empty()
        progress_bar = st.progress(0)
        start_time = time.time()
        
        if st.session_state.results is None:
            with ProcessPoolExecutor(max_workers=4) as executor:
                future_entradas = executor.submit(processar_tipo, uploaded_file.getvalue(), 'Entradas')
                future_saidas = executor.submit(processar_tipo, uploaded_file.getvalue(), 'Saídas')
                
                progress = 5
                while not future_entradas.done() or not future_saidas.done():
                    elapsed_time = time.time() - start_time
                    message = "Aguardando conclusão de Entradas e Saídas..."
                    if not future_entradas.done() and future_saidas.done():
                        message = "Aguardando conclusão de Entradas..."
                        progress = 75
                    elif future_entradas.done() and not future_saidas.done():
                        message = "Aguardando conclusão de Saídas..."
                        progress = 85
                    
                    status_area.info(f"⏳ Em andamento... ({elapsed_time:.1f}s) - {message}")
                    progress_bar.progress(progress)
                    time.sleep(0.5)

                entradas_justificadas, divergencias_nf_entradas = future_entradas.result()
                saidas_justificadas, divergencias_nf_saidas = future_saidas.result()
                
                st.session_state.results = (entradas_justificadas, divergencias_nf_entradas, saidas_justificadas, divergencias_nf_saidas)
                st.session_state.total_time = time.time() - start_time
                st.rerun()

        total_time = st.session_state.get('total_time', 0)
        status_area.success(f"✅ Análise Concluída em {total_time:.2f} segundos!")
        progress_bar.empty()

        (entradas_justificadas, divergencias_nf_entradas, saidas_justificadas, divergencias_nf_saidas) = st.session_state.results

        tab_entradas, tab_saidas = st.tabs(["📊 Relatório de Entradas (Créditos)", "📈 Relatório de Saídas (Débitos)"])
        with tab_entradas:
            st.subheader("📄 Divergências de Créditos (Entradas)")
            if not entradas_justificadas.empty:
                col1, col2 = st.columns(2)
                col1.metric("Total de Divergências", f"{len(entradas_justificadas)} Códigos")
                col2.metric("Valor Total Divergente", f"R$ {entradas_justificadas['Diferenca'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.dataframe(entradas_justificadas[['Codigo', 'Valor_Contabil_Auto', 'Valor_Fiscal_Auto', 'Diferenca', 'Causa_Provavel']], use_container_width=True)
                with st.expander("Ver detalhes das Notas Fiscais com divergência"):
                    st.dataframe(divergencias_nf_entradas, use_container_width=True)
            else: st.info("🎉 Nenhuma divergência encontrada nas entradas.")
        with tab_saidas:
            st.subheader("📄 Divergências de Débitos (Saídas)")
            if not saidas_justificadas.empty:
                col1, col2 = st.columns(2)
                col1.metric("Total de Divergências", f"{len(saidas_justificadas)} Códigos")
                col2.metric("Valor Total Divergente", f"R$ {saidas_justificadas['Diferenca'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.dataframe(saidas_justificadas[['Codigo', 'Valor_Contabil_Auto', 'Valor_Fiscal_Auto', 'Diferenca', 'Causa_Provavel']], use_container_width=True)
                with st.expander("Ver detalhes das Notas Fiscais com divergência"):
                    st.dataframe(divergencias_nf_saidas, use_container_width=True)
            else: st.info("🎉 Nenhuma divergência encontrada nas saídas.")
else:
    for key in ['processing', 'results', 'total_time']:
        if key in st.session_state:
            del st.session_state[key]