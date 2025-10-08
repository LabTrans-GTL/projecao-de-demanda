import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Configuração da página
st.set_page_config(
    page_title="Projeção de Demanda Aeroportuária",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado consolidado
st.markdown("""
<style>
    /* Configurações da sidebar */
    .css-1d391kg {
        width: 400px !important;
        min-width: 400px !important;
    }
    
    .css-1y0tads {
        width: 400px !important;
        min-width: 400px !important;
    }
    
    /* Melhorar espaçamento da sidebar */
    .css-1cypcdb {
        padding: 1rem 1.5rem;
    }
    
    /* Configurações gerais para modo claro e escuro */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: var(--background-color, white);
        color: var(--text-color, #333);
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 5px solid #2a5298;
        margin-bottom: 1rem;
        border: 1px solid var(--border-color, #e0e0e0);
    }
    
    .info-box {
        background: var(--info-bg, #f0f8ff);
        color: var(--text-color, #333);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2196f3;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color, #e0e0e0);
    }
    
    .success-box {
        background: var(--success-bg, #f0fff0);
        color: var(--text-color, #333);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4caf50;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color, #e0e0e0);
    }
    
    .warning-box {
        background: var(--warning-bg, #fff8dc);
        color: var(--text-color, #333);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #ff9800;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color, #e0e0e0);
    }
    
    /* Melhorar selectboxes */
    .stSelectbox > div > div {
        background-color: var(--background-color, white);
        color: var(--text-color, #333);
        border-radius: 8px;
        border: 1px solid var(--border-color, #e0e0e0);
        padding: 0.5rem;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #2a5298;
        box-shadow: 0 2px 4px rgba(42, 82, 152, 0.1);
    }
    
    /* Melhorar selectboxes da sidebar */
    .css-1d391kg .stSelectbox > div > div {
        background-color: var(--background-color, white);
        color: var(--text-color, #333);
        border-radius: 8px;
        border: 1px solid var(--border-color, #e0e0e0);
        padding: 0.5rem;
    }
    
    .css-1d391kg .stSelectbox > div > div:hover {
        border-color: #2a5298;
        box-shadow: 0 2px 4px rgba(42, 82, 152, 0.1);
    }
    
    /* Melhorar texto em modo escuro */
    .stMarkdown {
        color: var(--text-color, #333);
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: var(--text-color, #333);
    }
    
    /* Melhorar texto da sidebar */
    .css-1d391kg .stMarkdown {
        color: var(--text-color, #333);
    }
    
    .css-1d391kg .stMarkdown h3 {
        color: var(--text-color, #333);
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Melhorar contraste geral */
    .stApp {
        background-color: var(--background-color, #ffffff);
        color: var(--text-color, #333);
    }
    
    /* Melhorar gráficos */
    .js-plotly-plot {
        background-color: var(--background-color, white);
    }
    
    /* Melhorar mapas */
    .stMap {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Melhorar contraste para modo escuro */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #1e1e1e;
            --text-color: #ffffff;
            --border-color: #404040;
            --info-bg: #1a2332;
            --success-bg: #1a2e1a;
            --warning-bg: #2e2a1a;
        }
        
        .metric-card {
            background: #2d2d2d;
            color: #ffffff;
            border: 1px solid #404040;
        }
        
        .info-box {
            background: #1a2332;
            color: #ffffff;
            border: 1px solid #404040;
        }
        
        .success-box {
            background: #1a2e1a;
            color: #ffffff;
            border: 1px solid #404040;
        }
        
        .warning-box {
            background: #2e2a1a;
            color: #ffffff;
            border: 1px solid #404040;
        }
    }
    
    /* Forçar modo escuro se detectado */
    [data-theme="dark"] {
        --background-color: #1e1e1e;
        --text-color: #ffffff;
        --border-color: #404040;
        --info-bg: #1a2332;
        --success-bg: #1a2e1a;
        --warning-bg: #2e2a1a;
    }
    
    [data-theme="dark"] .metric-card {
        background: #2d2d2d;
        color: #ffffff;
        border: 1px solid #404040;
    }
    
    [data-theme="dark"] .info-box {
        background: #1a2332;
        color: #ffffff;
        border: 1px solid #404040;
    }
    
    [data-theme="dark"] .success-box {
        background: #1a2e1a;
        color: #ffffff;
        border: 1px solid #404040;
    }
    
    [data-theme="dark"] .warning-box {
        background: #2e2a1a;
        color: #ffffff;
        border: 1px solid #404040;
    }
</style>
""", unsafe_allow_html=True)

# Caminhos dos dados
CSV_AISWEB = os.path.join('src', 'data', 'AISWEB_Aeroportos.csv')
CSV_PAX_MERCADO = os.path.join('src', 'data', 'projecoes_por_aeroporto.csv')
CSV_PAX_PAN = os.path.join('src', 'data', 'base_final_PAN_cenarios.csv')
CSV_CARGA = os.path.join('src', 'data', 'Painel_Carga.csv')
EXCEL_PAX_INTERNACIONAL = os.path.join('src', 'data', 'Passageiros_Internacionais.xlsx')

# Carregar dados
@st.cache_data
def load_aisweb():
    return pd.read_csv(CSV_AISWEB, encoding='latin-1', sep=';')

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

@st.cache_data
def load_pax_internacional():
    try:
        df = pd.read_excel(EXCEL_PAX_INTERNACIONAL)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        return df
    except Exception:
        return pd.DataFrame()

# Função para converter valores de carga
def convert_carga_value(value):
    try:
        if pd.isna(value) or value == '':
            return 0.0
        str_value = str(value).strip()
        if ',' in str_value and '.' in str_value:
            str_value = str_value.replace('.', '').replace(',', '.')
        elif ',' in str_value:
            str_value = str_value.replace(',', '.')
        return float(str_value)
    except:
        return 0.0

# Função para converter valores de passageiros
def convert_passageiros_value(value):
    try:
        if pd.isna(value) or value == '':
            return 0.0
        str_value = str(value).strip()
        if ',' in str_value:
            str_value = str_value.replace(',', '.')
        return float(str_value)
    except:
        return 0.0

# Carregar todos os dados
aeroportos = load_aisweb()
pax_mercado = load_pax_mercado()
pax_pan = load_pax_pan()
carga = load_carga()
pax_internacional = load_pax_internacional()

# Ajustar nomes de colunas
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
    <h1>✈️ Projeção de Demanda Aeroportuária 2025-2054</h1>
    <p>Sistema de Análise e Projeção de Demanda para Infraestrutura Aeroportuária</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Configurações de Análise")
    
    # Primeiro seletor: Tipo de projeção
    tipo_projecao = st.selectbox(
        '📊 Tipo de Projeção',
        ['Passageiros', 'Carga']
    )
    
    # Segundo seletor: Para Passageiros - Doméstico/Internacional
    if tipo_projecao == 'Passageiros':
        natureza_pax = st.selectbox(
            '🌍 Natureza',
            ['Doméstico', 'Internacional']
        )
        
        # Terceiro seletor: Para Doméstico - Mercado/PAN
        if natureza_pax == 'Doméstico':
            tipo_domestico = st.selectbox(
                '🏗️ Tipo de Projeção Doméstica',
                ['Mercado (Rede Atual)', 'PAN (Rede de Planejamento)']
            )
        else:
            tipo_domestico = None
    else:
        natureza_pax = None
        tipo_domestico = None

    # Determinar dados baseado nas seleções
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
            
        elif natureza_pax == 'Doméstico':
            if tipo_domestico == 'Mercado (Rede Atual)':
                df_base = pax_mercado
                coluna_icao = 'airport_id'
                coluna_valor = 'total_movimento'
                y_label = 'Passageiros'
            else:  # PAN
                df_base = pax_pan
                coluna_icao = 'icao'
                coluna_valor = 'passageiros'
                y_label = 'Passageiros'

    # Obter aeroportos disponíveis na projeção selecionada
    if not df_base.empty:
        aeroportos_disponiveis = sorted(df_base[coluna_icao].astype(str).unique())
        aeroportos_filtrados = aeroportos[aeroportos['ICAO'].isin(aeroportos_disponiveis)]
    else:
        aeroportos_filtrados = aeroportos

    # Seletor de escopo
    escopo = st.selectbox(
        '🎯 Escopo da Análise',
        ['Brasil Total', 'Aeroporto Específico']
    )

    # Filtros de localização (apenas se não for Brasil Total)
    if escopo == 'Aeroporto Específico':
        st.markdown("### 📍 Localização")
        ufs = sorted(aeroportos_filtrados['UF'].unique())
        uf = st.selectbox('🏛️ UF', ufs)
        cidades = sorted(aeroportos_filtrados[aeroportos_filtrados['UF'] == uf]['Cidade'].unique())
        cidade = st.selectbox('🏙️ Cidade', cidades)
        icaos = sorted(aeroportos_filtrados[(aeroportos_filtrados['UF'] == uf) & (aeroportos_filtrados['Cidade'] == cidade)]['ICAO'].unique())
        icao = st.selectbox('✈️ ICAO', icaos)
        
        # Título e dados para aeroporto específico
        if tipo_projecao == 'Carga':
            titulo = f'Projeção de Carga - {icao}'
            df = df_base[df_base[coluna_icao] == icao].copy()
        elif tipo_projecao == 'Passageiros':
            if natureza_pax == 'Internacional':
                titulo = f'Passageiros Internacionais - {icao}'
                df = df_base[df_base[coluna_icao] == icao].copy()
            elif natureza_pax == 'Doméstico':
                if tipo_domestico == 'Mercado (Rede Atual)':
                    titulo = f'Passageiros Domésticos - Mercado (Rede Atual) - {icao}'
                    df = df_base[df_base[coluna_icao] == icao].copy()
                else:  # PAN
                    titulo = f'Passageiros Domésticos - PAN (Rede de Planejamento) - {icao}'
                    df = df_base[df_base[coluna_icao] == icao].copy()
        
        st.markdown(f"**Aeroporto:** {icao} - {cidade}/{uf}")
        
    else:  # Brasil Total
        # Agregar dados por ano e cenário
        if not df_base.empty:
            df_base_copy = df_base.copy()
            
            if coluna_valor == 'total_movimento':
                df_base_copy[coluna_valor] = df_base_copy[coluna_valor].apply(convert_passageiros_value)
            elif coluna_valor == 'passageiros':
                df_base_copy[coluna_valor] = df_base_copy[coluna_valor].apply(convert_passageiros_value)
            elif coluna_valor == 'carga_(kg)':
                df_base_copy[coluna_valor] = df_base_copy[coluna_valor].apply(convert_carga_value)
            
            df = df_base_copy.groupby(['ano', 'cenario'])[coluna_valor].sum().reset_index()
        else:
            df = pd.DataFrame()
        
        # Título para Brasil Total
        if tipo_projecao == 'Carga':
            titulo = 'Projeção de Carga - Brasil Total'
        elif tipo_projecao == 'Passageiros':
            if natureza_pax == 'Internacional':
                titulo = 'Passageiros Internacionais - Brasil Total'
            elif natureza_pax == 'Doméstico':
                if tipo_domestico == 'Mercado (Rede Atual)':
                    titulo = 'Passageiros Domésticos - Mercado (Rede Atual) - Brasil Total'
                else:  # PAN
                    titulo = 'Passageiros Domésticos - PAN (Rede de Planejamento) - Brasil Total'
        
        st.markdown('**Escopo:** Brasil Total')

# Layout principal
col1, col2 = st.columns([3, 1])

with col1:
    # Criar gráfico
    fig = go.Figure()
    
    if not df.empty:
        # Converter valores se necessário
        if coluna_valor == 'total_movimento':
            df[coluna_valor] = df[coluna_valor].apply(convert_passageiros_value)
        elif coluna_valor == 'passageiros':
            df[coluna_valor] = df[coluna_valor].apply(convert_passageiros_value)
        elif coluna_valor == 'carga_(kg)':
            df[coluna_valor] = df[coluna_valor].apply(convert_carga_value)
        
        # Separar histórico e projeções
        df_hist = df[df['cenario'] == 'Observado']
        df_proj = df[df['cenario'] != 'Observado']
        
        # Adicionar dados históricos se existirem
        if not df_hist.empty:
            fig.add_trace(go.Scatter(
                x=df_hist['ano'], 
                y=df_hist[coluna_valor],
                mode='lines+markers', 
                name='Observado', 
                line=dict(color='#666666', width=3, dash='dot'),
                marker=dict(size=8, color='#666666'),
                hovertemplate='<b>Observado</b><br>Ano: %{x}<br>Valor: %{y:,.0f}<extra></extra>'
            ))
        
        # Adicionar cenários de projeção
        cores_cenarios = {
            'Tendencial': '#1f77b4',
            'Transformador': '#2ca02c', 
            'Pessimista': '#d62728'
        }
        
        for cenario in ['Tendencial', 'Transformador', 'Pessimista']:
            df_cen = df_proj[df_proj['cenario'] == cenario]
            if not df_cen.empty:
                fig.add_trace(go.Scatter(
                    x=df_cen['ano'], 
                    y=df_cen[coluna_valor],
                    mode='lines+markers', 
                    name=cenario, 
                    line=dict(color=cores_cenarios[cenario], width=3),
                    marker=dict(size=8, color=cores_cenarios[cenario]),
                    hovertemplate=f'<b>{cenario}</b><br>Ano: %{{x}}<br>Valor: %{{y:,.0f}}<extra></extra>'
                ))

    # Configurar layout do gráfico
    fig.update_layout(
        title=dict(
            text=titulo,
            x=0.5,
            font=dict(size=20, color='#1e3c72')
        ),
        xaxis=dict(
            title='Ano',
            range=[2025, 2054],
            tickmode='linear',
            tick0=2025,
            dtick=5,
            gridcolor='#e0e0e0',
            title_font=dict(size=14, color='#333')
        ),
        yaxis=dict(
            title=y_label,
            gridcolor='#e0e0e0',
            title_font=dict(size=14, color='#333')
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", color='#333'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12)
        ),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Métricas resumidas
    if not df.empty:
        st.markdown("### 📈 Resumo 2054")
        
        # Último ano de projeção
        ultimo_ano = df[df['ano'] == df['ano'].max()]
        
        for cenario in ['Tendencial', 'Transformador', 'Pessimista']:
            valor = ultimo_ano[ultimo_ano['cenario'] == cenario][coluna_valor]
            if not valor.empty:
                try:
                    valor_num = float(valor.iloc[0])
                    if coluna_valor == 'carga_(kg)':
                        if valor_num >= 1e9:
                            valor_formatado = f"{valor_num/1e9:.1f}B kg"
                        elif valor_num >= 1e6:
                            valor_formatado = f"{valor_num/1e6:.1f}M kg"
                        else:
                            valor_formatado = f"{valor_num:,.0f} kg"
                    else:
                        if valor_num >= 1e9:
                            valor_formatado = f"{valor_num/1e9:.1f}B"
                        elif valor_num >= 1e6:
                            valor_formatado = f"{valor_num/1e6:.1f}M"
                        else:
                            valor_formatado = f"{valor_num:,.0f}"
                except:
                    valor_formatado = str(valor.iloc[0])
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="color: {cores_cenarios[cenario]}; margin: 0;">{cenario}</h4>
                    <p style="font-size: 1.2em; margin: 0.5rem 0;"><strong>{valor_formatado}</strong></p>
                    <small style="color: #666;">2054</small>
                </div>
                """, unsafe_allow_html=True)

# Mapa
st.markdown("### 🗺️ Localização Geográfica")

if escopo == 'Aeroporto Específico':
    info_aero = aeroportos[aeroportos['ICAO'] == icao]
    if not info_aero.empty:
        info_aero_copy = info_aero.copy()
        info_aero_copy['lat'] = info_aero_copy['lat'].astype(str).str.replace(',', '.').astype(float)
        info_aero_copy['lon'] = info_aero_copy['lon'].astype(str).str.replace(',', '.').astype(float)
        st.map(info_aero_copy[['lat', 'lon']])
    else:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ Informações Geográficas</h4>
            <p>Informações geográficas não encontradas para este ICAO.</p>
        </div>
        """, unsafe_allow_html=True)
else:  # Brasil Total
    if not aeroportos_filtrados.empty:
        aeroportos_map = aeroportos_filtrados.copy()
        aeroportos_map['lat'] = aeroportos_map['lat'].astype(str).str.replace(',', '.').astype(float)
        aeroportos_map['lon'] = aeroportos_map['lon'].astype(str).str.replace(',', '.').astype(float)
        st.map(aeroportos_map[['lat', 'lon']])
    else:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ Dados de Localização</h4>
            <p>Nenhum aeroporto encontrado para esta projeção.</p>
        </div>
        """, unsafe_allow_html=True)

# ProjLog - Sempre visível
st.markdown("### 📋 ProjLog das Projeções")

if tipo_projecao == 'Carga':
    st.markdown("""
    <div class="info-box">
        <h4>📦 Projeção de Carga Doméstica</h4>
        <p><strong>Descrição:</strong> Simula a demanda de carga aérea doméstica considerando a rede atual de aeroportos em operação.</p>
        
        <p><strong>🎯 Cenários de Projeção:</strong></p>
        <ul>
            <li><strong>Tendencial:</strong> Cenário baseado na tendência histórica observada</li>
            <li><strong>Transformador:</strong> Cenário otimista com transformações significativas no setor</li>
            <li><strong>Pessimista:</strong> Cenário conservador com crescimento limitado</li>
        </ul>
        
        <p><strong>📅 Período de Análise:</strong> 2025-2054</p>
        <p><strong>📊 Metodologia:</strong> Modelos econométricos baseados em séries históricas</p>
    </div>
    """, unsafe_allow_html=True)

elif tipo_projecao == 'Passageiros':
    if natureza_pax == 'Internacional':
        st.markdown("""
        <div class="info-box">
            <h4>🌍 Projeção de Passageiros Internacionais</h4>
            <p><strong>Descrição:</strong> Simula a demanda de passageiros em voos internacionais considerando a rede atual de aeroportos.</p>
            
            <p><strong>🎯 Cenários de Projeção:</strong></p>
            <ul>
                <li><strong>Tendencial:</strong> Cenário baseado na tendência histórica observada</li>
                <li><strong>Transformador:</strong> Cenário otimista com transformações significativas no setor</li>
                <li><strong>Pessimista:</strong> Cenário conservador com crescimento limitado</li>
            </ul>
            
            <p><strong>📅 Período de Análise:</strong> 2025-2054</p>
            <p><strong>📊 Metodologia:</strong> Modelos econométricos baseados em séries históricas</p>
        </div>
        """, unsafe_allow_html=True)
    
    elif natureza_pax == 'Doméstico':
        if tipo_domestico == 'Mercado (Rede Atual)':
            st.markdown("""
            <div class="info-box">
                <h4>🏠 Projeção de Mercado (Rede Atual)</h4>
                <p><strong>Descrição:</strong> Simula a demanda de passageiros domésticos considerando a rede atual de aeroportos em operação.</p>
                
                <p><strong>🎯 Cenários de Projeção:</strong></p>
                <ul>
                    <li><strong>Tendencial:</strong> Cenário baseado na tendência histórica observada</li>
                    <li><strong>Transformador:</strong> Cenário otimista com transformações significativas no setor</li>
                    <li><strong>Pessimista:</strong> Cenário conservador com crescimento limitado</li>
                </ul>
                
                <p><strong>📅 Período de Análise:</strong> 2025-2054</p>
                <p><strong>📊 Metodologia:</strong> Modelos econométricos baseados em séries históricas</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-box">
                <h4>🏗️ Projeção PAN (Rede de Planejamento)</h4>
                <p><strong>Descrição:</strong> Simula a demanda de passageiros domésticos para a Rede de Aeroportos de Referência do Governo Federal, 
                considerando uma rede de planejamento que pode incorporar novos aeroportos ou modificar os já existentes.</p>
                
                <p><strong>🎯 Objetivo:</strong> Instrumento de planejamento estratégico de longo prazo para orientar a priorização de investimentos em infraestrutura aeroportuária.</p>
                
                <p><strong>🎯 Cenários de Projeção:</strong></p>
                <ul>
                    <li><strong>Tendencial:</strong> Cenário baseado na tendência histórica observada</li>
                    <li><strong>Transformador:</strong> Cenário otimista com transformações significativas no setor</li>
                    <li><strong>Pessimista:</strong> Cenário conservador com crescimento limitado</li>
                </ul>
                
                <p><strong>📅 Período de Análise:</strong> 2025-2054</p>
                <p><strong>📊 Metodologia:</strong> Modelos econométricos baseados em séries históricas</p>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em; padding: 1rem;">
    <p><strong>📊 Fonte dos Dados:</strong> Projeções ANAC, PAN, AISWEB</p>
    <p><strong>🔧 Sistema:</strong> Desenvolvido para análise de demanda aeroportuária</p>
    <p><strong>📅 Última Atualização:</strong> 2025</p>
</div>
""", unsafe_allow_html=True)

