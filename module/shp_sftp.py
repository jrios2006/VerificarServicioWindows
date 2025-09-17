#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Conexión con el protocolo sftp
# es necesario la librería pysftp 
# pip install pysftp

# La primera vez es necesaria conectar mediante un cliente y generar una clave en un fichero
# .ssh/known_hosts
# En windows suele estar es c:\Users\Usuario\.ssh\known_hosts

# CrearCarpetaSFTP(credenciales, ruta)
# SubirFicheroSFTP(credenciales, carpeta, fichero, nombrefichero)
# BorrarFicheroSFTP(credenciales, carpeta, fichero)
# ListarArchivosSFTP(credenciales, carpeta)
# DescargarArchivoSFTP(credenciales, archivo, ruta = '/')
# VerificarFicheroSFTP(credenciales, archivo, ruta = '/')

import logging # para guardar un log
import sys
import pysftp
import os
import datetime
def CrearCarpetaSFTP(credenciales, ruta):
    '''
        Crea una carpeta o ruta en el servidor sFTP definido en el fichero de credenciales.
        TO DO: ver como meter contraseña de la clave privada si la hubiera
    '''
    Aux = False
    # El orden de la variable credencial debe venir así
    # [sftp_servidor, sftp_puerto, sftp_usuario, sftp_clave, sftp_claveprivada, sftp_raiz]
    sftp_servidor     = credenciales[0] 
    sftp_puerto       = credenciales[1] # 22 
    sftp_usuario      = credenciales[2] 
    sftp_clave        = credenciales[3] 
    sftp_claveprivada = credenciales[4] #  Clave si fuera necesario # Falta la contraseña de la clave si hubiera
    sftp_passclaveprivada = credenciales[5] 

	# Conectamos con el servidor SFTP
    # Ver los ficheros de clave si es necesario
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # conectamos
    try:
        # Creamos la conexion parametrizada (Falta añadir puerto y clave privada del certificado, junto con la clave publicas del servidor local)
        if os.path.isfile(sftp_claveprivada):
            sftp = pysftp.Connection(host=sftp_servidor, port=sftp_puerto, username=sftp_usuario, private_key=sftp_claveprivada, cnopts=cnopts)
        else:
            sftp = pysftp.Connection(host=sftp_servidor, port=sftp_puerto, username=sftp_usuario, password=sftp_clave, cnopts=cnopts)
        if not sftp.isdir(ruta):
            sftp.mkdir(ruta)
            Aux = True
        else:
            Cadena = "La carpeta %s ya existe en %s. No la creo." %(ruta, sftp_servidor)
            print(Cadena)
            logging.warning(Cadena)
        sftp.close()
    except:
        Cadena = "No consigo conectar con el servidor %s con el usuario %s" %(sftp_servidor, sftp_usuario)
        print(Cadena)
        logging.error(Cadena)
        e = sys.exc_info()
        logging.error(e)        
        print("Exception: {0}".format(e))        
    return Aux

def SubirFicheroSFTP(credenciales, carpeta, fichero, nombrefichero):
    '''
		Subo un fichero a un servidor SFTP prefijado mediante credenciales
		Debe subirse a la carpeta en el sitio SFTP. 
		Si no existe esta carpeta se debe de crear en el servidor
		fichero es el fichero local que subimos
		nombrefichero es el nombre del fichero por si se lo quiero cambiar en el servidor ftp
        carpeta no debe llevar / al final
	'''
    Aux = False
    # El orden de la variable credencial debe venir así
    # [sftp_servidor, sftp_puerto, sftp_usuario, sftp_clave, sftp_claveprivada, sftp_raiz]
    sftp_servidor     = credenciales[0] 
    sftp_puerto       = credenciales[1] # 22 
    sftp_usuario      = credenciales[2] 
    sftp_clave        = credenciales[3] 
    sftp_claveprivada = credenciales[4] #  Clave si fuera necesario
    sftp_passclaveprivada = credenciales[5] 

    logging.disable(logging.INFO)

	# Conectamos con el servidor SFTP
    # Ver los ficheros de clave si es necesario
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # conectamos, pero antes creo la carpeta en el servidor
    CrearCarpetaSFTP(credenciales, carpeta)
    try:
        if os.path.isfile(sftp_claveprivada):
            with pysftp.Connection(host=sftp_servidor, port=sftp_puerto, username=sftp_usuario, private_key=sftp_claveprivada, cnopts=cnopts) as sftp:
                localFilePath = fichero
                # Define the remote path where the file will be uploaded
                remoteFilePath = carpeta + "/" + nombrefichero
                sftp.put(localFilePath, remoteFilePath)
                Aux = True
        else:
            with pysftp.Connection(host=sftp_servidor, port=sftp_puerto, username=sftp_usuario, password=sftp_clave, cnopts=cnopts) as sftp:
                localFilePath = fichero
                # Define the remote path where the file will be uploaded
                remoteFilePath = carpeta + "/" + nombrefichero
                sftp.put(localFilePath, remoteFilePath)
                Aux = True
        sftp.close()
    except:
        Cadena = "No consigo subir al servidor %s el fichero %s" %(sftp_servidor, fichero)
        print(Cadena)
        logging.error(Cadena)
        e = sys.exc_info()
        logging.error(e)        
        print("Exception: {0}".format(e))
    logging.disable(logging.NOTSET)
    return Aux

