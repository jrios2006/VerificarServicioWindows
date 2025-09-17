#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Librería para funciones con Oracle
# ObtenerDatos_Oracle_enJSON(credenciales, sql)
# EjecutarSQL_Oracle(credenciales, sql)
# RegistrarLogPeticiones(Credenciales, Data, Tabla = 'Log_Scripts')

# las credenciales son necesarias para saber los siguientes datos:
# [Host, port, sid, userBBDD, passwordBBDD]
# Es necesario tener instalado cx_Oracle
# Es necesario instalarlo pip install cx_oracle, pero debemos de tener instalado antes muchos paquetes
# InsertarRegistro (Credenciales, Tabla, Datos)

import logging
import cx_Oracle
import json
from datetime import datetime

#from lib.propias import obtener_valor_atributo, es_fecha_valida

def ListarCamposTableOracle(Credenciales, NombreTabla):
    '''Dada una base de datos definida en Credenciales, y una tabla definida en un esquema de esa base de datos.
    Devuelvo la lista de los campos de la tabla con su nombre, el tipo y el tamaño de loas variables que son string'''
    sql = f"SELECT column_name AS NOMBRE, data_type AS TIPO, char_length AS LONGITUD FROM all_tab_columns WHERE table_name = '{NombreTabla.upper()}'"    
    # print(sql)
    resultado, Datos = ObtenerDatos_Oracle_enJSON(credenciales=Credenciales, sql=sql)    
    return Datos

def InsertarRegistroOracle(Credenciales, Tabla, Datos, ListaCampos = []):
    '''Dado una base de datos definido en Credenciales con esta estructura
    ['Nombre Servidor', puerto, 'SID', 'Usuario', 'Contraseña']
    y una Tabla con un nombre intetna hacer un inersción en esa tabla 
    Datos es un diccionario de datos y cada atributo es un campo de la tabla
    Se presupone que has conseguido componer Datos según espera la base de datos
    Devuelvo si he conseguido ejecutar la consulta y errores si no lo he conseguido
    ListaCampos es un Json que especifica la lista de todos los campos que tiene la Tabla.
    Si no lo especifico lo calculo en el momento y si la especifico asumo que está bien lo que paso
    '''
    Aux = False
    Errores = {}

    host = Credenciales[0]
    port = Credenciales[1]
    sid = Credenciales[2]
    user = Credenciales[3]
    password = Credenciales[4]
    if not ListaCampos:
        # No he pasado la lista de campo de campos de la Tabla. La obtengo
        #print('No he pasao la lista, la calculo')
        ListaCamposTabla = ListarCamposTableOracle(Credenciales=Credenciales, NombreTabla=Tabla)
    else:
        ListaCamposTabla = ListaCampos
        #print('He pasado la lista, la uso')


    if isinstance(Datos, dict):
        DatosCopia = Datos.copy()  # Crear una copia del diccionario

        # Agregar el valor de la secuencia a la copia de los datos

        campos = ', '.join(DatosCopia.keys())
        valores = ', '.join([':%s' % (i+1) for i in range(len(DatosCopia))])
        query = f"INSERT INTO {Tabla} ({campos}) VALUES ({valores})"

        Data = {}
        for k, v in DatosCopia.items():
            if isinstance(v, dict) or isinstance(v, list):
                # Entiendo que tipo de dato en Oracle es correcto y lo formateo
                Data[k] = json.dumps(v, ensure_ascii=False)
            if isinstance(v, (int, float)):
                # El valor es un número Tengo que ver si la clave está en la lista de campos 
                # y si es un char convertirlo a string y si no dejarlo como está
                Tipo = obtener_valor_atributo(Lista=ListaCampos, AtributoaBuscar='NOMBRE', ValorABUscar=k, AtributoaDevolver='TIPO')
                if Tipo is not None and "CHAR" in Tipo:
                    Data[k] = str(v)
                else:
                    Data[k] = v
            if isinstance(v, str):
                #Tengo que descubir y el valor es una fecha
                if es_fecha_valida(v):
                    Data[k] = datetime.strptime(v, '%Y-%m-%d').date()
                else:
                    Data[k] = v
            if isinstance(v, bool):
                # pOr si hubiera alguna vez un booleano, lo convierto a número 1 cierto 0 Falso
                if v:
                    Data[k] = 1
                else:
                    Data[k] = 0
           
        #print(Data)
        DatosaInsertar = tuple(Data.values())
        del DatosCopia #Libero  la memoria de lo que no voy a usar más
        try:
            # Obtener el próximo valor de la secuencia
            dsn = cx_Oracle.makedsn(host=host, port=port, sid=sid)
            conexion = cx_Oracle.connect(user=user, password=password, dsn=dsn)
            cursor = conexion.cursor()

            cursor.execute(query, DatosaInsertar)
            conexion.commit()
            cursor.close()
            conexion.close()
            Aux = True
        except cx_Oracle.IntegrityError as integrity_error:
            Errores['error'] = integrity_error
            Errores['sql'] = query
            Errores['datos'] = DatosaInsertar
            logging.error(integrity_error)
            logging.error(Errores)
        except cx_Oracle.DatabaseError as db_error:
            Errores['error'] = db_error
            Errores['sql'] = query
            Errores['datos'] = DatosaInsertar
            logging.error(db_error)
            logging.error(Errores)
        except Exception as general_error:
            Errores['error'] = general_error
            Errores['sql'] = query
            Errores['datos'] = DatosaInsertar
            logging.error(general_error)
            logging.error(Errores)
    else:
        Error = 'Datos como parámetros deben ser un diccionario'
        Errores['error'] = Error
        logging.error(Error)
        logging.error(Errores)

    return Aux, Errores

