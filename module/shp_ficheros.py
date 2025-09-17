#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	Librerí­a manejo de ficheros
#   CalcularHash(fichero)
#	ExisteFichero(archivo)
#   ExisteCarpeta(ruta, crear = False)
#   ConvertirBytes(num)
#   FileSize(archivo)
#   MoverFichero(origen, destino)
#   CopiarFichero(origen, destino)
#   BorrarFichero(archivo, log=True)
#   ListarArchivos(ruta = '.')
#   NombreyExtension(archivo)
#   ListarFicherosConPatron(ruta, extension, patron)
#   BuscarPalabraenArchivo(archivo, palabra)

import logging  # para guardar un log

def CalcularHash(fichero):
    ''' Calculo el hash de un fichero en formato hexdecimal para saber si un fichero ha cambniado y 
    lo debo de volver a procesar. Devuelvo el HASH y vacío en caso de que no exista el fichero.
    El valor que devulvo será 64 caracteres hexadecimales o Nulo'''
    import hashlib
    import os
    Aux = None
    if os.path.exists(fichero):
        sha256_hash = hashlib.sha256()
        with open(fichero, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                sha256_hash.update(chunk)
        Aux = sha256_hash.hexdigest()
    return Aux

def ExisteFichero(archivo):
    """
        Nos informa si existe o no el fichero.
        True si existe y False en caso contrario
    """
    import os
    Aux = False
    if (os.path.isfile(archivo)):
        Aux = True
    return Aux

def ExisteCarpeta(ruta, crear=False, EscribirLog = False):
    '''
      Devuelve cierto o falso si existe una ruta que le pasamos
      Si le decimos crear en el segundo parámetro, por defecto False
      la creamos si no e exite
    '''
    import os
    Aux = False
    try:
        os.stat(ruta)
        Aux = True
    except:
        if crear:
            try:
                os.makedirs(ruta)
                temporal = 'Carpeta ' + ruta + ' creada por el programa en local'
                if EscribirLog:
                    logging.warning(temporal)
                Aux = True
            except:
                if EscribirLog:
                    logging.error('No se ha logrado crear la carpeta en local')
    return Aux

def ConvertirBytes(num):
    """
        Convierte un número de bytes a texto MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def FileSize(archivo):
    '''
            Calcula el tamaño en byte de un fichero
        Devuelvo el tamaño y su descripción en texto    
        '''
    import os
    Aux = 0
    Texto = ''
    if os.path.isfile(archivo):
        file_info = os.stat(archivo)
        Aux = file_info.st_size
        Texto = ConvertirBytes(Aux)
    return Aux, Texto

def MoverFichero(origen, destino, EscribirLog = False):
    '''
      Mueve un fichero de ubicación desde la carpeta origen a destino
      en el sistema de fichero local
    '''
    import shutil
    import os
    Aux = False
    if os.path.exists(origen):
        ruta = shutil.move(origen, destino)
        temporal = 'El archivo ' + origen + ' ha sido movido a ' + destino + ' en local.'
        if EscribirLog:
            logging.info(temporal)
        Aux = True
    else:
        temporal = 'El archivo ' + origen + \
            ' no existe y no lo he podido mover con nombre ' + destino + ' en local.'
        if EscribirLog:
            logging.error(temporal)
    return Aux

def CopiarFichero(origen, destino):
    '''
                Copia un fichero de ubicación desde la carpeta origen a destino
                en el sistema de fichero local
        '''
    import shutil
    import os
    Aux = False
    if os.path.exists(origen):
        try:
            ruta = shutil.copy(origen, destino)
            temporal = 'El archivo ' + origen + ' ha sido copiado a ' + destino
            print(temporal)
            logging.info(temporal)
            Aux = True
        except shutil.Error:
            Cadena = 'Imposible copiar ' + origen + ' en ' + destino
            print(Cadena)
            logging.error(Cadena)
    else:
        temporal = 'El archivo ' + origen + \
            ' no existe y no lo he podido copiar con nombre ' + destino
        print(temporal)
        logging.error(temporal)
    return Aux

def BorrarFichero(archivo, log=True):
    """
      Borrar un fichero. Devulvo True si lo he conseguido borrar
      False si no lo he borrado porque no lo he encontrado
    """
    import os
    Aux = False
    if os.path.isfile(archivo):
        os.remove(archivo)
        temporal = 'El archivo ' + archivo + ' ha sido borrado en local.'
        #print(temporal)
        if log == True:
            logging.info(temporal)
        Aux = True
    else:
        temporal = 'El archivo ' + archivo + \
            ' no existe en el sistema de fichero local y no lo puedo borrar.'
        #print(temporal)
        logging.error(temporal)
    return Aux

def BorrarDirectorio(directorio, log=True):
    """
    Borrar un fichero. Devulvo True si lo he conseguido borrar
    False si no lo he borrado porque no lo he encontrado
    """
    import os
    import shutil

    Aux = False
    if os.path.isdir(directorio):
        os.rmdir(directorio)
        temporal = 'El directorio ' + directorio + ' ha sido borrado'
        print(temporal)
        if log == True:
            logging.info(temporal)
        Aux = True
    else:
        temporal = 'El directorio ' + directorio + \
            ' no existe en el sistema de fichero local y no lo puedo borrar.'
        print(temporal)
        logging.error(temporal)
    return Aux

def BorrarDirectorioRecursivo(directory):
    '''
      Dado un directorio elimina todas las carpetas y archivos queu contiene
    '''
    from pathlib import Path

    aux = False
    directory = Path(directory)
    for item in directory.iterdir():
        if item.is_dir():
            BorrarDirectorioRecursivo(item)
            aux = True
        else:
            item.unlink()
            aux = True
    directory.rmdir()
    return aux

def ListarArchivos(ruta='.', ext=''):
    '''
        Devuelvo una lista de los ficheros que hay en la carpeta ruta ordenados por antiguedad
        Por defecto es la ruta local
    '''
    from os import walk, listdir, path

    Aux = []

    if ExisteCarpeta(ruta):
        if ext == '':
            dir, subdirs, archivos = next(walk(ruta))
            Aux = archivos
            Aux.sort(key=lambda x: path.getmtime(path.join(ruta, x)))
        else:
            archivos = listdir(ruta)
            for archivo in archivos:
                if archivo.endswith(ext):
                    Aux.append(archivo)
            Aux.sort(key=lambda x: path.getmtime(path.join(ruta, x)))
    else:
        temporal = 'No existe la ruta ' + ruta + ' en el sistema de fichero local'
        print(temporal)
    '''
    print("Actual: ", dir)
    print("Subdirectorios: ", subdirs)
    print("Archivos: ", archivos)
    '''
    return Aux

def ListarSubCarpetas(ruta='.'):
    '''
        Devuelvo una lista de subcarpetas que hay en la carpeta ruta
        Por defecto es la ruta local
    '''
    from os import walk
    Aux = []
    if ExisteCarpeta(ruta):
        dir, subdirs, archivos = next(walk(ruta))
        Aux = subdirs
    else:
        temporal = 'No existe la ruta ' + ruta + ' en el sistema de fichero local'
        print(temporal)
        logging.error(temporal)
    return Aux

def NombreyExtension(archivo):
    '''
        Dado un archivo devuelvo el nombre y la extensión del mismo
        en una lista. ejemplo: ficherodeprueba.xlsx
        ['ficherodeprueba','.xlsx']
    '''
    import os
    nombreExtraido = ''
    extensionExtraido = ''
    if ExisteFichero(archivo):
        nombreExtraido, extensionExtraido = os.path.splitext(archivo)
    return nombreExtraido, extensionExtraido

def ListarFicherosConPatron(ruta, extension, patron, SoloDirectorioPrincipal=True):
    ''' Miro en la ruta y devuelvo una lista de los nombres de los ficheros que
    contienen ese patrón en el nombre. Además los ordeno por fecha de creación del fichero de más antiguo a más moderno.
    La variable SoloDirectorioPrincipal restringue donde buscamos si en todo la carpeta o solo en la raiz
    Devuelvo una lista con la estructura de cada elemento
    [('/tmp/RutaInicial/firma-DET.dat', 1690011486.467285)]
    Ojo verifico el tipo de datos que es y excluyo los que no sean texto
    '''
    import os
    import re
    import filetype
    ficheros_con_patron = []
    try:
        if SoloDirectorioPrincipal:
            for archivo in os.listdir(ruta):
                if os.path.isfile(os.path.join(ruta, archivo)) and archivo.endswith(extension) and re.search(patron, archivo):
                    fichero_completo = os.path.join(ruta, archivo)
                    kind = filetype.guess(fichero_completo)
                    if kind is None or kind.mime == 'text/plain':
                        ficheros_con_patron.append((fichero_completo, os.path.getctime(fichero_completo)))
        else:
            for root, _, archivos in os.walk(ruta):
                for archivo in archivos:
                    if archivo.endswith(extension) and re.search(patron, archivo):
                        fichero_completo = os.path.join(root, archivo)
                        kind = filetype.guess(fichero_completo)
                        if kind is None or kind.mime == 'text/plain':
                            ficheros_con_patron.append((fichero_completo, os.path.getctime(fichero_completo)))
        ficheros_con_patron.sort(key=lambda x: x[1])  # Ordenar por fecha de creación
    except FileNotFoundError:
        logging.error(f"La ruta '{ruta}' no existe.")
    return ficheros_con_patron

def BuscarPalabraenArchivo(archivo: str, frase: str):
    '''Busco si una frase está dentro de un archivo y devuelvo true o false'''
    import re
    Aux = False
    Diccionario = {}
    codificaciones = ['utf-8', 'latin-1']  # Lista de codificaciones a intentar
    for codificacion in codificaciones:
        try:
            with open(archivo, 'r', encoding=codificacion) as file:
                contenido = file.read()
                # Usar expresiones regulares para buscar la palabra exacta
                if re.search(r'\b' + re.escape(frase) + r'\b', contenido):
                    Aux = True  # La frase fue encontrada en el archivo
        except FileNotFoundError:
            Diccionario['error'] = f"El archivo '{archivo}' no fue encontrado."
        except UnicodeDecodeError:
            Diccionario['error'] = f"Error de decodificación al abrir el archivo '{archivo}' con codificación {codificacion}"
    return Aux, Diccionario
