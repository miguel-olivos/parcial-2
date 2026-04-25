import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.io import loadmat, whosmat
import os
from datetime import datetime

#funciones de validacion 

#________________________________________________________

def validar_numero_positivo(valor, nombre="valor"):
    """Valida que el valor sea un número positivo"""
    try:
        num = float(valor)
        if num <= 0:
            raise ValueError(f"{nombre} debe ser positivo")
        return num
    except ValueError:
        raise ValueError(f"{nombre} debe ser un número válido")
#se espesifican que sean numeros positivos para evitar frecuencias o datos negativvos
#que generen incongruencias y/o conflictos al ejecutar el codigo

#________________________________________________________

def validar_rango(valor, min_val, max_val, nombre="valor"):
    """Valida que el valor esté dentro de un rango"""
    try:
        num = float(valor)
        if num < min_val or num > max_val:
            raise ValueError(f"{nombre} debe estar entre {min_val} y {max_val}")
        return num
    except ValueError:
        raise ValueError(f"{nombre} debe ser un número válido")
    
#Vericar que los numeros no escapen de un rango determinado
#segun la situacion de analisis

#________________________________________________________

def validar_indice_canal(idx, num_canales, nombre="Canal"):
    """Valida que el índice de canal sea válido"""
    try:
        idx_int = int(idx)
        if idx_int < 0 or idx_int >= num_canales:
            raise ValueError(f"{nombre} debe estar entre 0 y {num_canales-1}")
        return idx_int
    except ValueError:
        raise ValueError(f"{nombre} debe ser un número entero")
    
#se aplica para los archivos egg principalmente por su sistema de tener canales
#y en caso de presentar operaciones "matriciales" es necesario que tengan la misma forma.

#________________________________________________________

def validar_existencia_archivo(ruta):
    """Valida que el archivo exista"""
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"El archivo {ruta} no existe")
    return ruta
#a la hora de trabajar con los archivos, se verifica su existencia antes de ejecutar algo
#para evitar problemas.

#________________________________________________________

#CLASE PARA ARCHIVOS SIATA (CSV)

class ArchivoSIATA:
    """
    Permite cargar, explorar, graficar y operar sobre datos de calidad del aire
    """
    def __init__(self, ruta_archivo):
        self.ruta = validar_existencia_archivo(ruta_archivo)
        self.datos = None #guardar todo lo que se trbaje, por eso empieza en none
        self.nombre = os.path.basename(ruta_archivo).split('.')[0]
        self._cargar_datos() #privado

#________________________________________________________

                #funciones internas.
#________________________________________________________

    def _cargar_datos(self):
        """Carga el archivo CSV con pandas"""
        try:
            self.datos = pd.read_csv(self.ruta)
            print(f"✓ Archivo {self.nombre} cargado correctamente")
            print(f"  Dimensiones: {self.datos.shape[0]} filas, {self.datos.shape[1]} columnas")
        except Exception as e:
            raise Exception(f"Error al cargar {self.ruta}: {e}")       
        
#lee y carga los datos con pandas (DataFrame), se hace el try except
#para evitar errores al ejecutar

#________________________________________________________

    def info_basica(self):
        """Muestra información básica del DataFrame (info y describe)"""
        print("\n" + "="*60)
        print(f"INFORMACIÓN DEL ARCHIVO: {self.nombre}")
        print("="*60)
#esta estructura de print ("="*60) se hace por pura estetica, tras unas pruebas aparte,
#se veia muy feo y la forma que quedo mas ordenado fue siguiendo la presente estructura.
        
        print("\n--- INFO() ---")
        print(f"Total filas: {len(self.datos)}")
        print(f"Total columnas: {len(self.datos.columns)}")
        print(f"Columnas: {list(self.datos.columns)}")
        print(f"Tipos de datos:\n{self.datos.dtypes}") #trabaja sobre cada valor
        print(f"Valores nulos por columna:\n{self.datos.isnull().sum()}")
        
        print("\n--- DESCRIBE() ---")
        columnas_numericas = self.datos.select_dtypes(include=[np.number]).columns
        if len(columnas_numericas) > 0:
            print(self.datos[columnas_numericas].describe()) 
#selecciona solo columnas donde sus datos son valores numericos.

        else:
            print("No hay columnas numéricas para describir")
        
        return self.datos
#________________________________________________________

    def listar_columnas(self):
        """Lista las columnas disponibles"""
        print("\nColumnas disponibles:")
        for i, col in enumerate(self.datos.columns):#enumera cada columna por facilidad.
            print(f"  {i}: {col} (tipo: {self.datos[col].dtype})")
        return list(self.datos.columns)
    #muestra la columbna con su indice y tipos de datos

