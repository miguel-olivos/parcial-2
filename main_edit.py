from clases_y_validacion_editando import ArchivoCSV, ArchivoEEG, Almacen, pedir_entero, listar_archivos, CARPETA_CSV, CARPETA_EEG

almacen = Almacen()
archivo_csv = None
archivo_eeg = None


def menu_csv():
    global archivo_csv
    # Se usa global para mantener la persistencia del objeto en el menú
    while True:
        print("\n--- Archivos CSV (SIATA) ---")
        print("1. Cargar archivo CSV")
        print("2. Mostrar info del archivo")
        print("3. Mostrar estadisticas (describe)")
        print("4. Graficar columna (plot, boxplot, histograma)")
        print("5. Operaciones (apply, map, suma/resta)")
        print("6. Graficar remuestreo (diario, mensual, trimestral)")
        print("0. Volver")
        print("-" * 30)

        op = input("Opcion: ").strip()

        if op == "0":
            break
        elif op == "1":
            ruta = listar_archivos(CARPETA_CSV, ".csv")
            if ruta is not None:
                archivo_csv = ArchivoCSV(ruta)
                almacen.guardar(archivo_csv)
        elif op in ("2", "3", "4", "5", "6"):
            if archivo_csv is None:
                print("Primero cargue un archivo CSV.")
                continue
            if op == "2":
                archivo_csv.mostrar_info()
            elif op == "3":
                archivo_csv.mostrar_describe()
            elif op == "4":
                archivo_csv.graficar_columna()
            elif op == "5":
                archivo_csv.operaciones()
            elif op == "6":
                archivo_csv.graficar_remuestreo()
        else:
            print("Opcion no valida.")


def menu_eeg():
    global archivo_eeg
    while True:
        print("\n--- Archivos EEG (.mat) ---")
        print("1. Cargar archivo MAT")
        print("2. Mostrar llaves del archivo")
        print("3. Sumar 3 canales y graficar")
        print("4. Promedio y desviacion estandar (stem)")
        print("0. Volver")
        print("-" * 30)

        op = input("Opcion: ").strip()

        if op == "0":
            break
        elif op == "1":
            ruta = listar_archivos(CARPETA_EEG, ".mat")
            if ruta is not None:
                archivo_eeg = ArchivoEEG(ruta)
                almacen.guardar(archivo_eeg)
        elif op in ("2", "3", "4"):
            if archivo_eeg is None:
                print("Primero cargue un archivo MAT.")
                continue
            if op == "2":
                archivo_eeg.mostrar_llaves()
            elif op == "3":
                archivo_eeg.sumar_canales()
            elif op == "4":
                archivo_eeg.promedio_std()
        else:
            print("Opcion no valida.")


def menu_almacen():
    while True:
        print("\n--- Almacen de objetos ---")
        print("1. Ver objetos guardados")
        print("2. Buscar un objeto")
        print("0. Volver")
        print("-" * 30)

        op = input("Opcion: ").strip()

        if op == "0":
            break
        elif op == "1":
            almacen.listar()
        elif op == "2":
            texto = input("Ingrese nombre o parte del nombre: ").strip()
            almacen.buscar(texto)
        else:
            print("Opcion no valida.")


def main():
    while True:
        print("\n=== Sistema de Exploracion Neuroambiental ===")
        print("1. Archivos CSV (SIATA - calidad del aire)")
        print("2. Archivos EEG (.mat - electroencefalografia)")
        print("3. Almacen de objetos")
        print("0. Salir")
        print("-" * 30)

        op = input("Opcion: ").strip()

        if op == "0":
            print("Hasta luego.")
            break
        elif op == "1":
            menu_csv()
        elif op == "2":
            menu_eeg()
        elif op == "3":
            menu_almacen()
        else:
            print("Opcion no valida.")


main()
