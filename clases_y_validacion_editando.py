import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.io import loadmat, whosmat
import os

#carpeta base: donde esta guardado este mismo archivo .py
#funciona en cualquier PC sin importar donde este la carpeta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#carpetas de datos predefinidas
CARPETA_CSV = os.path.join(BASE_DIR, "data_csv")
CARPETA_EEG = os.path.join(BASE_DIR, "data_eeg")

#________________________________________________________

def pedir_entero(mensaje, min_val=None, max_val=None):
    """Pide un entero al usuario y lo valida, si escribe mal vuelve a preguntar"""
    while True:
        try:
            valor = int(input(mensaje))
            if min_val is not None and valor < min_val:
                print(f"El valor debe ser mayor o igual a {min_val}")
                continue
            if max_val is not None and valor > max_val:
                print(f"El valor debe ser menor o igual a {max_val}")
                continue
            return valor
        except ValueError:
            print("Por favor ingrese un numero entero valido.")

#esta funcion se usa en el menu para pedir opciones o indices
#si el usuario escribe algo que no es un numero, vuelve a preguntar

#________________________________________________________

def listar_archivos(carpeta, extension):
    #busca todos los archivos de la extension dada dentro de la carpeta
    #el usuario elige uno por numero, sin escribir rutas
    archivos = []
    for raiz, dirs, ficheros in os.walk(carpeta):
        for f in ficheros:
            if f.endswith(extension):
                archivos.append(os.path.join(raiz, f))

    if len(archivos) == 0:
        print("No se encontraron archivos", extension, "en", carpeta)
        return None

    print("\nArchivos disponibles:")
    for i, ruta in enumerate(archivos, 1):
        nombre_corto = os.path.relpath(ruta, BASE_DIR)
        print(i, "-", nombre_corto)

    idx = pedir_entero("Elija el numero del archivo: ", 1, len(archivos))
    return archivos[idx - 1]

#________________________________________________________

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

def validar_existencia_archivo(ruta, extension=None):
    """Valida que el archivo exista y tenga la extension correcta"""
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"El archivo {ruta} no existe")
    if extension is not None:
        ext = os.path.splitext(ruta)[1].lower()
        if ext != extension:
            raise ValueError(f"Se esperaba un archivo {extension}, se recibio {ext}")
    return ruta
#a la hora de trabajar con los archivos, se verifica su existencia antes de ejecutar algo
#para evitar problemas. Tambien se agrego verificacion de extension.

#________________________________________________________