def ObtenerDatos_Oracle_enJSON(credenciales: list, sql: str) -> tuple:
    ''' Dada una base de datos definida en credenciales trata de ejecutar una sentencia sql
    Devuelvo una tupla donde el primer parámetros es True o False y nos dice si se ha podido ejecutar
    la consulta, el segundo parámetros contendrá los registros asociados a esa consulta o el error
    que reporta la librería en caso de no poder conectar
    Errores típicos:
    No sabemos el nombre del servidor: ORA-12545: La conexión ha fallado porque el host destino o el objeto no existen
    No es el puerto adecuado de conexión: ORA-12541: TNS:no hay ningún listener
    No sabemos el esquema o base de datos: ORA-12505: TNS:el listener no conoce actualmente el SID proporcionado en el descriptor de conexión
    Nos hemos confundido con el usuario o contraseña: ORA-01017: nombre de usuario/contraseña no válidos; conexión denegada
    Si el comando sql no está bien escrito: ORA-00933: comando SQL no terminado correctamente
    '''
    Aux = False # Es lo que voy a devolver
    DatosConsulta = [] # Es lo que voy a devolver en la consulta
    host = credenciales[0] # Nombre del servidor donde accedemos
    port = credenciales[1] #Puerto por el cual accedemos
    sid = credenciales[2] # Base de datos
    user = credenciales[3] # Usuario de la base de datos
    password = credenciales[4] # Contraseña de la base de datos
    #Elimino el caracter ; de la sentencia sql que da error
    sql = sql.replace(';','')
    #print(credenciales)
    try: 
        # Establece la conexión con el esquema, el nombre de host y el puerto
        dsn = cx_Oracle.makedsn(host=host, port=port, sid=sid)
        connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
        #print(connection.version)
        # Crea un objeto cursor
        cursor = connection.cursor()
        # Ejecuta la consulta SQL
        cursor.execute(sql)
        # Recupera los resultados
        rows = cursor.fetchall()
        # Obtiene las columnas del cursor
        columns = [column[0] for column in cursor.description]
        # Procesa los resultados
        for row in rows:
            result = dict(zip(columns, row))
            # Cuando encontramos problemas en serializar
            # Convierte los objetos datetime a cadenas
            for key, value in result.items():
                if isinstance(value, datetime):
                    result[key] = value.strftime('%Y-%m-%d %H:%M:%S')        
            DatosConsulta.append(result)
        # Cierra el cursor y la conexión
        cursor.close()
        connection.close()
        Aux = True
    except cx_Oracle.DatabaseError as e:
        #print(e)
        #print(type(e))
        DatosConsulta.append(str(e)) # Así no guardo cx_Oracle._Error object sino un str
    return Aux, DatosConsulta

