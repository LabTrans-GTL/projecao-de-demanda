import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np 
import folium
from streamlit_folium import folium_static

# Configuração da página - ESSENCIAL PARA RESPONSIVIDADE
st.set_page_config(
    page_title="Projeção de Demanda do Setor Aéreo Brasileiro 2025-2054",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Personalizado para Estética e Alinhamento ---
st.markdown("""
<style>
    /* Configuração de Cores e Fontes Globais */
    :root {
        --background-color: #F0F8FF !important; 
        --text-color: #333333 !important;
        --border-color: #e0e0e0 !important;
    }
    .stApp { background-color: var(--background-color); }
    /* Limpeza e Margens */
    #MainMenu, footer { visibility: hidden !important; }
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem; margin-top: 0rem !important; }
    .main { padding-top: 0rem; }
    .stApp > header { display: none; }
    hr { margin-top: 0.2rem; margin-bottom: 0.8rem; }

    /* Ajuste do Título Principal */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem 1.5rem; 
        border-radius: 10px; 
        color: white !important;
        text-align: center;
        margin-top: 1.5rem; 
        margin-bottom: 0.4rem; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
    }
    .main-header h1 { color: white !important; font-size: 2.0rem; margin-bottom: 0rem; }
    
    /* ALINHAMENTO DAS COLUNAS E ALTURA FIXA PARA PLOTLY E MAPA */
    div[data-testid="stColumn"] > div > div > div.streamlit-container > div:nth-child(2) { height: 600px !important; }
    .js-plotly-plot { height: 600px !important; }

    /* TÍTULOS DE GRÁFICO E MAPA (H2 ou .content-title) */
    .content-title {
        color: #1e3c72 !important; 
        font-size: 1.15rem; 
        margin-top: 0.3rem;   
        margin-bottom: 0.6rem; 
    }
    
    /* Estilo dos Cartões de Métricas */
    .metric-card {
        background: #ffffff !important;
        padding: 1.2rem; 
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08); 
        border: 1px solid #e0e0e0 !important;
        margin-bottom: 0.7rem; 
    }
    .metric-card h4 { font-size: 1.15em; margin-bottom: 0.4rem; font-weight: 600; }
    .metric-card .main-value { font-size: 1.8em; font-weight: bold; margin: 0.4rem 0 0.1rem; }
    .metric-card .small-text { font-size: 0.85em; }

    /* --- RESPONSIVIDADE (Ajustada) --- */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] { display: block; }
        div[data-testid="stColumn"] { width: 100% !important; margin-bottom: 1rem; }
        .js-plotly-plot { height: auto !important; min-height: 400px; }
    }


</style>
""", unsafe_allow_html=True)

# --- Caminhos dos Dados ---
CSV_AISWEB = os.path.join('src', 'data', 'AISWEB_Aeroportos.csv')
CSV_PAX_MERCADO = os.path.join('src', 'data', 'projecoes_por_aeroporto.csv')
CSV_PAX_PAN = os.path.join('src', 'data', 'base_final_PAN_cenarios.csv')
CSV_CARGA = os.path.join('src', 'data', 'Painel_Carga.csv')
# Caminho corrigido para o CSV de passageiros internacionais
CSV_PAX_INTERNACIONAL = os.path.join('src', 'data', 'Passageiros_Internacionais.csv')

# --- Função Auxiliar de Limpeza Vetorial (Para todas as funções de Load) ---
def clean_numeric_series(series):
    """Limpa e converte uma Series Pandas de string com formato BR para float."""
    cleaned = (
        series
        .astype(str)
        .str.replace('.', '', regex=False)  # Remove ponto de milhar
        .str.replace(',', '.', regex=False)  # Troca vírgula por ponto decimal
    )
    return pd.to_numeric(cleaned, errors='coerce').fillna(0)


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
        # Aplica a limpeza robusta para a coluna de valor (total_movimento)
        df['total_movimento'] = clean_numeric_series(df['total_movimento'])
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_pax_internacional():
    try:
        df = pd.read_csv(CSV_PAX_INTERNACIONAL, sep=';', encoding='latin-1')
        df.columns = ['icao', 'ano', 'cenario', 'sentido', 'natureza', 'passageiros']

        # Normaliza colunas-chave
        df['icao'] = df['icao'].astype(str).str.upper().str.strip()
        df['cenario'] = df['cenario'].astype(str).str.strip()
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')

        # Limpeza robusta para 'passageiros'
        df['passageiros'] = clean_numeric_series(df['passageiros'])

        # Ignora 'sentido' e agrega por ICAO, ano e cenário
        df = (
            df.dropna(subset=['icao', 'ano', 'cenario'])
              .groupby(['icao', 'ano', 'cenario'], as_index=False)['passageiros']
              .sum()
              .sort_values(['icao', 'cenario', 'ano'])
        )

        return df
    except Exception as e:
        st.error(f"Erro ao carregar Passageiros_Internacionais.csv: {e}")
        return pd.DataFrame()

@st.cache_data
def load_carga():
    try:
        df = pd.read_csv(CSV_CARGA, sep=';', encoding='latin-1')
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Limpeza robusta para 'carga_(kg)'
        df['carga_(kg)'] = clean_numeric_series(df['carga_(kg)'])
        
        df = df.dropna(subset=['icao', 'cenario', 'ano', 'carga_(kg)'])
        return df
    except Exception:
        return pd.DataFrame()
        
@st.cache_data
def load_pax_pan_domestico():
    try:
        df = pd.read_csv(CSV_PAX_PAN, sep=';', encoding='latin-1')
        df.columns = ['cenario', 'natureza', 'icao', 'sentido', 'ano', 'passageiros']
        
        # Limpeza robusta para 'passageiros' do PAN
        df['passageiros'] = clean_numeric_series(df['passageiros'])
        
        return df[df['natureza'] == 'Doméstico'].copy()
    except Exception:
        return pd.DataFrame()

# --- Funções de Conversão (NÃO USADAS NA BASE, MANTIDAS POR SEGURANÇA) ---
# Essas funções não são mais chamadas na sidebar, pois a limpeza já é feita nos loaders
def convert_passageiros_value(value):
    # Lógica de conversão manual (agora obsoleta para Pax, mas mantida)
    try:
        str_value = str(value).strip().replace('.', '').replace(' ', '')
        if ',' in str_value:
            str_value = str_value.replace(',', '.')
        return float(str_value) if str_value else 0.0
    except:
        return 0.0
        
def convert_carga_value(value):
    # Lógica de conversão manual (agora obsoleta para Carga, mas mantida)
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
        if v >= 1e9: text = f"{v/1e9:,.1f}" + "B kg"
        elif v >= 1e6: text = f"{v/1e6:,.1f}" + "M kg"
        else: text = f"{v:,.0f}" + " kg"
    else:
        if v >= 1e9: text = f"{v/1e9:,.1f}" + "B"
        elif v >= 1e6: text = f"{v/1e6:,.1f}" + "M"
        else: text = f"{v:,.0f}"
            
    # Converte para padrão brasileiro (PONTO para milhar, VÍRGULA para decimal)
    text = text.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    return text

# --- Carregamento de Dados e Ajustes ---
aeroportos = load_aisweb()
pax_mercado = load_pax_mercado()
pax_internacional = load_pax_internacional()
carga = load_carga() # Agora definido!

aeroportos = aeroportos.rename(columns={'ICAO': 'ICAO','CIDADE': 'Cidade','UF': 'UF','LAT': 'lat','LONG': 'lon'})

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
    
    natureza_pax = None
    tipo_rede = None 
    
    if tipo_projecao == 'Passageiros':
        
        natureza_pax = st.selectbox(
            'Natureza do Voo (Passageiros)',
            ['Doméstico', 'Internacional']
        )
        
        if natureza_pax == 'Doméstico':
            tipo_rede = st.selectbox(
                'Rede de Projeção Doméstica',
                ['Mercado (Rede Atual)', 'PAN (Rede de Planejamento)']
            )

    # Lógica de carregamento de base
    df_base = pd.DataFrame()
    coluna_icao = ''
    coluna_valor = ''
    y_label = ''
    
    if tipo_projecao == 'Carga':
        df_base = carga
        coluna_icao = 'icao'
        coluna_valor = 'carga_(kg)'
        y_label = 'Carga (kg)'
        
    elif tipo_projecao == 'Passageiros':
        if natureza_pax == 'Internacional':
            df_base = pax_internacional
            coluna_icao = 'icao'
            coluna_valor = 'passageiros'
            y_label = 'Passageiros'
            
        elif tipo_rede == 'Mercado (Rede Atual)':
            df_base = pax_mercado
            coluna_icao = 'airport_id'
            coluna_valor = 'total_movimento'
            y_label = 'Passageiros'
        else:  # Doméstico e PAN
            df_base = load_pax_pan_domestico()
            coluna_icao = 'icao'
            coluna_valor = 'passageiros'
            y_label = 'Passageiros'

    # O conversor manual foi removido, a coluna já deve ser numérica.
    
    if not df_base.empty:
        # Limpa ICAO e faz o filtro de aeroportos disponíveis
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
                if natureza_pax == 'Internacional':
                    titulo = f'Passageiros Internacionais - {icao}'
                elif tipo_rede == 'Mercado (Rede Atual)':
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
            if natureza_pax == 'Internacional':
                titulo = 'Passageiros Internacionais - Total Brasil'
            elif tipo_rede == 'Mercado (Rede Atual)':
                titulo = 'Passageiros Domésticos - Mercado (Rede Atual) - Total Brasil'
            else:
                titulo = 'Passageiros Domésticos - PAN (Rede de Planejamento) - Total Brasil'
        
        st.markdown('**Escopo:** Total Brasil')

# --- Layout Principal: GRÁFICO E MAPA LADO A LADO ---

st.markdown("---")
col_grafico, col_mapa = st.columns([2, 1]) 

# --- Coluna 1: GRÁFICO (2/3 da largura) ---
with col_grafico:
    st.markdown(f'<h2 class="content-title">{titulo}</h2>', unsafe_allow_html=True)
    
    fig = go.Figure()
    yaxis_range = None  # Inicializa o range do eixo Y

    if not df.empty:
        df['ano'] = pd.to_numeric(df['ano'], errors='coerce')
        df[coluna_valor] = pd.to_numeric(df[coluna_valor], errors='coerce').fillna(0)
        df = df.dropna(subset=['ano'])
        df['cenario'] = df['cenario'].astype(str)
        df_hist = df[df['cenario'].str.lower() == 'observado']
        df_proj = df[df['cenario'].str.lower() != 'observado']

        # Define se a série atual é carga (para formatação BR específica)
        is_carga_series = (coluna_valor == 'carga_(kg)')

        # Calcula o valor máximo para o eixo Y com base em todos os dados da visualização
        max_val = df[coluna_valor].max()
        if pd.notna(max_val) and max_val > 0:
            yaxis_range = [0, max_val * 1.25]

        # Observado (até 2024)
        if not df_hist.empty:
            df_hist_ate_2024 = df_hist[df_hist['ano'] <= 2024]
            if not df_hist_ate_2024.empty:
                fig.add_trace(
                    go.Scatter(
                        x=df_hist_ate_2024['ano'],
                        y=df_hist_ate_2024[coluna_valor],
                        mode='lines+markers',
                        # customdata contém o valor já formatado via fmt()
                        customdata=[fmt(v, is_carga_series) for v in df_hist_ate_2024[coluna_valor].fillna(0).tolist()],
                        hovertemplate='Ano: %{x}<br>Valor: %{customdata}<extra></extra>',
                        name='Observado',
                        line=dict(color='#6C757D', width=2, dash='dot'),
                        marker=dict(size=5, color='#6C757D')
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
                        customdata=[fmt(v, is_carga_series) for v in serie[coluna_valor].fillna(0).tolist()],
                        hovertemplate='Ano: %{x}<br>Valor: %{customdata}<extra></extra>',
                        name=cenario_nome,
                        line=dict(color=cor, width=2.5),
                        marker=dict(size=7, color=cor) 
                    )
                )

    # Configurar layout do gráfico
    fig.update_layout(
        locale='pt-BR',
        xaxis=dict(
            title='Ano', tickmode='linear', dtick=5, gridcolor='#e0e0e0', title_font=dict(size=13, color='#333'), tickfont=dict(size=12),
            range=[df['ano'].min()-3 if not df.empty and 'ano' in df.columns else 2000, 2056]
        ),
        yaxis=dict(
            title=y_label, gridcolor='#e0e0e0', title_font=dict(size=13, color='#333'),
            # Usamos separatethousands para aplicar separador de milhar e formatamos como inteiro.
            tickformat=',.0f', separatethousands=True, tickfont=dict(size=12),
            range=yaxis_range  # Aplica o range dinâmico
        ), 
        plot_bgcolor='white', paper_bgcolor='white', font=dict(family="Arial, sans-serif", color='#333', size=12), 
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=12)       
        ),
        height=600,
        margin=dict(l=50, r=20, t=20, b=50) 
    )
    
    st.plotly_chart(fig, use_container_width=True)

