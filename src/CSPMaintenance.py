from constraint import *
from functools import partial
import os
import random

# Función principal
def main():
    
    # Leer archivo de entrada
    datos = leer_archivo_entrada("data.txt")

    # Definir problema
    problem = define_problem(datos)

    # Resolver el problema
    soluciones = problem.getSolutions()
    
    # Generar el archivo de salida
    generar_salida_csv("data.txt", soluciones, datos)



def leer_archivo_entrada(ruta_archivo):
    """
    Lee un archivo de entrada con el formato especificado y retorna un diccionario con los datos procesados.
    """
    with open(ruta_archivo, 'r') as archivo:
        lineas = archivo.readlines()

    # Procesar la información general
    franjas = int(lineas[0].split(":")[1].strip())
    num_filas, num_columnas = map(int, lineas[1].split("x"))

    # Procesar la distribución de la matriz
    distribucion_matriz = {"STD": [], "SPC": [], "PRK": []}
    for key in distribucion_matriz.keys():
        linea = next((linea for linea in lineas if linea.startswith(f"{key}:")), None)
        if linea:
            posiciones = linea.split(":")[1].strip().split()
            distribucion_matriz[key] = [tuple(map(int, pos.strip("()").split(","))) for pos in posiciones]

    # Procesar los datos de los aviones
    aviones = []
    for linea in lineas:
        if "-" in linea and linea[0].isdigit():
            partes = linea.strip().split("-")
            avion = {
                "ID": int(partes[0]),
                "TIPO": partes[1],
                "RESTR": partes[2],
                "T1": int(partes[3]),
                "T2": int(partes[4])
            }
            aviones.append(avion)

    # Retornar los datos en un diccionario estructurado
    return {
        "franjas": franjas,
        "num_filas": num_filas,
        "num_columnas": num_columnas,
        "distribucion_matriz": distribucion_matriz,
        "aviones": aviones
    }

def generar_salida_csv(nombre_entrada, soluciones, datos):
    """
    Genera un archivo CSV con las soluciones encontradas.
    """
    # Construir el nombre del archivo de salida
    base_name = os.path.splitext(os.path.basename(nombre_entrada))[0]
    nombre_salida = f"{base_name}.csv"

    with open(nombre_salida, 'w') as archivo_salida:
        # Escribir el número de soluciones
        archivo_salida.write(f"N. Sol: {len(soluciones)}\n")

        # Generamos un número aleatorio para seleccionar un número de soluciones
        soluciones_a_escribir = random.sample(soluciones, random.randint(1, len(soluciones))) if soluciones else []
        
        # Limitar el número de soluciones a 30 si es necesario
        n_soluciones = min(len(soluciones_a_escribir), 30)
        # Formatear y escribir las soluciones
        for i, solucion in enumerate(soluciones[:n_soluciones], 1):  # Limitar a 10 soluciones
            archivo_salida.write(f"Solucion {i}:\n")
            for avion in datos["aviones"]:
                fila = [f"{avion['ID']}-{avion['TIPO']}-{avion['RESTR']}-{avion['T1']}-{avion['T2']}: "]
                for franja in range(datos["franjas"]):
                    variable_name = f"{franja+1}-{avion['ID']}"
                    posicion = solucion[variable_name]
                    tipo_taller = obtener_tipo_taller(posicion, datos)
                    fila.append(f"{tipo_taller}{posicion}")
                archivo_salida.write(" ".join(fila) + "\n")


def obtener_tipo_taller(posicion, datos):
    """
    Devuelve el tipo de taller en base a la posición.
    """
    if posicion in datos["distribucion_matriz"]["SPC"]:
        return "SPC"
    elif posicion in datos["distribucion_matriz"]["STD"]:
        return "STD"
    elif posicion in datos["distribucion_matriz"]["PRK"]:
        return "PRK"
    else:
        print(f"Posición desconocida: {posicion}")