def EjecutarSQL_Oracle(credenciales: list, sql: str) -> tuple:
    ''' Dada una base de datos definida en credenciales trata de ejecutar una sentencia sql
    Devuelvo True o False y nos dice si se ha podido ejecutar
    la consulta
    Errores típicos:
    No sabemos el nombre del servidor: ORA-12545: La conexión ha fallado porque el host destino o el objeto no existen
    No es el puerto adecuado de conexión: ORA-12541: TNS:no hay ningún listener
    No sabemos el esquema o base de datos: ORA-12505: TNS:el listener no conoce actualmente el SID proporcionado en el descriptor de conexión
    Nos hemos confundido con el usuario o contraseña: ORA-01017: nombre de usuario/contraseña no válidos; conexión denegada
    Si el comando sql no está bien escrito: ORA-00933: comando SQL no terminado correctamente
    '''
    Aux = False # Es lo que voy a devolver
    DatosConsulta = {} # Es lo que voy a devolver en la consulta
    host = credenciales[0] # Nombre del servidor donde accedemos
    port = credenciales[1] #Puerto por el cual accedemos
    sid = credenciales[2] # Base de datos
    user = credenciales[3] # Usuario de la base de datos
    password = credenciales[4] # Contraseña de la base de datos
    #Elimino el caracter ; de la sentencia sql que da error
    sql = sql.replace(';','')
    try: 
        # Establece la conexión con el esquema, el nombre de host y el puerto
        dsn = cx_Oracle.makedsn(host=host, port=port, sid=sid)
        connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
        #print(connection.version)
        # Crea un objeto cursor
        cursor = connection.cursor()
        # Ejecuta la consulta SQL
        cursor.execute(sql)    
        # Confirmar los cambios realizados (solo si estás utilizando transacciones)
        connection.commit()        
        cursor.close()
        connection.close()
        Aux = True
    except cx_Oracle.DatabaseError as e:
        logging.error(e)
        DatosConsulta['error'] = e
    return Aux, DatosConsulta

def ExisteTablaOracle(Credenciales, tabla):
    '''Dado un esquema de Oracle accesible mediante Credenciales no dice si existe una tabla en ese esquema. 
    Devuelvo True o False'''
    Aux = False
    sql = f"SELECT COUNT(*) AS Contar FROM all_tables WHERE table_name = '{tabla.upper()}' AND OWNER = '{Credenciales[3].upper()}'"
    print('******************')
    print(sql)
    print(Credenciales)
    print(tabla)
    print('******************')
    resultado, datos = ObtenerDatos_Oracle_enJSON(credenciales=Credenciales, sql=sql)
    print(resultado, datos)
    if resultado:
        # [{'CONTAR': 1}] si existe [{'CONTAR': 0}] No existe
        if datos[0]['CONTAR'] == 1:
            Aux = True
    return Aux

def CrearTablaOracle(Credenciales, Tabla, ListaSQL):
    '''Dada una base de datos (esquema) de Oracle creo una base de datos dependiendo de las consultas definidas en 
    SQL
    '''
    Aux = False
    AuxIntermedio = False
    if not ExisteTablaOracle(Credenciales=Credenciales, tabla=Tabla):
        #print('Empiezo a crear la base de datos')
        for sql in ListaSQL:
            print(sql)
            if EjecutarSQL_Oracle(credenciales=Credenciales, sql=sql):
                AuxIntermedio = True
                print('Verifica que se ha ejecutado')
            else:
                AuxIntermedio = False
                print('Mira porque no se ejecuta esta sentencia')
        if AuxIntermedio:
            Aux = AuxIntermedio
    else:
        # Ya está creada no hago nada
        Aux = True
        print('La tabla debería de existir')
    return Aux

def RegistrarLog(cadena, tipo='info', imprimir=True, RegistrarLog=True):
    '''
        Dado una cadena de log los que hago es registrslo en varios ficheros
        Uno es el fichero de log y otro el definido en la variable logFile
    '''
    if tipo == 'info':
        print(cadena)
        logging.info(cadena)
    if tipo == 'warning':
        print(cadena)
        logging.warning(cadena)
    if tipo == 'error':
        print(cadena)
        logging.error(cadena)
