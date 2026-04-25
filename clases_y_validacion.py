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