def define_problem(datos):
    """
    Define el problema CSP y agrega las variables y restricciones.
    """
    # Crear el problema de CSP
    problem = Problem()

    # Crear las variables: cada avión puede estar en cualquier posición en cualquier franja
    for franja in range(datos["franjas"]):
        for avion in datos["aviones"]:
            variable_name = f"{franja+1}-{avion['ID']}"
            domain = datos["distribucion_matriz"]["STD"] + datos["distribucion_matriz"]["SPC"] + datos["distribucion_matriz"]["PRK"]
            problem.addVariable(variable_name, domain)

    # Restricción 0: Asegurar que cada avión pueda completar sus tareas (T1 + T2)
    for avion in datos["aviones"]:
        variables = [f"{franja+1}-{avion['ID']}" for franja in range(datos["franjas"])]
        restriccion_parcial = partial(restriccion_completar_tareas, datos=datos, id_avion=avion["ID"])
        problem.addConstraint(restriccion_parcial, variables)

    # Restricción 1: Capacidad máxima de un taller o parking
    for franja in range(datos["franjas"]):
        variables = [f"{franja+1}-{avion['ID']}" for avion in datos["aviones"]]
        restriccion_parcial = partial(constrain_capacidad_maxima, datos=datos)
        problem.addConstraint(restriccion_parcial, variables)

    # Restricción 2: Asignación de tareas correctamente
    for avion in datos["aviones"]:
        variables = [f"{franja+1}-{avion['ID']}" for franja in range(datos["franjas"])]
        restriccion_parcial = partial(restriccion_asignacion_tareas, datos=datos, avion=avion)
        problem.addConstraint(restriccion_parcial, variables)

    # Restricción 3: Adyacencia de posiciones
    for franja in range(datos["franjas"]):
        variables = [f"{franja+1}-{avion['ID']}" for avion in datos["aviones"]]
        restriccion_parcial = partial(restriccion_adyacencia, datos=datos)
        problem.addConstraint(restriccion_parcial, variables)

    return problem

# Restricción 0: Cada avión debe completar todas sus tareas
def restriccion_completar_tareas(*variables, datos, id_avion):
    """
    Asegura que las tareas requeridas (T1 + T2) de un avión puedan ser completadas en las franjas horarias asignadas,
    excluyendo las franjas asignadas a posiciones PRK.
    """
    total_tareas = datos["aviones"][id_avion - 1]["T1"] + datos["aviones"][id_avion - 1]["T2"]
    posiciones_prk = datos["distribucion_matriz"]["PRK"]

    # Contar solo las posiciones donde no esté en PRK
    tareas_realizadas = sum(1 for posicion in variables if posicion not in posiciones_prk)

    # Validar si se pueden completar todas las tareas
    return tareas_realizadas >= total_tareas

# Restricción 1: Capacidad máxima de un taller o parking
def constrain_capacidad_maxima(*variables, datos):
    """
    No puede haber más de dos aviones en un espacio de la matriz.
    Si el avión que ya esta en una posición es de tipo JMB, solo puede haber un avión más STD en esa posición.
    """
    conteo_veces_usada_posicion = {}
    tipos_aviones_en_posicion = {}

    for index, posicion_matriz in enumerate(variables):
        tipo_avion = datos['aviones'][index]['TIPO']
        if posicion_matriz not in conteo_veces_usada_posicion:
            conteo_veces_usada_posicion[posicion_matriz] = 0
            tipos_aviones_en_posicion[posicion_matriz] = []
        conteo_veces_usada_posicion[posicion_matriz] += 1
        tipos_aviones_en_posicion[posicion_matriz].append(tipo_avion)

    # Validar restricciones
    for posicion_matriz in variables:
        if conteo_veces_usada_posicion[posicion_matriz] > 2:
            return False
        if tipos_aviones_en_posicion[posicion_matriz].count("JMB") > 1:
            return False

    return True


