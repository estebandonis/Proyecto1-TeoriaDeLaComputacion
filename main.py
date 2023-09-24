import nfa_to_dfa as dfn
import dfa_minimization as min

def check_conca(token, regex, i):
    if token not in "(|*) " and i + 1 < len(regex) and regex[i + 1] not in "(|*) ":
        # Concatenación encontrada, agregamos los caracteres juntos
        a = check_conca(token, regex, i + 1)
        return a
    else:
        return i


def shunting_yard_regex(regex):
    # Grado de precedencia de los operadores
    precedencia = {'*': 3, '|': 2, '.': 1}

    # Lista para guardar operandos y operadores
    operadores = []
    operandos = []

    # Recorremos la cadena de caracteres
    i = 0
    while i < len(regex):
        token = regex[i]
        if token not in "(|) ":

            a = check_conca(token, regex, i)
            if a != i:
                lista = [token]
                while i < a:
                    contador = 1
                    lista.append(regex[i + contador])
                    contador += 1

                    i += 1

                string = ''
                for letra in lista:
                    string += letra

                operandos.append(string)

            else:
                operandos.append(token)
        elif token in "|*":
            while operadores and operadores[-1] in "|*" and precedencia[operadores[-1]] >= precedencia[token]:
                operandos.append(operadores.pop())
            operadores.append(token)
        elif token == '(':
            operadores.append(token)
        elif token == ')':
            while operadores and operadores[-1] != '(':
                operandos.append(operadores.pop())
            operadores.pop()  # Pop '('

        i += 1

    while operadores:
        operandos.append(operadores.pop())

    return ' '.join(operandos)


def test_thompson_to_text_prueba(expr, output_text_file):
    contadorEstados = 0

    estados = []
    alfabeto = []
    transiciones = []
    estado_inicial = 0
    estados_aceptacion = []

    grupos = []

    stri = expr.split()

    b = 0
    while b < len(stri):
        carac = stri[b]
        if carac not in "(|) ":
            if len(carac) > 1:
                for s in carac:
                    if s in alfabeto:
                        alfabeto.remove(s)
                        alfabeto.append(s)
                        continue
                    else:
                        alfabeto.append(s)

                grupos.append(carac)
            else:
                if b + 1 < len(stri) and b + 2 < len(stri):
                    if stri[b + 1] != '|' and stri[b + 2] != '|':
                        grupos.append(carac)

                elif b + 1 < len(stri):
                    if stri[b + 1] != '|':
                        grupos.append(carac)

                else:
                    grupos.append(carac)

                if carac in alfabeto:
                    alfabeto.remove(carac)
                    alfabeto.append(carac)
                else:
                    if carac != '*':
                        alfabeto.append(carac)

        elif carac == '|':
            if stri[b - 1] == carac:
                grupos.append(carac)
            else:
                grupos.append([alfabeto[len(alfabeto) - 2], alfabeto[len(alfabeto) - 1], carac])

        elif carac == '*':
            grupos.append(carac)

        b += 1

    linea = 0
    while linea < len(grupos):
        group = grupos[linea]
        if '|' in group:
            if len(group) > 1:
                if contadorEstados == 0:
                    nuevo_estado_inicial = contadorEstados
                    nuevo_estado_final = contadorEstados + 1
                    estados.append(nuevo_estado_inicial)
                    estados.append(nuevo_estado_final)
                    contadorEstados += 2

                else:
                    nuevo_estado_inicial = estados[contadorEstados - 1]
                    nuevo_estado_final = contadorEstados
                    estados.append(nuevo_estado_final)
                    contadorEstados += 1

                transiciones.append((nuevo_estado_inicial, group[0], nuevo_estado_final))
                transiciones.append((nuevo_estado_inicial, group[1], nuevo_estado_final))

        elif '*' in group:
            grupoAnterior = grupos[linea - 1]
            if '|' not in grupoAnterior:
                ultimaTransition = transiciones.pop()
                ultimoEstado = estados[-1]
                penUltimoEstado = estados[-2]

                nuevo_estado_inicial = penUltimoEstado
                nuevo_estado_grupo_anterior = ultimoEstado
                nuevo_estado_final = contadorEstados

                estados.append(nuevo_estado_final)

                transiciones.append((nuevo_estado_inicial, '𝜀', nuevo_estado_grupo_anterior))
                transiciones.append((nuevo_estado_grupo_anterior, ultimaTransition[1], nuevo_estado_grupo_anterior))
                transiciones.append((nuevo_estado_grupo_anterior, '𝜀', nuevo_estado_final))

                contadorEstados += 1

            else:
                ultimaTransition = transiciones.pop()
                penUltimaTransition = transiciones.pop()
                ultimoEstado = estados[-1]
                penUltimoEstado = estados[-2]

                nuevo_estado_inicial = penUltimoEstado
                nuevo_estado_grupo_anterior_inicial = ultimoEstado
                nuevo_estado_grupo_anterior_final = contadorEstados
                nuevo_estado_final = contadorEstados + 1

                estados.append(nuevo_estado_grupo_anterior_final)
                estados.append(nuevo_estado_final)

                transiciones.append((nuevo_estado_inicial, '𝜀', nuevo_estado_final))
                transiciones.append((nuevo_estado_inicial, '𝜀', nuevo_estado_grupo_anterior_inicial))
                transiciones.append((nuevo_estado_grupo_anterior_inicial, ultimaTransition[1], nuevo_estado_grupo_anterior_final))
                transiciones.append((nuevo_estado_grupo_anterior_inicial, penUltimaTransition[1], nuevo_estado_grupo_anterior_final))
                transiciones.append((nuevo_estado_grupo_anterior_final, '𝜀', nuevo_estado_grupo_anterior_inicial))
                transiciones.append((nuevo_estado_grupo_anterior_final, '𝜀', nuevo_estado_final))

                contadorEstados += 2

        else:
            for oper in group:
                if contadorEstados == 0:
                    nuevo_estado_inicial = contadorEstados
                    nuevo_estado_final = contadorEstados + 1
                    estados.append(nuevo_estado_inicial)
                    estados.append(nuevo_estado_final)
                    contadorEstados += 2

                else:
                    nuevo_estado_inicial = estados[contadorEstados - 1]
                    nuevo_estado_final = contadorEstados
                    estados.append(nuevo_estado_final)
                    contadorEstados += 1

                transiciones.append((nuevo_estado_inicial, oper, nuevo_estado_final))

        linea += 1

    estados_aceptacion.append(estados[-1])

    with open(output_text_file, 'w', encoding='utf-8') as file:
        file.write(f"ESTADOS = {{{', '.join(map(str, estados))}}}\n")
        file.write(f"SIMBOLOS = {{{', '.join(alfabeto)}}}\n")
        file.write(f"INICIO = {{{estado_inicial}}}\n")
        file.write(f"ACEPTACION = {{{', '.join(map(str, estados_aceptacion))}}}\n")
        transiciones_str = ', '.join([f"({t[0]}, {t[1]}, {t[2]})" for t in transiciones])
        file.write(f"TRANSICIONES = {{{transiciones_str}}}\n")

    return estados, alfabeto, transiciones, estado_inicial, estados_aceptacion


