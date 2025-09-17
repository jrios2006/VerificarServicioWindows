#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Librería para trabajar con ficheros comprimidos
import py7zr
import os

def Comprimir7z(carpeta: str, nombre: str, password=''):
    '''Dado una carpeta, comprimo los ficheros de esta carpeta y genero un nuevo fichero
    en formato zip. Si relleno el password cifro el nuevo contenido con esta contraseña
    Devuelo True o False y si devuelvo True devuelvo la lista de los ficheros que he comprimido y si hay un error 
    devuelvo el error que me da
    Devuelvo estos atributos: Nombre (ruta relativa completa del fichero)
    EsDirectorio booleano que nos dice si es un directorio o no
    Size es el tamaño en bytes que ocupará el fichero
    SizeComprimido es el tamaño que he logrado comprimir
    CRC32 marca para verificar la descompresión
    Fecha Fecha en la que realizao la compresión
    '''
    Aux = False
    Diccionario = {}
    try:
        if password != '':
            with py7zr.SevenZipFile(nombre, 'w', password=password, header_encryption=True) as archive:
                archive.writeall(carpeta)
        else:
            with py7zr.SevenZipFile(nombre, 'w') as archive:
                archive.writeall(carpeta)
        # Lista para almacenar los detalles de los archivos comprimidos
        detalles_archivos = []
        if password != '':
            # Abre el archivo 7z en modo lectura
            with py7zr.SevenZipFile(nombre, mode='r', password=password) as archive:
                # Obtiene la lista de archivos en el archivo 7z
                #lista_archivos = archive.getnames()
                lista_archivos = archive.list()
                for archivo in lista_archivos:
                    detalles_archivo = {
                        "Nombre": archivo.filename,
                        "EsDirectorio" : archivo.is_directory,
                        "Size" : archivo.uncompressed,
                        "SizeComprimido" : archivo.compressed,
                        "CRC32" : archivo.crc32,
                        "Fecha" : archivo.creationtime
                    }
                    detalles_archivos.append(detalles_archivo)
            Diccionario['archivos'] = detalles_archivos
        else:
            with py7zr.SevenZipFile(nombre, mode='r') as archive:
                # Obtiene la lista de archivos en el archivo 7z
                #lista_archivos = archive.getnames()
                lista_archivos = archive.list()
                for archivo in lista_archivos:
                    detalles_archivo = {
                        "Nombre": archivo.filename,
                        "EsDirectorio" : archivo.is_directory,
                        "Size" : archivo.uncompressed,
                        "SizeComprimido" : archivo.compressed,
                        "CRC32" : archivo.crc32,
                        "Fecha" : archivo.creationtime
                    }
                    detalles_archivos.append(detalles_archivo)
            Diccionario['archivos'] = detalles_archivos
        Aux = True
    except Exception as e:
        Diccionario['error'] = e
        #print(f"Se produjo un error: {e}")    
    return Aux, Diccionario