#________________________________________________________
    def graficar_tres_estilos(self, columna):
            """
            Genera 3 subplots: line plot, boxplot, histograma
            Guarda el gráfico automáticamente
            """
            if columna not in self.datos.columns:
                raise ValueError(f"Columna '{columna}' no encontrada")
            
            # Crear figura con 3 subplots

            fig, axes = plt.subplots(1, 3, figsize=(15, 5)) #le da el tamano a la figura
    #axes, junta los 3 graficos a desarroyar en una misma ventana, todo para facilitar la visualizacion

            # Plot 1: Line plot (cambios segun algun otro dato)
            axes[0].plot(self.datos.index, self.datos[columna], color='blue', alpha=0.7)
            axes[0].set_title(f'Line Plot - {columna}')
            axes[0].set_xlabel('Índice')
            axes[0].set_ylabel('Valor')
            axes[0].grid(True, alpha=0.3)

            # Plot 2: Boxplot (resumen estadistico en un grafico)
            axes[1].boxplot(self.datos[columna].dropna())
            axes[1].set_title(f'Boxplot - {columna}')
            axes[1].set_ylabel('Valor')
            axes[1].grid(True, alpha=0.3)



            # Plot 3: Histograma (analizar si hay sesgoz de datos y/o concentraciones)
            axes[2].hist(self.datos[columna].dropna(), bins=30, color='green', alpha=0.7, edgecolor='black')
            axes[2].set_title(f'Histograma - {columna}')
            axes[2].set_xlabel('Valor')
            axes[2].set_ylabel('Frecuencia')
            axes[2].grid(True, alpha=0.3)

            plt.suptitle(f'Análisis de {columna} - {self.nombre}', fontsize=14)
            plt.tight_layout()
            
            # Guardar gráfico
            nombre_archivo = f"{self.nombre}_{columna}_analisis.png"
            plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight')
            print(f"✓ Gráfico guardado como: {nombre_archivo}")
            plt.close()

        
#________________________________________________________
    def operar_con_apply(self, columna, operacion):
        """
        Aplica una operación usando apply
        Operaciones disponibles: 'normalizar', 'log10', 'cuadrado'
        """
        if columna not in self.datos.columns:
            raise ValueError(f"Columna '{columna}' no encontrada")
        
        datos_limpios = self.datos[columna].dropna()
        
        if operacion == 'normalizar':
            resultado = datos_limpios.apply(lambda x: (x - datos_limpios.min()) / (datos_limpios.max() - datos_limpios.min()))
            print(f"✓ Normalización aplicada a '{columna}'")
        elif operacion == 'log10':
            resultado = datos_limpios.apply(lambda x: np.log10(x) if x > 0 else np.nan)
            print(f"✓ Log10 aplicado a '{columna}'")
        elif operacion == 'cuadrado':
            resultado = datos_limpios.apply(lambda x: x ** 2)
            print(f"✓ Cuadrado aplicado a '{columna}'")
        else:
            raise ValueError(f"Operación '{operacion}' no reconocida")
        
        return resultado
#permite manejar los datos de forma mas compacta segun lo que se busque, por ejemplo al normalizar se 
#logran evidenciar tendencais de forma mas directa y manejable.