def simulacion_afd(afd, cadena):
    estados = afd[0]
    alfabeto = afd[1]
    transiciones = afd[2]
    estado_inicial = afd[3]
    estados_aceptacion = afd[4]

    mensajeError = "No cumple con el lenguaje"
    mensajeAprobacion = "Cumple con el lenguaje"


    for cad in cadena:
        if cad not in alfabeto:
            return mensajeError

    estado_actual = estado_inicial
    veces = 0
    numCadena = 0
    cad = "null"
    if len(cadena) != 0:
        cad = cadena[numCadena]

        for tran in transiciones:

            if estados.index(estado_actual) < estados.index(tran[0]):
                return mensajeError

            else:
                if estados.index(estado_actual) == estados.index(tran[0]) and cad == tran[1]:
                    estado_actual = tran[2]
                    if numCadena != len(cadena) - 1:
                        numCadena += 1
                        cad = cadena[numCadena]
                    else:
                        if estados[estados.index(estado_actual)] == len(estados) - 1:
                            estado_actual = estados[estados.index(estado_actual) + 1]
                            continue
                else:
                    if estados[estados.index(estado_actual)] == len(estados) - 1:
                        estado_actual = estados[estados.index(estado_actual) + 1]

    if estado_actual in estados_aceptacion:
        return mensajeAprobacion
    else:
        return mensajeError


def main():
    infix_regex = "(a|b)*aabb"
    cadena = "ababaabb"

    postfix_regex = shunting_yard_regex(infix_regex)
    print("Cadena convertida a postfix: " + postfix_regex)

    # Ejemplo de uso con expresión en notación postfix
    output_text_file = "afn.txt"
    afn = test_thompson_to_text_prueba(postfix_regex, output_text_file)
    print(f"Descripción del AFN guardada en '{output_text_file}'")

    estados = set(afn[0])
    alfabeto = set(afn[1])
    transiciones = set(afn[2])
    estado_inicial = {afn[3]}
    estados_aceptacion = {afn[4][0]}

    afd = dfn.exec(estados, alfabeto, estado_inicial, estados_aceptacion, transiciones)

    print(simulacion_afd(afd, cadena))


main()
