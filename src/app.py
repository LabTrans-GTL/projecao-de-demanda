import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np 
# IMPORTAÇÃO NECESSÁRIA PARA O MAPA
import folium
from streamlit_folium import folium_static

# Configuração da página
st.set_page_config(
    page_title="Projeção de Demanda do Setor Aéreo Brasileiro 2025-2054",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Personalizado para Estética LabTrans/Institucional ---
st.markdown("""
<style>
    /* 2. FUNDO AZUL CLARO E FONTES MAIORES */
    
    /* Configuração de Cores e Fontes Globais */
    :root {
        --background-color: #F0F8FF !important; /* Azul Claro para o fundo da página */
        --text-color: #333333 !important;
        --border-color: #e0e0e0 !important;
        font-size: 110%; /* AJUSTADO: Fonte base para um ponto neutro */
    }
    
    /* Aplica o fundo azul claro */
    .stApp {
        background-color: var(--background-color);
    }
    
    /* ---------------------------------------------------- */
    /* AJUSTE PARA REMOVER ESPAÇO EM BRANCO NO TOPO E OTIMIZAR MARGENS */
    
    /* Oculta o menu de deploy (os três pontos e o botão deploy) e o footer */
    #MainMenu, footer {
        visibility: hidden !important;
    }
    
    .block-container {
        padding-top: 0rem !important; 
        padding-bottom: 0rem;
        margin-top: 0rem !important;
    }
    .main {
        padding-top: 0rem; 
    }
    .stApp > header {
        display: none; /* Oculta o cabeçalho padrão do Streamlit */
    }
    
    /* Reduz a margem do separador --- */
    hr {
        margin-top: 0.5rem;    
        margin-bottom: 0.5rem; 
    }
    /* ---------------------------------------------------- */
    
    /* Estilo do sidebar (FONTES AJUSTADAS) */
    .stSidebar .stSelectbox label, 
    .stSidebar .stRadio label,
    .stSidebar .stMarkdown {
        font-size: 1.1em !important; /* AJUSTADO: Fonte dos rótulos dos filtros e texto do sidebar */
        font-weight: 500;
    }
    .stSidebar div[data-testid="stTextInput"] > div > input,
    .stSidebar div[data-testid="stSelectbox"] > div > div > div > input {
        font-size: 1.1em !important; /* AJUSTADO: Fonte do texto digitado/selecionado no filtro */
    }


    /* Estilo do cabeçalho principal (mantido) */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 3rem 1.5rem; 
        border-radius: 15px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15); 
    }
    .main-header h1 {
        color: white !important;
        font-size: 3.5rem; 
        margin-bottom: 0.5rem;
    }

    
    /* Melhoria dos cartões de métricas - HIERARQUIA DE FONTES CORRIGIDA */
    .metric-card {
        background: #ffffff !important;
        padding: 1.5rem; /* Ajustado */
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
        border: 1px solid #e0e0e0 !important;
        margin-bottom: 0.8rem; 
        transition: transform 0.2s ease-in-out; 
    }
    .metric-card:hover {
        transform: translateY(-5px); 
    }
    .metric-card h4 {
        font-size: 1.3em; /* AJUSTADO: Título do cartão */
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .metric-card .main-value {
        font-size: 2.0em; /* CORRIGIDO: Valor principal (CAGR) */
        font-weight: bold;
        margin: 0.5rem 0 0.2rem;
    }
    .metric-card .sub-value {
        font-size: 1.15em; /* AJUSTADO: Valor de projeção */
        color: #555;
        margin: 0.2rem 0 0.5rem;
    }
    .metric-card .small-text {
        font-size: 0.95em; /* AJUSTADO: Texto auxiliar */
        color: #888;
        margin-bottom: 0.5rem;
    }
    .metric-card hr {
        margin: 1.0rem 0; /* Ajustado */
        border: none;
        border-top: 1px solid #f0f0f0; 
    }
    
    /* Estilo para títulos secundários (mantidos) */
    .stMarkdown h3 {
        color: #1e3c72 !important; 
        border-bottom: 2px solid #a9c6f0; 
        padding-bottom: 0.7rem; 
        margin-top: 1rem;    
        margin-bottom: 1rem; 
        font-size: 1.8rem; 
    }
    
    /* AJUSTE PARA ALINHAMENTO FINO DOS TÍTULOS DO GRÁFICO E MAPA (mantidos) */
    .content-title {
        color: #1e3c72 !important; 
        font-size: 1.8rem;
        margin-top: 0.5rem;   
        margin-bottom: 0.8rem; 
    }

    /* Sombras para elementos visuais (mantido) */
    .js-plotly-plot, .stMap, .map-container {
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        overflow: hidden;
    }

</style>
""", unsafe_allow_html=True)

# --- Caminhos dos Dados ---
CSV_AISWEB = os.path.join('src', 'data', 'AISWEB_Aeroportos.csv')
CSV_PAX_MERCADO = os.path.join('src', 'data', 'projecoes_por_aeroporto.csv')
CSV_PAX_PAN = os.path.join('src', 'data', 'base_final_PAN_cenarios.csv')
CSV_CARGA = os.path.join('src', 'data', 'Painel_Carga.csv')

# --- Funções de Carregamento ---
@st.cache_data
def load_aisweb():
    try:
        return pd.read_csv(CSV_AISWEB, encoding='latin-1', sep=';')
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_pax_mercado():
    try:
        df = pd.read_csv(CSV_PAX_MERCADO, sep=';', encoding='latin-1')
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_pax_pan():
    try:
        df = pd.read_csv(CSV_PAX_PAN, sep=';', encoding='latin-1')
        df.columns = ['cenario', 'natureza', 'icao', 'sentido', 'ano', 'passageiros']
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_carga():
    try:
        df = pd.read_csv(CSV_CARGA, sep=';', encoding='latin-1')
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        df = df.dropna(subset=['icao', 'cenario', 'ano', 'carga_(kg)'])
        return df
    except Exception:
        return pd.DataFrame()

# --- Funções de Conversão ---
def convert_passageiros_value(value):
    try:
        str_value = str(value).strip()
        if not str_value: return 0.0
        str_value = str_value.replace('.', '')
        if ',' in str_value:
            str_value = str_value.replace(',', '.')
        str_value = str_value.replace(' ', '')
        return float(str_value)
    except:
        return 0.0
        
def convert_carga_value(value):
    try:
        str_value = str(value).strip()
        if not str_value: return 0.0
        
        if '.' in str_value and ',' in str_value:
            str_value = str_value.replace('.', '')
            str_value = str_value.replace(',', '.')
        elif ',' in str_value:
            str_value = str_value.replace(',', '.')
        return float(str_value)
    except:
        return 0.0

# --- FUNÇÃO DE FORMATAÇÃO PRINCIPAL (PADRÃO BR) ---
def fmt(v, is_carga):
    if v is None or np.isnan(v): return "N/A"
    v = abs(v) 
    
    if is_carga:
        if v >= 1e9: 
            text = f"{v/1e9:,.1f}" + "B kg"
        elif v >= 1e6: 
            text = f"{v/1e6:,.1f}" + "M kg"
        else:
            text = f"{v:,.0f}" + " kg"
    else:
        if v >= 1e9: 
            text = f"{v/1e9:,.1f}" + "B"
        elif v >= 1e6: 
            text = f"{v/1e6:,.1f}" + "M"
        else:
            text = f"{v:,.0f}"
            
    # Converte para padrão brasileiro (PONTO para milhar, VÍRGULA para decimal)
    text = text.replace(',', 'X') 
    text = text.replace('.', ',')
    text = text.replace('X', '.')
    
    return text

# --- Carregamento de Dados e Ajustes ---
aeroportos = load_aisweb()
pax_mercado = load_pax_mercado()
pax_pan = load_pax_pan()
carga = load_carga()

aeroportos = aeroportos.rename(columns={
    'ICAO': 'ICAO',
    'CIDADE': 'Cidade',
    'UF': 'UF',
    'LAT': 'lat',
    'LONG': 'lon'
})

# Header principal
st.markdown("""
<div class="main-header">
    <h1>Projeção de Demanda do Setor Aéreo Brasileiro 2025-2054</h1>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### Configurações de Análise")
    
    tipo_projecao = st.selectbox(
    'Tipo de Projeção',
        ['Passageiros', 'Carga']
    )
    
    if tipo_projecao == 'Passageiros':
        natureza_pax = 'Doméstico'
        tipo_domestico = st.selectbox(
            'Tipo de Projeção Doméstica',
            ['Mercado (Rede Atual)', 'PAN (Rede de Planejamento)']
        )
    else:
        natureza_pax = None
        tipo_domestico = None

    # Lógica de carregamento de base
    df_base = pd.DataFrame()
    coluna_icao = ''
    coluna_valor = ''
    y_label = ''
    conversor = None 

    if tipo_projecao == 'Carga':
        df_base = carga
        coluna_icao = 'icao'
        coluna_valor = 'carga_(kg)'
        y_label = 'Carga (kg)'
        conversor = convert_carga_value
        
    elif tipo_projecao == 'Passageiros':
        if tipo_domestico == 'Mercado (Rede Atual)':
            df_base = pax_mercado
            coluna_icao = 'airport_id'
            coluna_valor = 'total_movimento'
            y_label = 'Passageiros'
            conversor = convert_passageiros_value
        else:  # PAN
            df_base = pax_pan
            coluna_icao = 'icao'
            coluna_valor = 'passageiros'
            y_label = 'Passageiros'
            conversor = convert_passageiros_value
    
    if not df_base.empty and conversor is not None:
        df_base_copy = df_base.copy()
        df_base_copy[coluna_valor] = df_base_copy[coluna_valor].apply(conversor)
        df_base = df_base_copy
    
    if not df_base.empty:
        df_base[coluna_icao] = df_base[coluna_icao].astype(str).str.upper().str.strip()
        aeroportos_disponiveis = sorted(df_base[coluna_icao].astype(str).unique())
        aeroportos_filtrados = aeroportos[aeroportos['ICAO'].isin(aeroportos_disponiveis)]
    else:
        aeroportos_filtrados = aeroportos

    # Seletor de escopo - 'Total Brasil'
    escopo = st.selectbox(
        'Escopo da Análise',
        ['Total Brasil', 'Aeroporto Específico']
    )

    icao = None 
    df = pd.DataFrame()
    titulo = "Selecione uma projeção válida"

    # Lógica para definir o título
    if escopo == 'Aeroporto Específico':
        st.markdown("### Localização")
        
        if aeroportos_filtrados.empty:
            st.warning("Nenhum aeroporto encontrado na projeção selecionada.")
        else:
            ufs = sorted(aeroportos_filtrados['UF'].unique())
            uf = st.selectbox('UF', ufs)
            cidades = sorted(aeroportos_filtrados[aeroportos_filtrados['UF'] == uf]['Cidade'].unique())
            cidade = st.selectbox('Cidade', cidades)
            icaos = sorted(aeroportos_filtrados[(aeroportos_filtrados['UF'] == uf) & (aeroportos_filtrados['Cidade'] == cidade)]['ICAO'].unique())
            icao = st.selectbox('ICAO', icaos)
            
            if not df_base.empty and icao and icao in df_base[coluna_icao].unique():
                df = df_base[df_base[coluna_icao] == icao].copy()

            if tipo_projecao == 'Carga':
                titulo = f'Projeção de Carga - {icao}'
            elif tipo_projecao == 'Passageiros':
                if tipo_domestico == 'Mercado (Rede Atual)':
                    titulo = f'Passageiros Domésticos - Mercado (Rede Atual) - {icao}'
                else:
                    titulo = f'Passageiros Domésticos - PAN (Rede de Planejamento) - {icao}'
            
            st.markdown(f"**Aeroporto:** {icao} - {cidade}/{uf}")
        
    else:  # Total Brasil
        if not df_base.empty:
            df = df_base.groupby(['ano', 'cenario'])[coluna_valor].sum().reset_index()
        
        if tipo_projecao == 'Carga':
            titulo = 'Projeção de Carga - Total Brasil'
        elif tipo_projecao == 'Passageiros':
            if tipo_domestico == 'Mercado (Rede Atual)':
                titulo = 'Passageiros Domésticos - Mercado (Rede Atual) - Total Brasil'
            else:
                titulo = 'Passageiros Domésticos - PAN (Rede de Planejamento) - Total Brasil'
        
        st.markdown('**Escopo:** Total Brasil')

# --- Layout Principal: GRÁFICO E MAPA LADO A LADO ---

st.markdown("---")
# Define a proporção das colunas: 2/3 para o gráfico (2) e 1/3 para o mapa (1)
col_grafico, col_mapa = st.columns([2, 1]) 

# --- Coluna 1: GRÁFICO (2/3 da largura) ---
with col_grafico:
    # Usa a classe CSS "content-title" para o título alinhado e sem margem extra
    st.markdown(f'<h2 class="content-title">{titulo}</h2>', unsafe_allow_html=True)
    
    fig = go.Figure()

    if not df.empty:
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        df[coluna_valor] = pd.to_numeric(df[coluna_valor], errors='coerce').fillna(0)
        df = df.dropna(subset=['ano'])

        df['cenario'] = df['cenario'].astype(str)
        df_hist = df[df['cenario'].str.lower() == 'observado']
        df_proj = df[df['cenario'].str.lower() != 'observado']

        # Observado (até 2024)
        if not df_hist.empty:
            df_hist_ate_2024 = df_hist[df_hist['ano'] <= 2024]
            if not df_hist_ate_2024.empty:
                fig.add_trace(
                    go.Scatter(
                        x=df_hist_ate_2024['ano'],
                        y=df_hist_ate_2024[coluna_valor],
                        mode='lines+markers',
                        name='Observado',
                        line=dict(color='#6C757D', width=2, dash='dot'),
                        marker=dict(size=6, color='#6C757D')
                    )
                )

        # Projeções (2025–2054)
        cores_projecao = {'Tendencial':'#0D6EFD', 'Transformador':'#2CA02C', 'Pessimista':'#FFD000'}
        for cenario_nome, cor in cores_projecao.items():
            serie = df_proj[(df_proj['cenario'] == cenario_nome) & (df_proj['ano'] >= 2025)]
            if not serie.empty:
                fig.add_trace(
                    go.Scatter(
                        x=serie['ano'],
                        y=serie[coluna_valor],
                        mode='lines+markers',
                        name=cenario_nome,
                        line=dict(color=cor, width=3),
                        marker=dict(size=8, color=cor) 
                    )
                )

    # Configurar layout do gráfico
    fig.update_layout(
        xaxis=dict(
            title='Ano', 
            tickmode='linear', 
            dtick=5, 
            gridcolor='#e0e0e0', 
            title_font=dict(size=14, color='#333'), # AJUSTADO: Rótulo do Eixo X
            tickfont=dict(size=13)                  # AJUSTADO: Valores do Eixo X
        ), 
        yaxis=dict(
            title=y_label, 
            gridcolor='#e0e0e0', 
            title_font=dict(size=14, color='#333'), # AJUSTADO: Rótulo do Eixo Y
            tickformat='.0f', 
            separatethousands=True,
            tickfont=dict(size=13)                  # AJUSTADO: Valores do Eixo Y
        ), 
        plot_bgcolor='white', 
        paper_bgcolor='white', 
        font=dict(family="Arial, sans-serif", color='#333', size=13), # AJUSTADO: Fonte base do gráfico
        legend=dict(
            orientation="h",         
            yanchor="bottom",        
            y=1.02,                   
            xanchor="center",          
            x=0.5,                  
            font=dict(size=13)       # AJUSTADO: Fonte da legenda
        ),
        height=650 
    )

    st.plotly_chart(fig, use_container_width=True)

# --- Coluna 2: MAPA (1/3 da largura) ---
with col_mapa:
    # Usa a classe CSS "content-title" para o título alinhado e sem margem extra
    st.markdown('<h2 class="content-title">Cenário Tendencial 2054</h2>', unsafe_allow_html=True)

    target_icao = icao if escopo == 'Aeroporto Específico' else None
    
    if not df_base.empty:
        
        # 1. Filtra a base de projeção para o Cenário Tendencial e Ano 2054
        df_projecao_mapa = df_base[
            (df_base['cenario'] == 'Tendencial') & 
            (df_base['ano'] == 2054)
        ].copy()
        
        # 2. Agrupa por ICAO
        df_projecao_mapa = df_projecao_mapa.groupby([coluna_icao]).agg({coluna_valor: 'sum'}).reset_index()
        df_projecao_mapa = df_projecao_mapa.rename(columns={coluna_valor: 'volume_2054'})
        
        # 3. Junta a projeção com as coordenadas
        map_data_volume = aeroportos.merge(
            df_projecao_mapa, 
            left_on='ICAO', 
            right_on=coluna_icao, 
            how='inner'
        )
        
        try:
            map_data_volume['lat'] = map_data_volume['lat'].astype(str).str.replace(',', '.').astype(float)
            map_data_volume['lon'] = map_data_volume['lon'].astype(str).str.replace(',', '.').astype(float)
            map_data_volume = map_data_volume.dropna(subset=['lat', 'lon', 'volume_2054'])
            
            if not map_data_volume.empty:
                
                # --- Definição de Raio para Leafmap (Folium) ---
                map_data_volume['volume_log'] = np.log1p(map_data_volume['volume_2054'].clip(lower=1))
                
                MAX_RADIUS = 25 
                min_log = map_data_volume['volume_log'].min()
                max_log = map_data_volume['volume_log'].max()

                if max_log > min_log:
                    map_data_volume['raio'] = (
                        (map_data_volume['volume_log'] - min_log) / (max_log - min_log)
                    ) * MAX_RADIUS
                else:
                    map_data_volume['raio'] = 5 
                    
                # 3. Formata o Tooltip
                is_carga_mapa = (coluna_valor == 'carga_(kg)')
                map_data_volume['Tooltip_Text'] = map_data_volume.apply(
                    lambda row: f"<b>{row['ICAO']} - {row['Cidade']}/{row['UF']}</b><br>"
                               f"Projeção 2054 ({tipo_projecao}): {fmt(row['volume_2054'], is_carga_mapa)}", 
                    axis=1
                )
                
                # --- Criação do Mapa Leafmap (Folium) ---
                
                # 4. Define o centro do mapa e o zoom
                center_lat = map_data_volume['lat'].mean()
                center_lon = map_data_volume['lon'].mean()
                zoom_level = 4
                
                if target_icao and target_icao in map_data_volume['ICAO'].values:
                    target_row = map_data_volume[map_data_volume['ICAO'] == target_icao].iloc[0]
                    center_lat = target_row['lat']
                    center_lon = target_row['lon']
                    zoom_level = 7 
                    
                m = folium.Map(
                    location=[center_lat, center_lon], 
                    zoom_start=zoom_level, 
                    control_scale=True, 
                    tiles='cartodbpositron'
                )
                
                # Adiciona os marcadores (bolhas)
                for _, row in map_data_volume.iterrows():
                    
                    cor_fill = '#dc3545' if row['ICAO'] == target_icao else '#0d6efd'
                    
                    folium.CircleMarker(
                        location=(row['lat'], row['lon']),
                        radius=row['raio'], 
                        color=cor_fill, 
                        weight=1,
                        fill=True,
                        fill_color=cor_fill, 
                        fill_opacity=0.6,
                        tooltip=row['Tooltip_Text']
                    ).add_to(m)

                # Exibe o mapa no Streamlit
                # O height é ajustado para ser o mesmo do gráfico (650)
                folium_static(m, width=700, height=650) 

            else:
                st.warning("Nenhuma coordenada ou volume válido encontrado para o mapa.")

        except Exception as e:
            st.error(f"Erro ao processar as coordenadas ou volumes para o mapa. Detalhe: {e}") 
    else:
        st.info("Nenhum dado de projeção disponível para mapeamento.")


# --- Métricas com CAGR ---
st.markdown("---")
    
if not df.empty:
    
    col_tenden, col_transf, col_pess = st.columns(3)
    
    is_carga = (coluna_valor == 'carga_(kg)')
    ano_base = 2025
    ultimo_ano = 2054
    periodo = ultimo_ano - ano_base 
    
    cenarios_cartoes = [
        ('Tendencial', '#0D6EFD', col_tenden), 
        ('Transformador', '#2CA02C', col_transf), 
        ('Pessimista', '#FFD000', col_pess)
    ]

    for nome, cor, coluna in cenarios_cartoes:
        serie = df[df['cenario'] == nome]
        
        v2054_series = serie.loc[serie['ano'] == ultimo_ano, coluna_valor]
        v2025_series = serie.loc[serie['ano'] == ano_base, coluna_valor]
        
        v2054 = v2054_series.squeeze() if not v2054_series.empty else None
        v2025 = v2025_series.squeeze() if not v2025_series.empty else None
        
        if isinstance(v2054, (float, np.float64)) and np.isnan(v2054): v2054 = None
        if isinstance(v2025, (float, np.float64)) and np.isnan(v2025): v2025 = None
        
        cagr = None
        # Cálculo do CAGR
        if v2054 is not None and v2025 is not None and v2025 > 0 and v2054 >= 0 and periodo > 0:
            try:
                cagr = ((v2054 / v2025) ** (1/periodo) - 1) * 100
            except: cagr = 0.0 
        elif v2054 is not None and v2025 is not None and v2025 == 0 and v2054 > 0:
            cagr = float('inf')
        elif v2054 is not None and v2025 is not None and v2025 == 0 and v2054 == 0:
             cagr = 0.0
        
        valor_fmt = fmt(v2054, is_carga)
        # Formatação do CAGR para padrão BR (ponto decimal substituído por vírgula)
        cagr_fmt = f"{cagr:.2f}%".replace('.', ',') if cagr is not None and cagr != float('inf') else "N/A"
        if cagr == float('inf'): cagr_fmt = "Crescimento Ilimitado" 

        with coluna: # Insere o cartão na coluna específica
            st.markdown(f"""
                <div class="metric-card" style="border-left: 8px solid {cor};">
                    <h4 style="color:{cor};">{nome}</h4>
                    <p class="main-value" style="color:{cor};">{cagr_fmt}</p>
                    <p class="small-text">Taxa Média Anual ({ano_base}–{ultimo_ano})</p>
                    <hr>
                    <p class="sub-value">Projeção {ultimo_ano}: <strong>{valor_fmt}</strong></p>
                </div>
                """, unsafe_allow_html=True)
# ---
## Footer

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 1em; padding: 1rem; margin-top: 0.5rem;">
    <p><strong>Última Atualização:</strong> Outubro/2025</p>
</div>
""", unsafe_allow_html=True)