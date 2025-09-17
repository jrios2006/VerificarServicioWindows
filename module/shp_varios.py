import datetime

def add_fecha_archivo(nombre_fichero):
    '''
        Función que añade la fecha actual del sistema al final de un archivo de texto.

        Argumentos:
            nombre_fichero (str): Ruta del archivo de texto.

        Ejemplo de uso:
            add_fecha_archivo("mi_archivo.txt")
    '''

    # Obtener la fecha actual formateada
    fecha_hora_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Abrir el archivo en modo append (añadir al final)
    with open(nombre_fichero, "a") as archivo:
    # Escribir la línea con la fecha actual
        archivo.write(f"Reiniciando el servicio a las {fecha_hora_actual}\n")

def generar_tabla_html(fichero):
    '''Leer el contenido del fichero y lo invierte y me genera una tabla html con el contenido del fichero'''
    with open(fichero, 'r') as file:
        lineas = file.readlines()
    
    # Ordenar las líneas de manera inversa
    lineas_ordenadas = sorted(lineas, reverse=True)
    
    # Generar el código HTML para la tabla
    tabla_html = '<table border="1">\n'
    tabla_html += '  <tr><th>Linea</th></tr>\n'
    for linea in lineas_ordenadas:
        tabla_html += f'  <tr><td>{linea.strip()}</td></tr>\n'
    tabla_html += '</table>'
    
    return tabla_html