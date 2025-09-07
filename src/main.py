import sys
import time
from constraint import Problem
from collections import defaultdict

# Function to read input file
def read_input(path):
    def parse_positions(line):
        positions_str = line.split(":")[1].strip()
        positions = [tuple(map(int, pos.split(","))) for pos in positions_str.replace("(", "").replace(")", "").split()]
        return positions

    with open(path, "r") as file:
        lines = file.readlines()

    franjas = int(lines[0].strip())
    matriz_dim = tuple(map(int, lines[1].strip().split("x")))

    talleres_std = parse_positions(lines[2])
    talleres_spc = parse_positions(lines[3])
    parkings = parse_positions(lines[4])

    aviones = []
    for line in lines[5:]:
        parts = line.strip().split("-")
        id_avion = parts[0]
        tipo = parts[1]
        restr = parts[2]
        tareas_tipo1 = int(parts[3])
        tareas_tipo2 = int(parts[4])
        aviones.append({"ID": id_avion, "TIPO": tipo, "RESTR": restr, "T1": tareas_tipo1, "T2": tareas_tipo2})

    return franjas, matriz_dim, talleres_std, talleres_spc, parkings, aviones

# Save results
def save_output(output_path, solutions, aviones, franjas, talleres_spc, talleres_std):
    with open(output_path, 'w') as file:
        file.write(f"N. Sol: {len(solutions)}\n")
        if not solutions:
            file.write("No se encontraron soluciones válidas.\n")
            print("No se encontraron soluciones válidas.")
            return

        for i, solution in enumerate(solutions):
            file.write(f"\nSolucion {i + 1}:\n")
            for avion in aviones:
                id_avion = avion["ID"]
                tipo = avion["TIPO"]
                restr = avion["RESTR"]
                tareas_1 = avion["T1"]
                tareas_2 = avion["T2"]
                file.write(f"{id_avion}-{tipo}-{restr}-{tareas_1}-{tareas_2}: ")
                for franja in range(franjas):
                    pos = solution[f"{id_avion}-{franja}"]
                    if pos in talleres_spc:
                        tipo_taller = "SPC"
                    elif pos in talleres_std:
                        tipo_taller = "STD"
                    else:
                        tipo_taller = "PRK"
                    file.write(f"{tipo_taller}{pos} ")
                file.write("\n")

# Define the CSP problem
def define_problem(franjas, tamano, talleres_std, talleres_spc, parkings, aviones):
    problem = Problem()

    dominio = talleres_std + talleres_spc + parkings

    # Variables
    for avion in aviones:
        for franja in range(franjas):
            problem.addVariable(f"{avion['ID']}-{franja}", dominio)

    # Restricción: Máximo 2 aviones por taller
    def restriccion_max_2_aviones(*asignaciones):
        conteo_talleres = defaultdict(int)
        for posicion in asignaciones:
            conteo_talleres[posicion] += 1
            if conteo_talleres[posicion] > 2:
                return False
        return True

    # Restricción: Máximo 1 JUMBO por taller
    def restriccion_max_1_jumbo(*asignaciones):
        conteo_jumbo = defaultdict(int)
        for avion, posicion in zip(aviones, asignaciones):
            if avion["TIPO"] == "JMB":
                conteo_jumbo[posicion] += 1
                if conteo_jumbo[posicion] > 1:
                    return False
        return True

    # Restricción: Completar tareas en talleres válidos con orden si aplica
    def restriccion_tareas(*asignaciones):
        for avion in aviones:
            tareas_restantes = {"T1": avion["T1"], "T2": avion["T2"]}
            talleres_spc_count = 0
            talleres_count = 0

            for franja in range(franjas):
                posicion = asignaciones[aviones.index(avion) * franjas + franja]
                if posicion in talleres_spc:
                    talleres_spc_count += 1
                    talleres_count += 1
                    if tareas_restantes["T2"] > 0:
                        tareas_restantes["T2"] -= 1
                    elif avion["RESTR"] == "T" and tareas_restantes["T2"] == 0 and tareas_restantes["T1"] > 0:
                        tareas_restantes["T1"] -= 1
                elif posicion in talleres_std:
                    talleres_count += 1
                    if tareas_restantes["T2"] > 0 and avion["RESTR"] == "T":
                        return False
                    if tareas_restantes["T1"] > 0:
                        tareas_restantes["T1"] -= 1

            # Validar que las tareas tipo 2 se realizaron en talleres especializados
            if talleres_spc_count < avion["T2"]:
                return False

            # Validar que las tareas tipo 1 se realizaron en talleres válidos
            if talleres_count < avion["T1"] + avion["T2"]:
                return False

        return True

    # Restricción: Asegurar adyacencia libre
    def restriccion_adyacencia(*asignaciones):
        ocupados = set(asignaciones)
        for posicion in ocupados:
            if posicion in parkings + talleres_std + talleres_spc:
                x, y = posicion
                adyacentes = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                if all(adj in ocupados for adj in adyacentes if adj in dominio):
                    return False
        return True

    # Restricción: Evitar aviones JUMBO adyacentes
    def restriccion_jumbos_no_adyacentes(*asignaciones):
        posiciones_jumbos = [pos for avion, pos in zip(aviones, asignaciones) if avion["TIPO"] == "JMB"]
        for pos in posiciones_jumbos:
            x, y = pos
            adyacentes = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            if any(adj in posiciones_jumbos for adj in adyacentes if adj in dominio):
                return False
        return True

    for franja in range(franjas):
        variables_franja = [f"{avion['ID']}-{franja}" for avion in aviones]
        problem.addConstraint(restriccion_max_2_aviones, variables_franja)
        problem.addConstraint(restriccion_max_1_jumbo, variables_franja)
        problem.addConstraint(restriccion_adyacencia, variables_franja)
        problem.addConstraint(restriccion_jumbos_no_adyacentes, variables_franja)

    # Añadir restricciones
    problem.addConstraint(restriccion_tareas, [f"{avion['ID']}-{franja}" for avion in aviones for franja in range(franjas)])

    return problem

# Main function
def main():
    if len(sys.argv) != 2:
        print("Uso: python CSPMaintenance.py <path maintenance>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = input_path.replace(".txt", ".csv")

    # Read input data
    franjas, tamano, talleres_std, talleres_spc, parkings, aviones = read_input(input_path)

    # Debugging output
    print(f"Franjas: {franjas}")
    print(f"Tamaño de la matriz: {tamano}")
    print(f"Talleres STD: {talleres_std}")
    print(f"Talleres SPC: {talleres_spc}")
    print(f"Parkings: {parkings}")
    print(f"Aviones: {aviones}")

    # Define the CSP problem
    problem = define_problem(franjas, tamano, talleres_std, talleres_spc, parkings, aviones)

    # Solve the problem and measure time
    start_time = time.time()
    solutions = problem.getSolutions()
    end_time = time.time()

    print(f"Tiempo: {end_time - start_time:.2f} segundos")
    print(f"Número de soluciones encontradas: {len(solutions)}")

    save_output(output_path, solutions, aviones, franjas, talleres_spc, talleres_std)

if _name_ == "_main_":
    main()