def BorrarFicheroSFTP(credenciales, carpeta, fichero):
    '''
		Borro un fichero del servidor SFTP prefijado
		Si pongo carpeta intento ir a la ruta definida
		en la variable carpeta para borrar en esa ruta
	'''
    Aux = False
    # El orden de la variable credencial debe venir así
    # [sftp_servidor, sftp_puerto, sftp_usuario, sftp_clave, sftp_claveprivada, sftp_raiz]
    sftp_servidor     = credenciales[0] 
    sftp_puerto       = credenciales[1] # 22 
    sftp_usuario      = credenciales[2] 
    sftp_clave        = credenciales[3] 
    sftp_claveprivada = credenciales[4] #  Clave si fuera necesario
    sftp_passclaveprivada = credenciales[5] 

    logging.disable(logging.INFO)

	# Conectamos con el servidor SFTP
    # Ver los ficheros de clave si es necesario
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # conectamos
    try:
        # Creamos la conexion parametrizada (Falta añadir puerto y clave privada del certificado, junto con la clave publicas del servidor local)
        if os.path.isfile(sftp_claveprivada):
            sftp = pysftp.Connection(host=sftp_servidor, port=sftp_puerto, username=sftp_usuario, private_key=sftp_claveprivada, cnopts=cnopts)
        else:
            sftp = pysftp.Connection(host=sftp_servidor, port=sftp_puerto, username=sftp_usuario, password=sftp_clave, cnopts=cnopts)
        if sftp.isfile(carpeta + "/" + fichero):
            sftp.remove(carpeta + "/" + fichero)
            Aux = True
        else:
            Cadena = "No puedo borrar el fichero %s de la carpeta %s en el servidor %s." %(fichero, carpeta, sftp_servidor)
            print(Cadena)
            logging.warning(Cadena)
        sftp.close()
    except:
        Cadena = "No consigo conectar con el servidor %s con el usuario %s" %(sftp_servidor, sftp_usuario)
        print(Cadena)
        logging.error(Cadena)
        e = sys.exc_info()
        logging.error(e)        
        print("Exception: {0}".format(e))
    logging.disable(logging.NOTSET)
    return Aux

