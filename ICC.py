# -*- coding: utf-8 -*-
"""
Created on Fri May  2 00:55:25 2025

@author: santo
"""

import pandas as pd
import numpy as np
from scipy import stats

def read_participant_data(participant_id):
    """Lee datos de cada participante, maneja formatos CSV y Excel."""
    try:
        if participant_id == 'P5':
            df = pd.read_excel('P5.xlsx', sheet_name='Hoja1')
            df['Ángulo 1'] = df['Ángulo 1'].astype(float)
        else:
            df = pd.read_csv(f'{participant_id}.csv', 
                            delimiter=';', 
                            decimal=',',
                            encoding='utf-8')
        
        df['participante'] = participant_id
        df['medicion'] = df.index + 1
        df.rename(columns={'Ángulo 1': 'angulo'}, inplace=True)
        return df[['participante', 'medicion', 'angulo']]
    
    except Exception as e:
        print(f"Error leyendo {participant_id}: {str(e)}")
        return pd.DataFrame()

# 1. Leer y combinar datos
participantes = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6']
dataframes = [read_participant_data(p) for p in participantes]
combined_df = pd.concat(dataframes, ignore_index=True)

# 2. Normalizar número de mediciones
min_mediciones = combined_df.groupby('participante')['medicion'].max().min()
filtered_df = combined_df[combined_df['medicion'] <= min_mediciones]

# 3. Asignar grupos (ejemplo: primeros 3 expertos, últimos 3 novatos)
filtered_df['grupo'] = np.where(filtered_df['participante'].isin(['P1','P2','P3']), 
                              'experto', 
                              'novato')

# 4. Función ICC actualizada
def calcular_icc(data_frame):
    """Calcula ICC(1,k) usando one-way ANOVA"""
    try:
        pivot_data = data_frame.pivot(index='participante', 
                                    columns='medicion', 
                                    values='angulo')
        n, k = pivot_data.shape
        
        grand_mean = pivot_data.values.mean()
        subject_means = pivot_data.mean(axis=1)
        
        SS_total = ((pivot_data - grand_mean)**2).sum().sum()
        SS_subjects = k * ((subject_means - grand_mean)**2).sum()
        SS_error = SS_total - SS_subjects
        
        MS_subjects = SS_subjects / (n - 1)
        MS_error = SS_error / (n * (k - 1))
        
        icc = (MS_subjects - MS_error) / (MS_subjects + (k - 1)*MS_error)
        return max(0, min(icc, 1))
    
    except Exception as e:
        print(f"Error cálculo ICC: {str(e)}")
        return np.nan

# 5. Análisis completo
def analisis_icc_completo(dataframe):
    resultados = {}
    
    print("\n=== VERIFICACIÓN INICIAL ===")
    print("Participantes por grupo:")
    print(dataframe.groupby('grupo')['participante'].nunique())

    print("\n=== CÁLCULOS ICC ===")
    resultados['General'] = calcular_icc(dataframe)
    
    for grupo in dataframe['grupo'].unique():
        grupo_df = dataframe[dataframe['grupo'] == grupo]
        resultados[grupo] = calcular_icc(grupo_df)
    
    print("\n=== RESULTADOS FINALES ===")
    print("{:<10} {:<10} {:<15}".format('Grupo', 'ICC(1,k)', 'Interpretación'))
    print("-"*35)
    for grupo, icc in resultados.items():
        if pd.isna(icc):
            print(f"{grupo:<10} {'NaN':<10} {'Error'}")
            continue
            
        if icc >= 0.9:
            interp = "Excelente"
        elif icc >= 0.75:
            interp = "Bueno"
        elif icc >= 0.5:
            interp = "Moderado"
        else:
            interp = "Pobre"
        
        print(f"{grupo:<10} {icc:.3f}{'':<5} {interp:<15}")
    
    return resultados

# 6. Ejecutar análisis
if __name__ == "__main__":
    resultados = analisis_icc_completo(filtered_df)