#Restricción asignación de tareas correctamente
def restriccion_asignacion_tareas(*variables, datos, avion):
    """
    Verifica que las tareas asignadas a cada avión sean correctas.
    """
    tareas_t1 = avion["T1"]
    tareas_t2 = avion["T2"]
    talleres_spc = 0
    talleres_std = 0
    tareas_t2_comenzadas = False
    tareas_t2_finalizadas = False
    for posicion_matriz in variables:
        if posicion_matriz in datos["distribucion_matriz"]["SPC"]:
            talleres_spc += 1
            tareas_t2_comenzadas = True
            if talleres_spc >= tareas_t2:
                tareas_t2_finalizadas = True 
            
        elif posicion_matriz in datos["distribucion_matriz"]["STD"]:
            talleres_std += 1
            if avion["RESTR"] == "T" and tareas_t2_comenzadas and not tareas_t2_finalizadas:
                return False
            
        elif posicion_matriz in datos["distribucion_matriz"]["PRK"]:
            
            if avion["RESTR"] == "T" and tareas_t2_comenzadas and not tareas_t2_finalizadas:
                return False
        
        total_tareas_asignadas = talleres_spc + talleres_std

    
    #Si existen tareas de tipo 2, deben de realizarse en talleres especializados (SPC)
    if tareas_t2 > 0 and talleres_spc < tareas_t2:
        return False
    
    #Las tareas t1, deben de realizarse todas da igual el tipo de taller
    if tareas_t1 > 0 and (total_tareas_asignadas-tareas_t2) < tareas_t1:
        return False
    
    # Validar que si el avión tiene RESTR = 'T', T2 ocurre antes que T1, suponiendo que NO puede ir a STD antes de terminar T2
    if avion["RESTR"] == "T":
        tareas_t2_restantes = tareas_t2
        for index, posicion_matriz in enumerate(variables):
            if posicion_matriz in datos["distribucion_matriz"]["SPC"] and tareas_t2_restantes > 0:
                tareas_t2_restantes -= 1
            elif tareas_t2_restantes > 0 and posicion_matriz in datos["distribucion_matriz"]["STD"]:
                # Si encuentra un STD antes de terminar T2, es inválido
                return False

    return True

def restriccion_adyacencia(*variables, datos):
    """
    Verifica que las posiciones de los aviones cumplan con las siguientes restricciones:
    1. Al menos una posición adyacente debe estar libre (maniobrabilidad).
    2. Dos aviones tipo JMB no pueden estar adyacentes.
    """
    # Obtener el tamaño de la matriz para limitar los bordes
    num_filas = datos["num_filas"]
    num_columnas = datos["num_columnas"]

    # Crear una matriz de ocupación para la franja horaria actual
    matriz_ocupacion = [[None for col in range(num_columnas)] for fil in range(num_filas)]

    # Asignar aviones a las posiciones en la matriz según las variables
    for index, posicion in enumerate(variables):
        fila, columna = posicion
        matriz_ocupacion[fila][columna] = datos["aviones"][index]  # Asignar el avión a la posición

    # Verificar restricciones para cada posición ocupada
    for fila in range(num_filas):
        for columna in range(num_columnas):
            avion_actual = matriz_ocupacion[fila][columna]
            if avion_actual is not None:
                # Generar las posiciones adyacentes (arriba, abajo, izquierda, derecha)
                adyacentes = [
                    (fila - 1, columna),  # Arriba
                    (fila + 1, columna),  # Abajo
                    (fila, columna - 1),  # Izquierda
                    (fila, columna + 1)   # Derecha
                ]

                # Filtrar las posiciones adyacentes válidas (dentro de los límites de la matriz)
                adyacentes_validas = [
                    (f, c) for f, c in adyacentes
                    if 0 <= f < num_filas and 0 <= c < num_columnas
                ]

                # Verificar maniobrabilidad: al menos una posición adyacente debe estar libre
                if all(matriz_ocupacion[f][c] is not None for f, c in adyacentes_validas):
                    return False  # No hay maniobrabilidad

                # Verificar que no haya JUMBOS adyacentes
                if avion_actual["TIPO"] == "JMB":
                    for f, c in adyacentes_validas:
                        avion_adyacente = matriz_ocupacion[f][c]
                        if avion_adyacente is not None and avion_adyacente["TIPO"] == "JMB":
                            return False  # No puede haber dos JUMBOS adyacentes

    # Si cumple con todas las restricciones, retornar True
    return True

   

# Ejecutar función principal
main()