# --- Coluna 2: MAPA (1/3 da largura) ---
with col_mapa:
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
            # Garante que as coordenadas são floats
            map_data_volume['lat'] = map_data_volume['lat'].astype(str).str.replace(',', '.').astype(float)
            map_data_volume['lon'] = map_data_volume['lon'].astype(str).str.replace(',', '.').astype(float)
            map_data_volume = map_data_volume.dropna(subset=['lat', 'lon', 'volume_2054'])
            
            if not map_data_volume.empty and map_data_volume['volume_2054'].sum() > 0:
                
                # --- Definição de Raio para Leafmap (Folium) ---
                map_data_volume['volume_log'] = np.log1p(map_data_volume['volume_2054'].clip(lower=1))
                
                MAX_RADIUS = 20
                min_log = map_data_volume['volume_log'].min()
                max_log = map_data_volume['volume_log'].max()

                if max_log > min_log:
                    map_data_volume['raio'] = ((map_data_volume['volume_log'] - min_log) / (max_log - min_log)) * MAX_RADIUS
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

                folium_static(m, width=700, height=600) 

            else:
                st.warning("Nenhuma coordenada ou volume válido encontrado para o mapa.")

        except Exception as e:
            st.error(f"Erro ao processar as coordenadas ou volumes para o mapa. Detalhe: {e}") 
    else:
        st.info("Nenhum dado de projeção disponível para mapeamento.")


# ---
## Métricas

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
<div style="text-align: center; color: #666; font-size: 0.9em; padding: 0.8rem; margin-top: 0.5rem;">
    <p><strong>Última Atualização:</strong> Outubro/2025</p>
</div>
""", unsafe_allow_html=True)