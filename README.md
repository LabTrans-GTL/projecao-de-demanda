# Projecao Demanda

This project is a Streamlit application designed to present market projection results for all airports in Brazil. It allows users to explore various demand scenarios and historical data related to air travel and cargo.

## Project Structure

```
Projecao_demanda
├── src
│   ├── app.py                  # Main entry point for the Streamlit application
│   ├── data
│   │   ├── projecoes_por_aeroporto.xlsx  # Market projection results for all airports
│   │   ├── Painel_Carga.xlsx   # Market projection results for air cargo
│   │   ├── Passageiros_Internacionais.xlsx  # Projections related to international passengers
│   │   ├── base_final_PAN_cenarios.csv  # Demand projection results for PAN network
│   │   └── AISWEB_Aeroportos.csv  # Information about airports for selectors
│   ├── utils
│   │   └── data_loader.py       # Utility functions for loading and processing data
│   └── components
│       └── map.py               # Functions to create and display a map of airports
├── requirements.txt             # List of dependencies for the project
└── README.md                    # Documentation for the project
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd Projecao_demanda
   ```

2. **Create a virtual environment**:
   ```
   python -m venv Projecao_demanda
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```
     Projecao_demanda\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source Projecao_demanda/bin/activate
     ```

4. **Install the required packages**:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the Streamlit application, execute the following command in the terminal:
```
streamlit run src/app.py
```

## Features

- Select ICAO codes, states, and cities to filter projections.
- Display three scenarios: Tendential, Transformational, and Pessimistic.
- Visualize historical data up to 2024.
- Interactive map showing the locations of selected airports.

## Acknowledgments

This project utilizes data from various sources to provide insights into air travel demand in Brazil.