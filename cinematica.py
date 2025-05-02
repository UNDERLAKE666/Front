import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# Configuración inicial
plt.figure(figsize=(14, 8))
plt.style.use('default')

def limpiar_valor(valor):
    try:
        return float(str(valor).replace(',', '.').strip()) if str(valor).strip() else None
    except:
        return None

def cargar_archivo(archivo):
    datos = []
    with open(archivo, 'r', encoding='utf-8') as f:
        for linea in f:
            partes = linea.strip().split(';')
            if len(partes) >= 3:
                try:
                    tiempo = limpiar_valor(partes[0])
                    ang1 = limpiar_valor(partes[1])
                    ang2 = limpiar_valor(partes[2])
                    if all(v is not None for v in [tiempo, ang1, ang2]):
                        datos.append([tiempo, ang1, ang2])
                except:
                    continue
    return pd.DataFrame(datos, columns=['Tiempo (ms)', 'Ángulo 1', 'Ángulo 2'])

colores = plt.cm.tab20.colors

for i, archivo in enumerate(glob.glob('P*.csv')):
    try:
        print(f"\nProcesando: {archivo}")
        df = cargar_archivo(archivo)
        
        if not df.empty:
            df['Tiempo (s)'] = df['Tiempo (ms)'] / 1000
            label = os.path.splitext(archivo)[0]
            
            plt.plot(df['Tiempo (s)'], df['Ángulo 1'], 
                    color=colores[i], 
                    linewidth=2,
                    label=f'{label} - Ángulo 1')
            
            plt.plot(df['Tiempo (s)'], df['Ángulo 2'], 
                    color=colores[i], 
                    linestyle='--',
                    alpha=0.8,
                    label=f'{label} - Ángulo 2')
            
            print(f"Registros válidos: {len(df)}")
            print(f"Rango tiempo: {df['Tiempo (s)'].min():.2f}s - {df['Tiempo (s)'].max():.2f}s")
        else:
            print(f"Archivo vacío o sin datos válidos: {archivo}")
    
    except Exception as e:
        print(f"Error crítico en {archivo}: {str(e)}")

plt.xlabel('Tiempo (segundos)', fontsize=12)
plt.ylabel('Ángulo (grados)', fontsize=12)
plt.title('Comparación de Ángulos', fontsize=14)
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
plt.tight_layout()
plt.show()