def ListarArchivosSFTP(credenciales, carpeta):
    '''
		Conecto con el servidor SFTP. Le paso las credenciales de acceso
		Devuelvo los ficheros que hay en su carpeta raiz
		Devuelvo una lista con dos valores
		El primer valor si ha habido o no errores en la conexiçon (True o False)
		El segundo valor es la lista de los ficheros que ha encontrado. 
        Si no hay nada devuelve lista vacía
	'''
    Aux = False
    ListaFicheros = []
    # El orden de la variable credencial debe venir así
    # [sftp_servidor, sftp_puerto, sftp_usuario, sftp_clave, sftp_claveprivada, sftp_raiz]
    sftp_servidor     = credenciales[0] 
    sftp_puerto       = credenciales[1] # 22 
    sftp_usuario      = credenciales[2] 
    sftp_clave        = credenciales[3] 
    sftp_claveprivada = credenciales[4] #  Clave si fuera necesario
    sftp_passclaveprivada = credenciales[5] 

    logging.disable(logging.INFO)

	# Conectamos con el servidor SFTP
    # Ver los ficheros de clave si es necesario
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # conectamos
    try:
        # Creamos la conexion parametrizada (Falta añadir puerto y clave privada del certificado, junto con la clave publicas del servidor local)
        if os.path.isfile(sftp_claveprivada):
            sftp = pysftp.Connection(host=sftp_servidor, port=sftp_puerto, username=sftp_usuario, private_key=sftp_claveprivada, cnopts=cnopts)
        else:
            sftp = pysftp.Connection(host=sftp_servidor, port=sftp_puerto, username=sftp_usuario, password=sftp_clave, cnopts=cnopts)
        if sftp.isdir(carpeta):
            Aux = True
            ListaFicheros = sftp.listdir(carpeta)
        sftp.close()
    except:
        Cadena = "No consigo conectar con el servidor %s con el usuario %s" %(sftp_servidor, sftp_usuario)
        print(Cadena)
        logging.error(Cadena)
        e = sys.exc_info()
        logging.error(e)        
        print("Exception: {0}".format(e))
    logging.disable(logging.NOTSET)
    return Aux, ListaFicheros

def DescargarArchivoSFTP(credenciales, archivo, ruta = '/'):
    '''
        Conecto con el servidor SFTP para descargar el archivo de la ruta
        Lo copio a la carpeta donde se ejecuta y la función devuelve una lista con dos valores
        Primer valor si ha habido o no error en la conexión ftp (True o False)
        True se ha descargado, False no se ha descargado
        Segundo valor el nombre del fichero que hemos descargado
        Vací­o si ha habido error
    '''
    Aux = False
    NombreFicheroLocal = ''
    # El orden de la variable credencial debe venir así
    # [sftp_servidor, sftp_puerto, sftp_usuario, sftp_clave, sftp_claveprivada, sftp_raiz]
    sftp_servidor     = credenciales[0] 
    sftp_puerto       = credenciales[1] # 22 
    sftp_usuario      = credenciales[2] 
    sftp_clave        = credenciales[3] 
    sftp_claveprivada = credenciales[4] #  Clave si fuera necesario
    sftp_passclaveprivada = credenciales[5] 

    logging.disable(logging.INFO)

	# Conectamos con el servidor SFTP
    # Ver los ficheros de clave si es necesario
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # conectamos
    try:
        # Creamos la conexion parametrizada (Falta añadir puerto y clave privada del certificado, junto con la clave publicas del servidor local)
        if os.path.isfile(sftp_claveprivada):
            sftp = pysftp.Connection(host=sftp_servidor, port=sftp_puerto, username=sftp_usuario, private_key=sftp_claveprivada, cnopts=cnopts)
        else:
            sftp = pysftp.Connection(host=sftp_servidor, port=sftp_puerto, username=sftp_usuario, password=sftp_clave, cnopts=cnopts)
        if sftp.isfile(ruta + "/" + archivo):
            sftp.get(ruta + "/" + archivo)
            Aux = True
            NombreFicheroLocal = archivo
        else:
            Cadena = "No puedo descargar el fichero %s del servidor %s" %(archivo, sftp_servidor)
            print(Cadena)
            logging.error(Cadena)
        sftp.close()
    except:
        Cadena = "No consigo conectar con el servidor %s con el usuario %s" %(sftp_servidor, sftp_usuario)
        print(Cadena)
        logging.error(Cadena)
        e = sys.exc_info()
        logging.error(e)        
        print("Exception: {0}".format(e))
    logging.disable(logging.NOTSET)
    return Aux, NombreFicheroLocal