#________________________________________________________

    def operar_con_map(self, columna, operacion):
        """
        Aplica una operación usando map
        Operaciones disponibles: 'escalar', 'invertir', 'signo'
        """
        if columna not in self.datos.columns:
            raise ValueError(f"Columna '{columna}' no encontrada")
        
        datos_limpios = self.datos[columna].dropna()
        
        if operacion == 'escalar':
            resultado = datos_limpios.map(lambda x: x * 2)
            print(f"✓ Escalado (x2) aplicado a '{columna}'")
        elif operacion == 'invertir':
            resultado = datos_limpios.map(lambda x: 1/x if x != 0 else np.nan)
            print(f"✓ Inversión aplicada a '{columna}'")
        elif operacion == 'signo':
            resultado = datos_limpios.map(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
            print(f"✓ Función signo aplicada a '{columna}'")
        else:
            raise ValueError(f"Operación '{operacion}' no reconocida")
        
        return resultado
# MOTIVO: Usamos map porque las operaciones son simples transformaciones
# elemento por elemento, sin necesidad de conocer el resto de la serie.
# map es más eficiente y rápido para este tipo de transformaciones directas.

#________________________________________________________

    def sumar_restar_columnas(self, col1, col2, operacion='sumar'):
        """Suma o resta dos columnas"""
        if col1 not in self.datos.columns or col2 not in self.datos.columns:
            raise ValueError("Una o ambas columnas no existen")
        
        if operacion == 'sumar':
            resultado = self.datos[col1] + self.datos[col2]
            print(f"✓ Suma de '{col1}' + '{col2}'")
        elif operacion == 'restar':
            resultado = self.datos[col1] - self.datos[col2]
            print(f"✓ Resta de '{col1}' - '{col2}'")
        else:
            raise ValueError("Operación debe ser 'sumar' o 'restar'")
        
        return resultado
#Operación aritmética entre dos columnas completas 

#________________________________________________________

    def procesar_fechas_y_remuestrear(self, columna_fecha='fecha_hora'):
        """
        Convierte columna de fechas a índice y realiza remuestreo
        """
    #es necesario identificar la columna de fecha para poder convertirla a índice y realizar el remuestreo,
    #por eso se hace esta busqueda de posibles nombres de columnas que puedan contener fechas.
        posibles_fechas = ['fecha_hora', 'fecha', 'date', 'datetime', 'tiempo', 'time']
        col_fecha = None
        
        for posible in posibles_fechas:
            if posible in self.datos.columns:
                col_fecha = posible
                break
        
    #si no se encuentra la columna de fecha con los nombres comunes,
    # se verifica si el nombre proporcionado existe en el DataFrame, si es así se usa ese nombre para la fecha.
        if col_fecha is None and columna_fecha in self.datos.columns:
            col_fecha = columna_fecha
        
        if col_fecha is None:
            print("No se encontró columna de fecha. Usando índice por defecto.")
            return None
        
    # Convertir a datetime y establecer como índice
    #se convierte la columna de fecha a formato datetime, si hay errores se convierten a NaT (Not a Time) 
    # y luego se eliminan esas filas.

        self.datos[col_fecha] = pd.to_datetime(self.datos[col_fecha], errors='coerce')
        self.datos = self.datos.dropna(subset=[col_fecha])
        self.datos = self.datos.set_index(col_fecha)
        self.datos = self.datos.sort_index()
        
        print(f"✓ Índice de fechas configurado usando '{col_fecha}'")
        
    #se selecciona la primera columna numérica disponible para realizar el remuestreo,
    #si no hay columnas numéricas se muestra un mensaje y se retorna None.

        columnas_numericas = self.datos.select_dtypes(include=[np.number]).columns
        if len(columnas_numericas) == 0:
            print("No hay columnas numéricas para remuestrear")
            return None
        
        col_numerica = columnas_numericas[0]
        print(f"Usando columna numérica: {col_numerica}")
        
    #cada subplot muestra el remuestreo de la columna numérica seleccionada a diferentes frecuencias (diaria, mensual y trimestral).
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        #se hace el remuestreo diario, mensual y trimestral
        #usando la función resample de pandas, se calcula la media para cada día y se grafica.

        # Remuestreo DIARIO
        diario = self.datos[col_numerica].resample('D').mean()
        axes[0].plot(diario.index, diario.values, color='blue')
        axes[0].set_title(f'Remuestreo Diario - {col_numerica}')
        axes[0].set_ylabel('Valor')
        axes[0].grid(True, alpha=0.3)
        
        # Remuestreo MENSUAL
        mensual = self.datos[col_numerica].resample('M').mean()
        axes[1].plot(mensual.index, mensual.values, color='red')
        axes[1].set_title(f'Remuestreo Mensual - {col_numerica}')
        axes[1].set_ylabel('Valor')
        axes[1].grid(True, alpha=0.3)
        
        # 3. Remuestreo TRIMESTRAL
        trimestral = self.datos[col_numerica].resample('Q').mean()
        axes[2].plot(trimestral.index, trimestral.values, color='green')
        axes[2].set_title(f'Remuestreo Trimestral - {col_numerica}')
        axes[2].set_xlabel('Fecha')
        axes[2].set_ylabel('Valor')
        axes[2].grid(True, alpha=0.3)
        
        # Título general y guardado
        # se le da un título general a la figura y se guarda automáticamente con un nombre 
        # que incluye el nombre del archivo y el tipo de análisis.
        plt.suptitle(f'Remuestreo de Datos - {self.nombre}', fontsize=14)
        plt.tight_layout()
        
        nombre_archivo = f"{self.nombre}_remuestreo.png"
        plt.savefig(nombre_archivo, dpi=150, bbox_inches='tight')
        print(f"✓ Gráfico de remuestreo guardado como: {nombre_archivo}")
        plt.close()
        
        return {'diario': diario, 'mensual': mensual, 'trimestral': trimestral}
    

    def copiar_datos(self):
        """
        Retorna una copia de los datos para no modificar el original
        """
        return self.datos.copy()

#________________________________________________________



