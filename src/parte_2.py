from itertools import product

# =========================================
# FUNCIÓN PARA LEER EL MAPA Y LOS AVIONES
# =========================================
def leer_mapa(ruta_archivo):
    with open(ruta_archivo, 'r') as file:
        n_aviones = int(file.readline().strip())
        aviones = []
        for _ in range(n_aviones):
            linea = file.readline().strip()
            pos_inicial, pos_final = linea.split()
            pos_inicial = tuple(map(int, pos_inicial.strip("()").split(',')))
            pos_final = tuple(map(int, pos_final.strip("()").split(',')))
            aviones.append((pos_inicial, pos_final))
        mapa = [line.strip().split(';') for line in file]
    return n_aviones, aviones, mapa

# =========================================
# FUNCIÓNES HEURÍSTICAS
# =========================================
def heuristica_global(posiciones, objetivos):
    return sum(abs(x1 - x2) + abs(y1 - y2) for (x1, y1), (x2, y2) in zip(posiciones, objetivos))

# =========================================
# GENERACIÓN DE MOVIMIENTOS VÁLIDOS
# =========================================
def generar_movimientos_validos(n_aviones, posiciones, mapa):
    dicc_posiciones = {}
    for i in range(n_aviones):
        movimientos_posibles = []
        x, y = posiciones[i]
        filas, columnas = len(mapa), len(mapa[0])
        posibles_movimientos = [
            (0, -1, '←'), (0, 1, '→'), (-1, 0, '↑'), (1, 0, '↓'), (0, 0, 'w')
        ]
        for dx, dy, movimiento in posibles_movimientos:
            nx, ny = x + dx, y + dy
            if 0 <= nx < filas and 0 <= ny < columnas and (mapa[nx][ny] == 'A' or mapa[nx][ny] == 'B'):
                if not (mapa[x][y] == 'A' and movimiento == 'w'):
                    movimientos_posibles.append((nx, ny, movimiento))
        dicc_posiciones[i] = movimientos_posibles
    return dicc_posiciones

# =========================================
# VERIFICACIÓN DE CRUCES ENTRE AVIONES
# =========================================
def no_hay_cruces(anteriores, nuevas):
    posiciones_ocupadas = set()
    for i in range(len(anteriores)):
        if nuevas[i] in posiciones_ocupadas:
            return False
        posiciones_ocupadas.add(nuevas[i])
        for j in range(i + 1, len(anteriores)):
            if anteriores[i] == nuevas[j] and anteriores[j] == nuevas[i]:
                return False
    return True

# =========================================
# IMPLEMENTACIÓN DEL ALGORITMO A*
# =========================================
def a_estrella_multi(n_aviones, aviones, mapa):
    n = n_aviones
    posiciones_iniciales = tuple(avion[0] for avion in aviones)
    objetivos = tuple(avion[1] for avion in aviones)
    
    open_list = []  # Lista abierta manual como cola de prioridad
    caminos_iniciales = [[(posicion[0], posicion[1], '')] for posicion in posiciones_iniciales]
    open_list.append((0, posiciones_iniciales, 0, caminos_iniciales))  # (f, posiciones, g, caminos)
    visited = set()

    while open_list:
        # Ordenar lista para simular comportamiento de cola de prioridad
        open_list.sort(key=lambda x: x[0])  # Ordenar por f
        f, posiciones, g, caminos = open_list.pop(0)  # Extraer el menor elemento

        if posiciones in visited:
            continue
        visited.add(posiciones)

        if posiciones == objetivos:
            return caminos

        movimientos_aviones = generar_movimientos_validos(n_aviones, posiciones, mapa)
        combinaciones = product(*[movimientos_aviones[i] for i in range(n)])
        combinaciones_validas = [
            tuple((nx, ny) for nx, ny, _ in comb)
            for comb in combinaciones
            if no_hay_cruces(posiciones, [(nx, ny) for nx, ny, _ in comb])
        ]

        for nuevas_posiciones in combinaciones_validas:
            nuevos_caminos = [
                caminos[i] + [(nuevas_posiciones[i][0], nuevas_posiciones[i][1], 
                            next(mov for nx, ny, mov in movimientos_aviones[i] 
                                    if (nx, ny) == nuevas_posiciones[i]))]
                for i in range(n)
            ]
            g_nuevo = g + 1
            h = heuristica_global(nuevas_posiciones, objetivos)
            open_list.append((g_nuevo + h, nuevas_posiciones, g_nuevo, nuevos_caminos))
    
    return None

# =========================================
# PROGRAMA PRINCIPAL
# =========================================
try:
    ruta = "mapa.csv"
    n, aviones, mapa = leer_mapa(ruta)
except Exception as e:
    print(f"Error al leer el archivo: {e}")
    exit()

solucion = a_estrella_multi(n, aviones, mapa)

if solucion:
    print("Solución encontrada:")
    for i, camino in enumerate(solucion):
        pasos_con_movimientos = []
        for paso in camino:
            pos, mov = paso[:2], paso[2]
            if mov:
                pasos_con_movimientos.append(f"{mov} {pos}")
            else:
                pasos_con_movimientos.append(f"{pos}")
        print(f"Avión {i + 1}: " + " ".join(pasos_con_movimientos))
else:
    print("No se encontró solución. Puede que las posiciones iniciales u obstáculos impidan el movimiento.")