class ArchivoCSV:
    #clase para manejar los archivos CSV del SIATA (calidad del aire)

    def __init__(self, ruta):
        validar_existencia_archivo(ruta, ".csv")
        self.ruta = ruta
        self.nombre = os.path.basename(ruta)
        self.df = pd.read_csv(ruta)
        #pasar la columna de fechas a indice
        self.df["fecha_hora"] = pd.to_datetime(self.df["fecha_hora"], errors="coerce")
        self.df = self.df.set_index("fecha_hora").sort_index()
        print("Archivo cargado:", self.nombre)
        print("Filas:", len(self.df))

    def mostrar_info(self):
        print("\nInfo del archivo:")
        self.df.info()

    def mostrar_describe(self):
        print("\nEstadisticas:")
        print(self.df.describe())

    def listar_columnas(self):
        columnas = list(self.df.columns)
        print("\nColumnas disponibles:")
        for i, col in enumerate(columnas, 1):
            print(i, "-", col)
        return columnas

    def elegir_columna(self):
        columnas = self.listar_columnas()
        idx = pedir_entero("Elija el numero de la columna: ", 1, len(columnas))
        return columnas[idx - 1]

    def graficar_columna(self):
        #3 subplots: plot, boxplot e histograma de la columna elegida
        col = self.elegir_columna()
        datos = self.df[col].dropna()

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle("Graficas de: " + col + " - " + self.nombre)

        axes[0].plot(datos.index, datos.values)
        axes[0].set_title("Plot")
        axes[0].set_xlabel("Fecha")
        axes[0].set_ylabel(col)

        axes[1].boxplot(datos.values)
        axes[1].set_title("Boxplot")
        axes[1].set_ylabel(col)

        axes[2].hist(datos.values, bins=30)
        axes[2].set_title("Histograma")
        axes[2].set_xlabel(col)
        axes[2].set_ylabel("Frecuencia")

        plt.tight_layout()
        self.guardar_figura("grafica_" + col + "_" + self.nombre[:-4] + ".png")
        # Se generan 3 subplots para cumplir con el requerimiento de visualización triple
        plt.show()

    def operaciones(self):
        #apply: normalizar cada columna entre 0 y 1
        normalizado = self.df.apply(lambda col: (col - col.min()) / (col.max() - col.min()))
        print("\nResultado con apply (normalizacion min-max), primeras 3 filas:")
        print(normalizado.head(3))

        #map: clasificar la calidad del aire segun el valor de pm25
        if "pm25" in self.df.columns:
            def clasificar(v):
                if pd.isna(v):
                    return "sin dato"
                elif v <= 12:
                    return "buena"
                elif v <= 35.4:
                    return "moderada"
                else:
                    return "mala"
            resultado = self.df["pm25"].map(clasificar)
            print("\nResultado con map (clasificacion pm25), primeras 5 filas:")
            print(resultado.head())
        else:
            print("La columna pm25 no esta en este archivo.")

        #sumar o restar dos columnas elegidas por el usuario
        print("\nElija dos columnas para sumar o restar:")
        col1 = self.elegir_columna()
        col2 = self.elegir_columna()
        op = input("Sumar o restar? (s/r): ").strip()
        if op == "s":
            resultado = self.df[col1] + self.df[col2]
            print("\nResultado de", col1, "+", col2, ", primeras 5 filas:")
        else:
            resultado = self.df[col1] - self.df[col2]
            print("\nResultado de", col1, "-", col2, ", primeras 5 filas:")
        print(resultado.head())

    def graficar_remuestreo(self):
        #resample a dias, meses y trimestres
        col = self.elegir_columna()
        datos = self.df[col].dropna()

        por_dia = datos.resample("D").mean()
        por_mes = datos.resample("ME").mean()
        por_trimestre = datos.resample("QE").mean()

        fig, axes = plt.subplots(3, 1, figsize=(12, 9))
        fig.suptitle("Remuestreo de " + col + " - " + self.nombre)

        axes[0].plot(por_dia.index, por_dia.values)
        axes[0].set_title("Diario")
        axes[0].set_xlabel("Fecha")
        axes[0].set_ylabel(col)

        axes[1].plot(por_mes.index, por_mes.values, marker="o")
        axes[1].set_title("Mensual")
        axes[1].set_xlabel("Fecha")
        axes[1].set_ylabel(col)

        axes[2].plot(por_trimestre.index, por_trimestre.values, marker="s")
        axes[2].set_title("Trimestral")
        axes[2].set_xlabel("Fecha")
        axes[2].set_ylabel(col)

        plt.tight_layout()
        self.guardar_figura("remuestreo_" + col + "_" + self.nombre[:-4] + ".png")
        plt.show()

    def guardar_figura(self, nombre):
        carpeta = os.path.join(BASE_DIR, "graficas")
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
        ruta = os.path.join(carpeta, nombre)
        plt.savefig(ruta)
        print("Grafica guardada en:", ruta)

#________________________________________________________


class ArchivoEEG:
    # Esta clase permite procesar archivos .mat de Parkinson y Control
