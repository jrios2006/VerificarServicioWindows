#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Librería para lanzar comandos del sistema operativo
import subprocess
import os

def EjecutarComando(Lista: str):
    '''
    Lista es una cadena de caracteres del comando a ejecutar
    Devuelvo si he podido ejecutar el comando. True o False
    En caso de error devuelvo el error que obtnefo en un diccionaro { "error" : "descricpcion del error"}
    '''
    Aux = False
    Diccionario = {}
    Comando = [palabra for palabra in Lista.split(' ') if palabra]
    print(Comando)
    try:
        # Ejecuta el comando expdp
        subprocess.run(Comando, check=True)
        Aux = True
    except subprocess.CalledProcessError as e:
        Diccionario['error'] = f"Error al ejecutar expdp: {e}"

    return Aux, Diccionario