def VerificarFicheroSFTP(credenciales, archivo, ruta = '/'):
    '''
        Función que nos dice si un archhivo está en un servidor SFTP
        en la ruta especificada. Devolverá True si lo encuentra y False
        si no lo encuentra
    '''
    Aux = False
    # El orden de la variable credencial debe venir así
    # [sftp_servidor, sftp_puerto, sftp_usuario, sftp_clave, sftp_claveprivada, sftp_raiz]
    sftp_servidor     = credenciales[0] 
    sftp_puerto       = credenciales[1] # 22 
    sftp_usuario      = credenciales[2] 
    sftp_clave        = credenciales[3] 
    sftp_claveprivada = credenciales[4] #  Clave si fuera necesario
    sftp_passclaveprivada = credenciales[5] 

	# Conectamos con el servidor SFTP
    # Ver los ficheros de clave si es necesario
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # conectamos
    try:
        # Creamos la conexion parametrizada (Falta añadir puerto y clave privada del certificado, junto con la clave publicas del servidor local)
        if os.path.isfile(sftp_claveprivada):
            sftp = pysftp.Connection(host=sftp_servidor, port=sftp_puerto, username=sftp_usuario, private_key=sftp_claveprivada, cnopts=cnopts)
        else:
            sftp = pysftp.Connection(host=sftp_servidor, port=sftp_puerto, username=sftp_usuario, password=sftp_clave, cnopts=cnopts)
        if sftp.isfile(ruta + "/" + archivo):
            Aux = True
        sftp.close()
    except:
        Cadena = "No consigo conectar con el servidor %s con el usuario %s" %(sftp_servidor, sftp_usuario)
        print(Cadena)
        logging.error(Cadena)
        e = sys.exc_info()
        logging.error(e)        
        print("Exception: {0}".format(e))        
    return Aux

def ListarArchivosSFTPconAtributos(credenciales, carpeta):
    '''
		Conecto con el servidor SFTP. Le paso las credenciales de acceso
		Devuelvo los ficheros que hay en su carpeta raiz
		Devuelvo una lista con dos valores
		El primer valor si ha habido o no errores en la conexiçon (True o False)
		El segundo valor es la lista de los ficheros que ha encontrado junto con la fecha de creación y ordenado. 
        Si no hay nada devuelve lista vacía
	'''
    Aux = False
    ListaFicheros = []
    Lista = []
    # El orden de la variable credencial debe venir así
    # [sftp_servidor, sftp_puerto, sftp_usuario, sftp_clave, sftp_claveprivada, sftp_raiz]
    sftp_servidor     = credenciales[0] 
    sftp_puerto       = credenciales[1] # 22 
    sftp_usuario      = credenciales[2] 
    sftp_clave        = credenciales[3] 
    sftp_claveprivada = credenciales[4] #  Clave si fuera necesario
    sftp_passclaveprivada = credenciales[5] 

    logging.disable(logging.INFO)

	# Conectamos con el servidor SFTP
    # Ver los ficheros de clave si es necesario
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    # conectamos
    try:
        # Creamos la conexion parametrizada (Falta añadir puerto y clave privada del certificado, junto con la clave publicas del servidor local)
        if os.path.isfile(sftp_claveprivada):
            sftp = pysftp.Connection(host=sftp_servidor, port=sftp_puerto, username=sftp_usuario, private_key=sftp_claveprivada, cnopts=cnopts)
        else:
            sftp = pysftp.Connection(host=sftp_servidor, port=sftp_puerto, username=sftp_usuario, password=sftp_clave, cnopts=cnopts)
        if sftp.isdir(carpeta):
            Aux = True
            ListaFicheros = sftp.listdir_attr(carpeta)
            ListaFicheros.sort(key=lambda x: x.st_mtime, reverse=True)
            for atributos in ListaFicheros:
                atime_timestamp = atributos.st_atime  # Valor de atime en segundos desde la época
                atime_datetime = datetime.datetime.fromtimestamp(atime_timestamp)
                mtime_timestamp = atributos.st_mtime  # Valor de atime en segundos desde la época
                mtime_datetime = datetime.datetime.fromtimestamp(mtime_timestamp)

                diccionario_atributos = {
                    'nombre': atributos.filename,
                    'size': atributos.st_size,
                    'uid': atributos.st_uid,
                    'gid': atributos.st_gid,
                    'mode': atributos.st_mode,
                    'atime': atime_datetime, #atributos.st_atime,
                    'mtime': mtime_datetime #atributos.st_mtime
                }
                Lista.append(diccionario_atributos)            
        sftp.close()
    except:
        Cadena = "No consigo conectar con el servidor %s con el usuario %s" %(sftp_servidor, sftp_usuario)
        logging.error(Cadena)
        e = sys.exc_info()
        logging.error(e)        
        #print("Exception: {0}".format(e))
    logging.disable(logging.NOTSET)
    return Aux, Lista