# detectando automáticamente la matriz de datos y ajustando sus dimensiones.
    
    #clase para manejar archivos .mat de EEG (Control y Parkinson)
    #frecuencia de muestreo de 1000 Hz

    fs = 1000

    def __init__(self, ruta):
        validar_existencia_archivo(ruta, ".mat")
        self.ruta = ruta
        self.nombre = os.path.basename(ruta)
        self.mat = loadmat(ruta)
        self.datos3d = None
        self.datos2d = None
        self.cargar_datos()
        print("Archivo EEG cargado:", self.nombre)

    def cargar_datos(self):
        #busca la variable principal del archivo y arma las matrices 2D y 3D
        #los archivos de clase tienen forma (trials, muestras, canales)
        #se transpone a (trials, canales, muestras) para trabajar mas facil
        ignorar = {"__header__", "__version__", "__globals__"}
        for llave in self.mat:
            if llave in ignorar:
                continue
            arr = self.mat[llave]
            if isinstance(arr, np.ndarray) and arr.ndim >= 2:
                if arr.ndim == 3:
                    #transponer de (trials, muestras, canales) a (trials, canales, muestras)
                    self.datos3d = arr.transpose(0, 2, 1)
                    #2D: aplanar trials -> (canales, muestras_total)
                    self.datos2d = self.datos3d.reshape(self.datos3d.shape[1], -1)
                else:
                    self.datos2d = arr
                    self.datos3d = arr[np.newaxis, :]
                break

    def mostrar_llaves(self):
        print("\nLlaves del archivo (whosmat):")
        info = whosmat(self.ruta)
        for nombre, forma, tipo in info:
            print(" ", nombre, "- forma:", forma, "- tipo:", tipo)
        print("\nForma matriz 2D:", self.datos2d.shape)
        print("Forma matriz 3D:", self.datos3d.shape)
        print("Frecuencia de muestreo:", self.fs, "Hz")

    def sumar_canales(self):
        #suma 3 canales en un rango de muestras elegido por el usuario
        n_canales, n_muestras = self.datos2d.shape
        print("Canales disponibles: 0 a", n_canales - 1)
        print("Muestras disponibles: 0 a", n_muestras - 1)

        c1 = validar_indice_canal(pedir_entero("Canal 1: ", 0, n_canales - 1), n_canales, "Canal 1")
        c2 = validar_indice_canal(pedir_entero("Canal 2: ", 0, n_canales - 1), n_canales, "Canal 2")
        c3 = validar_indice_canal(pedir_entero("Canal 3: ", 0, n_canales - 1), n_canales, "Canal 3")

        inicio = pedir_entero("Muestra de inicio: ", 0, n_muestras - 2)
        fin = pedir_entero("Muestra de fin: ", inicio + 1, n_muestras - 1)

        segmento = self.datos2d[:, inicio:fin]
        t = np.arange(fin - inicio) / self.fs  #eje de tiempo en segundos

        canal1 = segmento[c1]
        canal2 = segmento[c2]
        canal3 = segmento[c3]
        suma = canal1 + canal2 + canal3

        fig, axes = plt.subplots(2, 1, figsize=(12, 7))
        fig.suptitle("Suma de canales - " + self.nombre)

        axes[0].plot(t, canal1, label="Canal " + str(c1))
        axes[0].plot(t, canal2, label="Canal " + str(c2))
        axes[0].plot(t, canal3, label="Canal " + str(c3))
        axes[0].set_title("Canales seleccionados")
        axes[0].set_xlabel("Tiempo (s)")
        axes[0].set_ylabel("Amplitud (uV)")
        axes[0].legend()

        axes[1].plot(t, suma, color="red")
        axes[1].set_title("Resultado de la suma")
        axes[1].set_xlabel("Tiempo (s)")
        axes[1].set_ylabel("Amplitud (uV)")

        plt.tight_layout()
        self.guardar_figura("suma_canales_" + self.nombre[:-4] + ".png")
        plt.show()

    def promedio_std(self):
        #promedio y desviacion estandar sobre la matriz 3D a lo largo de un eje
        print("Forma de la matriz 3D:", self.datos3d.shape)
        eje = pedir_entero("Ingrese el eje (0, 1 o 2): ", 0, self.datos3d.ndim - 1)

        promedio = np.mean(self.datos3d, axis=eje).flatten()
        std = np.std(self.datos3d, axis=eje).flatten()
        x = np.arange(len(promedio))

        fig, axes = plt.subplots(2, 1, figsize=(12, 7))
        fig.suptitle("Promedio y desviacion estandar - eje " + str(eje) + " - " + self.nombre)

        axes[0].stem(x, promedio)
        axes[0].set_title("Promedio")
        axes[0].set_xlabel("Indice")
        axes[0].set_ylabel("Amplitud (uV)")

        axes[1].stem(x, std)
        axes[1].set_title("Desviacion estandar")
        axes[1].set_xlabel("Indice")
        axes[1].set_ylabel("Amplitud (uV)")

        plt.tight_layout()
        self.guardar_figura("prom_std_" + self.nombre[:-4] + ".png")
        plt.show()

    def guardar_figura(self, nombre):
        carpeta = os.path.join(BASE_DIR, "graficas")
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
        ruta = os.path.join(carpeta, nombre)
        plt.savefig(ruta)
        print("Grafica guardada en:", ruta)
        # El guardado automático asegura que los resultados estén disponibles para informes posteriores

#________________________________________________________


class Almacen:
    #clase extra para guardar los objetos creados y poder buscarlos despues

    def __init__(self):
        self.objetos = {}

    def guardar(self, obj):
        self.objetos[obj.nombre] = obj
        print("Objeto guardado:", obj.nombre)

    def listar(self):
        if len(self.objetos) == 0:
            print("El almacen esta vacio.")
        else:
            print("\nObjetos en el almacen:")
            for i, nombre in enumerate(self.objetos, 1):
                tipo = type(self.objetos[nombre]).__name__
                print(i, "-", tipo, ":", nombre)

    def buscar(self, texto):
        for nombre in self.objetos:
            if texto.lower() in nombre.lower():
                print("Encontrado:", nombre)
                return self.objetos[nombre]
        print("No se encontro ninguno con ese nombre.")
        return None
