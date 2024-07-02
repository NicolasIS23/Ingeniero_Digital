from threading import excepthook
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
from subprocess import run, PIPE
import sys
import xlsxwriter
import requests
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import locale
import requests
from requests.models import Response
import matplotlib.pyplot as plt
import json
from plotly.colors import n_colors
import plotly.graph_objects as go
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
import gmaps
import gmaps.datasets
import urllib.request
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from heapq import nsmallest
from scipy.spatial import distance
import time
import requests
import pandas as pd
from plotly.colors import n_colors
import plotly.graph_objects as go
import numpy as np
from fpdf import FPDF
from datetime import datetime
import locale
import textwrap
from fastapi import FastAPI, File, UploadFile, HTTPException
import geopandas as gpd
import psycopg2
import folium
from PIL import Image
import io
import os
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime
import random


app = FastAPI(title= 'Ingeniero Digital', description = 'API ingeniero Digital')


@app.get('/API/GenerarInforme/PROPERTY-PERSONALIZADO')
async def StandAlone(municipio:str = None, direccion:str = None, latitud:str = None, longitud:str = None, nit: str = None, valor_a_asegurar: str = None, chip: str = None, consecutivo_CIRO: str = None):
    
    try:
        if direccion is None or nit is None:
            return HTTPException(status_code=100, detail="No se llenaron los campos obligatorios")
    except HTTPException as e:
        raise e
    
    is_cc = False
        
    if valor_a_asegurar == None:
        valor_a_asegurar = "No especificado"
    
    if consecutivo_CIRO == None:
        consecutivo_CIRO = "No especificado"

    inicio = time.time()
    #ESTANDARIZACIÓN NIT
    if type(nit) != type(None):
        nit = nit.replace('.','')
        nit = nit.replace(',','')
    
    if len(nit) != 9:
        is_cc = True
        print("Se trata de un documento de identidad")
        
    print(f"Es cédula? {is_cc}")
    
    #ALMACENAR VARIABLES 

    workbook = xlsxwriter.Workbook('Archivos/save2.xlsx')
    worksheet = workbook.add_worksheet('first')

    worksheet.write(1,0, direccion)
    worksheet.write(1,1, municipio)
    worksheet.write(1,2, nit)
    worksheet.write(1,3, valor_a_asegurar)
    worksheet.write(1,4, latitud)
    worksheet.write(1,5, longitud)
    worksheet.write(1,6, chip)

    worksheet.write(0,0, 'direccion')
    worksheet.write(0,1, 'municipio')
    worksheet.write(0,2, 'nit')
    worksheet.write(0,3, 'valor')
    worksheet.write(0,4, "latitud")
    worksheet.write(0,5, "longitud")
    worksheet.write(0,6, "CHIP")
    
    workbook.close()
    
    print(f"La dirección del predio es: {direccion}")
    print(f"El NIT de la empresa es: {nit}")

    #Imprimir el mes con un 0 antes

    now = datetime.now()
    if len(str(now.month)) == 1:
        here = str(0) + str(now.month)

    fecha_actual = now.strftime('%d/%m/%Y')
    sector = pd.read_csv("Archivos/barrios_bogota.csv", sep=';') #Base con los datos de barrio, UPZ y localidad

    #Biblioteca de Modelos CATASTRO 

    construccion = None

    ConstruccioN = [None,None,None]
    pais = 'Colombia'
    asunto = 'Prueba'
    modelo = 'Catastro'


    con = psycopg2.connect(
        database="ingdigital", 
        user="postgres", 
        password="Bolivar2021",
        host="35.153.192.47", 
        port=8081)
    #Leer datos de entrada
    save2 = pd.read_excel("Archivos/save2.xlsx") 
    #Base de datos con los tipos de uso en un predio
    TUso = pd.read_excel(r"Archivos/TPredioV1.0.xls", sheet_name='30.Dominios  ') 

    DireccioN = []
    lotes = []
    
    #LIMPIAR INFORMACIÓN DE ENTRADA
    #ELIMINAR TILDES DE DIRECCION Y MUNICIPIO
    for i in range(0, len(save2)):
        direccion = save2.iloc[i].iloc[0]
        if not str(save2.iloc[i].iloc[0]) == 'nan':
            #direccion = direccion.replace(",", "")
            direccion = direccion.upper()
            direccion = direccion.replace("Á","A")
            direccion = direccion.replace("É","E")
            direccion = direccion.replace("Í","I")
            direccion = direccion.replace("Ó","O")
            direccion = direccion.replace("Ú","U")
            DireccioN.append(direccion)
        else:
            DireccioN.append('None')

    MunicipiO = []
    for i in range(0,len(save2)):
        municipio = save2.iloc[i].iloc[1]
        if str(municipio) == 'nan':
            municipio = "BOGOTA"
        if not (str(municipio) == 'nan' or type(municipio) == None):
            municipio = municipio.upper()
            municipio = municipio.replace("Á", "A")
            municipio = municipio.replace("É", "E")
            municipio = municipio.replace("Í", "I")
            municipio = municipio.replace("Ó", "O")
            municipio = municipio.replace("Ú", "U")
        MunicipiO.append(municipio)

    #QUITAR PUNTOS Y COMAS DEL NIT
    if is_cc == False:
        NiT = []
        for i in range(0,len(save2)):
            nit = save2.iloc[i].iloc[2]
            if not (type(nit) == type(None) or str(nit) == 'nan'):
                nit = int(str(nit).replace('.',''))
                nit = int(str(nit).replace(',',''))
            NiT.append(nit)
    ValoR = []
    for i in range(0,len(save2)):
        valor = save2.iloc[i].iloc[3]
        ValoR.append(valor)
    LatituD = []
    for i in range(0,len(save2)):
        gamma = save2.iloc[i].iloc[4]
        if not (str(gamma) == 'nan' or type(gamma) == type(None)):
            gamma = float(str(gamma).replace(',','.'))
        LatituD.append(gamma) #
    LongituD = []
    for i in range(0,len(save2)):
        eta = save2.iloc[i].iloc[5]
        if not (str(eta) == 'nan' or type(eta) == type(None)):
            eta = float(str(eta).replace(',','.'))
        LongituD.append(eta)
    ChiP = []
    for i in range(0,len(save2)):
        chip = save2.iloc[i].iloc[6]
        ChiP.append(chip)
    for i in sector["NOMBRE_BARRIO"]:
        if i in DireccioN[0]:
            DireccioN[0] = DireccioN[0].replace(i, "")
            break
        
    
    #ESTANDARIZADOR

    CarrerA = ["CARRERA", "CRA", "K", "KRA", "K.", "CRA.", "KRA.", "KR.", "CR"]
    CallE = ["CLL", "CALLE", "CL.", "CLL.", "C.", "KALLE"]
    DiagonaL = ["DIAGONAL", "DG.", "DIAG.", "DIAG", "D.", "DGL", "DGL."]
    TransversaL = ["TRANSVERSAL", "TV.", "TR.", "T.", "TRANS.", "TRR", "T", "TRANS", "TR"]
    AvenidA = ["AVENIDA", "AV.", "A.", "AVD", "AVDA"]
    AvenidaCalle = ["AV CL", "AC."]
    AvenidaCarrera = ["AK.", "AV KR"]
    Bodega = ["BODEGA", "BG.", "BOD", "BOD.", "BODEGAS", "BOEGAS", "BODG2", "BOEGA", "BD", "PLANTA"]
    Local = ["LOCAL", "LC.", "LOC", "LOCALES", "LOC."]
    Interior = ["INTERIOR", "INT", "INT.", "IN."]
    Apartamento = ["APT.", "AP.", "APARTAMENTO", "APT", "APTO", "APTO."]
    Oficina = ["OFICINA", "OF.", "OFICINAS", "CONSULTORIO", "CONSULT.", "CONSULT", "0FIC", "OFOF", "0F", "OFC", "OFC."]
    Torre = ["TORRE", "TO."]
    Lote = ["LOTE", "LOT", "LOT."]
    for i in range(0,len(DireccioN)):
        for j in range(0, len(CarrerA)):
            if CarrerA[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(CarrerA[j] + " ", "KR ")
                break
        for j in range(0, len(CallE)):
            if CallE[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(CallE[j] + " ", "CL ")
                break
        if not " BIS" in DireccioN[i]:
            if "BIS" in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("BIS", " BIS")
        if "–" in DireccioN[i]:
           DireccioN[i] = DireccioN[i].replace("–", " ")
        if "ª" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("ª", "")
        if "#" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" #", " ")
        elif "#" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("#", "")
        elif "NO." in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" NO. ", " ")
        elif "N°" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" N° ", " ")
        elif "Nº" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" Nº ", " ")
        elif "NO" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" NO ", " ")
        elif "NO." in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("NO.", "")
        elif "N°" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("N°", "")
        elif "Nº" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("Nº", "")
        if "-" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" - ", " ")
        elif "-" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("-", " ")
        if "—" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" — ", " ")
        elif "—" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("—", " ")
        if "−" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" − ", " ")
        elif "−" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("−", " ")
        if "–" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" – ", " ")
        elif "–" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("–", " ")
        for j in range(0, len(DiagonaL)):
            if DiagonaL[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(DiagonaL[j] + " ", "DG ")
                break
        for j in range(0, len(TransversaL)):
            if TransversaL[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(TransversaL[j] + " ", "TV ")
                break
        for j in range(0, len(AvenidA)):
            if AvenidA[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(AvenidA[j] + " ", "AV ")
                break
        for j in range(0, len(Bodega)):
            if Bodega[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(Bodega[j] + " ", "BG ")
        for j in range(0, len(Local)):
            if Local[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(Local[j] + " ", "LC ")
        for j in range(0, len(Apartamento)):
            if Apartamento[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(Apartamento[j] + " ", "AP ")
        for j in range(0, len(Oficina)):
            if Oficina[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(Oficina[j] + " ", "OF ")
            elif Oficina[j] in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace(Oficina[j], "OF ")
        for j in range(0, len(Torre)):
            if Torre[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(Torre[j] + " ", "TO ")
        for j in range(0, len(Lote)):
            if Lote[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(Lote[j] + " ", "LT ")
        for j in range(0, len(Interior)):
            if Interior[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(Interior[j] + " ", "IN ")
                break
        for j in range(0, len(AvenidaCalle)):
            if AvenidaCalle[j] in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace(AvenidaCalle[j] + " ", "AC ")
                break
        for j in range(0, len(AvenidaCarrera)):
            if AvenidaCarrera[j] in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace(AvenidaCarrera[j] + " ", "AK ")
                break
        if "   " in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("   ", " ")
        if "  " in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("  ", " ")
        if "   " in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("   ", " ")
        if "  " in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("  ", " ")
        if "  " in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("  ", " ")
     
    for i in range(0, len(DireccioN)):
        componentes = DireccioN[i].split()
        print(componentes)
        if len(componentes) > 7:
            DireccioN[i] = ' '.join(componentes[:6])
    print(f"{DireccioN}")
    
    direccion_basica = direccion.split(maxsplit=6)
    direccion_basica = ' '.join(direccion_basica[:6])
    print(direccion_basica)
    

    '''
    Apiest = 'http://ec2-35-153-192-47.compute-1.amazonaws.com:8092/API/1a1'
    args = {'Ciudad' : 'Bogota', 'Direccion': direccion}
    response = requests.get(Apiest, params = args)
    DireccioN[0] = response.json()['DIRECCION_ESTANDAR']['0']
    nDireccion = []
    for i in DireccioN[0]:
        nDireccion.append((i))
        
    letras = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "O", "P", "Q"]
    a = 0
    for i in ((DireccioN[0])):
        for j in range (len(letras)):
            try:
                if letras[j] == i and nDireccion[a-1] == " ":
                    nDireccion.pop(a-1)
            except:
                pass
        a = a+1
    DireccioN[0] = "".join(nDireccion)
    '''


    #Lectura desde PostgreSQL
    sql_predios = f"""SELECT * FROM predios_0321
    WHERE STRPOS(REPLACE("PreDirecc", '  ', ' '), '{DireccioN[0]}') > 0"""
    predios = pd.read_sql(sql_predios, con) 
    pd.set_option('display.max_columns', 100)
    predios
    
    if len(predios) == 0:
        sql_predios = f"""SELECT * FROM predios_0321
        WHERE STRPOS('{ChiP[0]}', REPLACE("PreChip", ' ', '')) > 0"""
        predios = pd.read_sql(sql_predios, con)     

    U = 0 #Variable para seleccionar la fila de la tabla de predios de una dirección

    if "BG" in DireccioN[0]: #A veces aparece IN en vez de BG
        if len(predios) == 0:
            DireccioN[0] = DireccioN[0].replace("BG", "IN")
            sql_predios = f"""SELECT * FROM predios_0321
    WHERE REPLACE("PreDirecc", '  ', ' ') = '{DireccioN[0]}'"""
            predios = pd.read_sql(sql_predios, con)

    if len(predios) == 0:
        Letras = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "O", "P", "Q"]
        for i in range(0,len(DireccioN)):
            for j in range(0, len(Letras)):
                if Letras[j] in DireccioN[i].split():
                    DireccioN[i] = DireccioN[i].replace(" " + Letras[j], Letras[j])
                    sql_predios = f"""SELECT * FROM predios_0321
    WHERE REPLACE("PreDirecc", '  ', ' ') = '{DireccioN[0]}'"""
                    predios = pd.read_sql(sql_predios, con)

    if len(predios) == 0:
        if "BIS" in DireccioN[0]:
            DireccioN[0] = DireccioN[0].replace("BIS", "BIS ")
            sql_predios = f"""SELECT * FROM predios_0321
    WHERE REPLACE("PreDirecc", '  ', ' ') = '{DireccioN[0]}'"""
            predios = pd.read_sql(sql_predios, con)

    if len(predios) == 0:
        sql_predios = f"""SELECT * FROM predios_0321
        WHERE STRPOS(REPLACE("PreDSI", '  ', ' '), '{DireccioN[0]}') > 0"""
        predios = pd.read_sql(sql_predios, con) 
        if len(predios) == 0:
            sql_predios = f"""SELECT * FROM predios_0321
        WHERE STRPOS('{DireccioN[0]}', REPLACE("PreDSI", '  ', ' ')) > 0"""
            predios = pd.read_sql(sql_predios, con) 

    if not len(predios) == 0:
        sql_lotes = f"""SELECT * FROM lotes_0321
            WHERE STRPOS("LOTCODIGO", '{'00' + str(predios.iloc[U]["Barmanpre"])}') = 1"""
        lotes = gpd.GeoDataFrame.from_postgis(sql_lotes, con)  

    if not len(predios) == 0:
        if len(str(predios.iloc[U]["PreCCons"])) == 1:
            sql_construccion = f"""SELECT * FROM construccion_tabla_0321
                WHERE STRPOS("ConCodigo", '{'00' + str(predios.iloc[U]["Barmanpre"]) + '00' + str(predios.iloc[U]["PreCCons"])}') = 1"""
            construccion = gpd.GeoDataFrame.from_postgis(sql_construccion, con)
        elif len(str(predios.iloc[U]["PreCCons"])) > 1:
            sql_construccion = f"""SELECT * FROM construccion_tabla_0321
                WHERE STRPOS("ConCodigo", '{'00' + str(predios.iloc[U]["Barmanpre"]) + '0' + str(predios.iloc[U]["PreCCons"])}') = 1"""
            construccion = gpd.GeoDataFrame.from_postgis(sql_construccion, con)

    if not (str(LatituD[0]) == 'nan' or str(LongituD[0]) == 'nan'):
        if len(predios) == 0:
            if type(LatituD[0]) == str:
                LatituD[0] = LatituD[0].replace(',', '.')
            if type(LongituD[0]) == str:
                LongituD[0] = LongituD[0].replace(',', '.')
            sql_lotes2 = f"""SELECT * FROM lotes_0321
            WHERE ST_Intersects(
                geom,
                ST_Transform(ST_GeometryFromText('POINT({LongituD[0]} {LatituD[0]})', 4686), 4686)
                );
            """
            lotes2 = gpd.GeoDataFrame.from_postgis(sql_lotes2, con)
            if not len(lotes2) == 0:
                lotes = lotes2
            if not len(lotes2) == 0:
                sql_construccion2 = f"""SELECT * FROM construccion_tabla_0321
                WHERE ST_Intersects(
                    ST_Centroid(geom),
                    ST_GeomFromText('{lotes['geom'].iloc[0]}', 4686)
                    );
                """
                construccion2 = gpd.GeoDataFrame.from_postgis(sql_construccion2, con)
                if not len(construccion2) == 0:
                    construccion = construccion2

                #predios
                sql_predios = f"""SELECT * FROM predios_0321
                    WHERE STRPOS('{lotes['LOTCODIGO'][0]}', CONCAT('0','0',"Barmanpre")) = 1"""
                predios = pd.read_sql_query(sql_predios, con)
                DireccioN[0] = predios["PreDirecc"].iloc[0]

    if len(predios) == 0:
        geolocalizador_entrada = {'direccion': DireccioN[0],
                'ciudad': MunicipiO[0].upper().replace('Á', 'A'), 'f': 'json'}

        # GENERACIÓN DE LAS COORDENADAS A PARTIR DE LA DIRECCIÓN
        geolocalizador = 'https://www.segurosbolivar.com/arcgis/rest/services/Servicios_SB/geoEsri/GPServer/geoEsri/execute'
        geolocalizador_salida = requests.get(url=geolocalizador,
                        headers={'content-type': 'application/json'},
                        params=geolocalizador_entrada)
        print(f"La salida de la geolocalización es: {geolocalizador_salida.json()}")
        try:
            if "results" in geolocalizador_salida.json() and geolocalizador_salida.json()["results"]:
                pass
            else:
                print("Respuesta de geolocalización no válida")
                return HTTPException(status_code = 105, detail=f"Dirección: {direccion}, NIT: {nit}. Respuesta de geolocalización no válida")
        except HTTPException as e:
            return e
        if not len(geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')) == 1:
            try:
                LatituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[0]
                LongituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[1]
            except:
                urlGeocode = 'http://api.lupap.co/v2/co/'
                temp = requests.get(urlGeocode + 'bogota' + '?a=' + direccion+'&key=3bee5f0a19bf31eb0fa8a70376a4c61eb34d9ba8')
                LatituD[0] = temp.json()['response']['geometry']['coordinates'][1]
                LongituD[0] = temp.json()['response']['geometry']['coordinates'][0]
                
            sql_lotes2 = f"""SELECT * FROM lotes_0321
            WHERE ST_Intersects(
                geom,
                ST_Transform(ST_GeometryFromText('POINT({LongituD[0]} {LatituD[0]})', 4686), 4686)
                );
            """
            lotes2 = gpd.GeoDataFrame.from_postgis(sql_lotes2, con)
            if not len(lotes2) == 0:
                lotes = lotes2
            if not len(lotes2) == 0:
                sql_construccion2 = f"""SELECT * FROM construccion_tabla_0321
                WHERE ST_Intersects(
                    ST_Centroid(geom),
                    ST_GeomFromText('{lotes['geom'].iloc[0]}', 4686)
                    );
                """
                construccion2 = gpd.GeoDataFrame.from_postgis(sql_construccion2, con)
                if not len(construccion2) == 0:
                    construccion = construccion2 

                #predios
                sql_predios = f"""SELECT * FROM predios_0321
                    WHERE STRPOS('{lotes['LOTCODIGO'][0]}', CONCAT('0','0',"Barmanpre")) = 1"""
                predios = pd.read_sql_query(sql_predios, con)
                try:
                    if len(predios) > 0:
                        DireccioN[0] = predios["PreDirecc"].iloc[0]
                    else:
                        raise HTTPException(status_code=103, detail=f"Dirección: {direccion}, NIT: {nit}. No hay información en las bases de datos")
                except HTTPException as e:
                    return e
            if len(lotes2) == 0:
                sql_lotes3 = f"""SELECT * FROM lotes_0321
                WHERE ST_Distance(
                    geom,
                    ST_Transform(ST_GeometryFromText('POINT({LongituD[0]} {LatituD[0]})', 4686), 4686)
                    ) < 0.0002
                ORDER BY
                geom <-> ST_GeometryFromText('POINT({LongituD[0]} {LatituD[0]})', 4686):: geometry
                LIMIT 1;
                """
                lotes3 = gpd.GeoDataFrame.from_postgis(sql_lotes3, con)
                if not len(lotes3) == 0:
                    lotes = lotes3
                if not len(lotes3) == 0:
                    sql_construccion2 = f"""SELECT * FROM construccion_tabla_0321
                    WHERE ST_Intersects(
                        ST_Centroid(geom),
                        ST_GeomFromText('{lotes['geom'].iloc[0]}', 4686)
                        );
                    """
                    construccion2 = gpd.GeoDataFrame.from_postgis(sql_construccion2, con)
                    if not len(construccion2) == 0:
                        construccion = construccion2 

                    #predios
                    sql_predios = f"""SELECT * FROM predios_0321
                        WHERE STRPOS('{lotes['LOTCODIGO'][0]}', CONCAT('0','0',"Barmanpre")) = 1"""
                    predios = pd.read_sql_query(sql_predios, con)
                    if len(predios["PreDirecc"]) > 0:
                        DireccioN[0] = predios["PreDirecc"].iloc[0]

    #Se vuelve a intentar con la dirección sin estandarizar

    if len(predios) == 0:
        DireccioN[0] = save2.iloc[0].iloc[0] 
        if not str(save2.iloc[i].iloc[0]) == 'nan':
            DireccioN[0] = DireccioN[0].upper()
            DireccioN[0] = DireccioN[0].replace("Á","A")
            DireccioN[0] = DireccioN[0].replace("É","E")
            DireccioN[0] = DireccioN[0].replace("Í","I")
            DireccioN[0] = DireccioN[0].replace("Ó","O")
            DireccioN[0] = DireccioN[0].replace("Ú","U")
        
        geolocalizador_entrada = {'direccion': DireccioN[0],
                'ciudad': MunicipiO[0].upper().replace('Á', 'A'), 'f': 'json'}

        # GEOLOCALIZADOR DEVUELVE LA LATITUD Y LONGITUD DE LA DIRECCION INGRESADA
        # geolocalizador = 'https://www.segurosbolivar.com/arcgis/rest/services/Servicios_SB/geoEsri/GPServer/geoEsri/execute'

        geolocalizador_salida = requests.get(url=geolocalizador,
                        headers={'content-type': 'application/json'},
                        params=geolocalizador_entrada)
        print(geolocalizador_salida.json())
        try:
            if "results" in geolocalizador_salida.json() and geolocalizador_salida.json()["results"]:
                pass
            else:
                print("Respuesta de geolocalización no válida")
                return HTTPException(status_code = 105, detail=f"Dirección: {direccion}, NIT: {nit}. Respuesta de geolocalización no válida")
        except HTTPException as e:
            return e
        if not len(geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')) == 1:
            try:
                LatituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[0]
                LongituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[1]
            except:
                urlGeocode = 'http://api.lupap.co/v2/co/'
                temp = requests.get(urlGeocode + 'bogota' + '?a=' + direccion+'&key=3bee5f0a19bf31eb0fa8a70376a4c61eb34d9ba8')
                LatituD[0] = temp.json()['response']['geometry']['coordinates'][0]
                LongituD[0] = temp.json()['response']['geometry']['coordinates'][1]
        
            sql_lotes2 = f"""SELECT * FROM lotes_0321
            WHERE ST_Intersects(
                geom,
                ST_Transform(ST_GeometryFromText('POINT({LongituD[0]} {LatituD[0]})', 4686), 4686)
                );

            """
            lotes2 = gpd.GeoDataFrame.from_postgis(sql_lotes2, con)
            if not len(lotes2) == 0:
                lotes = lotes2
            if not len(lotes2) == 0:
                sql_construccion2 = f"""SELECT * FROM construccion_tabla_0321
                WHERE ST_Intersects(
                    ST_Centroid(geom),
                    ST_GeomFromText('{lotes['geom'].iloc[0]}', 4686)
                    );
                """
                construccion2 = gpd.GeoDataFrame.from_postgis(sql_construccion2, con)
                if not len(construccion2) == 0:
                    construccion = construccion2 

                #predios
                sql_predios = f"""SELECT * FROM predios_0321
                    WHERE STRPOS('{lotes['LOTCODIGO'][0]}', CONCAT('0','0',"Barmanpre")) = 1"""
                predios = pd.read_sql_query(sql_predios, con)
                DireccioN[0] = predios["PreDirecc"].iloc[0]
        
            if len(lotes2) == 0:
                sql_lotes3 = f"""SELECT * FROM lotes_0321
                WHERE ST_Distance(
                    geom,
                    ST_Transform(ST_GeometryFromText('POINT({LongituD[0]} {LatituD[0]})', 4686), 4686)
                    ) < 0.0002
                ORDER BY
                geom <-> ST_GeometryFromText('POINT({LongituD[0]} {LatituD[0]})', 4686):: geometry
                LIMIT 1;
                """
                lotes3 = gpd.GeoDataFrame.from_postgis(sql_lotes3, con)
                if not len(lotes3) == 0:
                    lotes = lotes3
                if not len(lotes3) == 0:
                    sql_construccion2 = f"""SELECT * FROM construccion_tabla_0321
                    WHERE ST_Intersects(
                        ST_Centroid(geom),
                        ST_GeomFromText('{lotes['geom'].iloc[0]}', 4686)
                        );
                    """
                    construccion2 = gpd.GeoDataFrame.from_postgis(sql_construccion2, con)
                    if not len(construccion2) == 0:
                        construccion = construccion2 

                    #predios
                    sql_predios = f"""SELECT * FROM predios_0321
                        WHERE STRPOS('{lotes['LOTCODIGO'][0]}', CONCAT('0','0',"Barmanpre")) = 1"""
                    predios = pd.read_sql_query(sql_predios, con)
                    if len(predios["PreDirecc"]) > 0:
                        DireccioN[0] = predios["PreDirecc"].iloc[0]

    ###

    if not type(construccion) == type(None):
        if len(construccion) == 0:
            sql_construccion = f"""SELECT * FROM construccion_tabla_0321
                WHERE STRPOS("ConCodigo", '{'00' + str(predios.iloc[U]["Barmanpre"])}') = 1"""
            construccion = gpd.GeoDataFrame.from_postgis(sql_construccion, con)
            if not len(construccion) == 0:
                construccion = gpd.GeoDataFrame(construccion.iloc[0:1])

    ###


    if len(predios) >= 2:
        if not list(predios["PreAUso"].dropna()) == []:
            U = predios["PreAUso"].dropna().apply(lambda x: x.replace(',','.')).astype(float).idxmax()
        else:
            U = 0
    else:
        U = 0

     

    def PreCUso(index):
        '''Retorna los usos de los predios de la dirección
        '''    
        for i in range(0, len(TUso.iloc[:,0:1])):
            if not (str(predios['PreCUso'].unique()[index]) == 'nan' or str(predios['PreCUso'].unique()[index]) == 'None'):
                if str(TUso.iloc[72:,:].iloc[i].iloc[0]) == '0' + str(int(predios['PreCUso'].unique()[index])) or str(TUso.iloc[72:,:].iloc[i].iloc[0]) == '00' + str(int(predios['PreCUso'].unique()[index])):
                    return f'''Etiqueta: {TUso.iloc[72:,:].iloc[i].iloc[2]}.
                    Definición: {TUso.iloc[72:,:].iloc[i].iloc[1]}'''
                    break

                    
    def coma(name):
        '''Retorna el índice del carácter del string que es igual a una coma
        params:
        index = índice de la fila
        name = nombre de la columna
        '''
        for i in range(0,100):
            if predios.iloc[U][name][i] == '.':
                return i
                break

    def clase_suelo():
        '''Extrae la clase de suelo urbano de la Zona Homogénea Física'''
        if predios.iloc[U]['PreCZHF'] is not None:
            if len(predios.iloc[U]['PreCZHF']) == 15:
                if predios.iloc[U]['PreCZHF'][0] == '5':
                    return 'Clase de Suelo Urbano protegido'
                elif predios.iloc[U]['PreCZHF'][0] == '6':
                    return 'Clase de Suelo Urbano no protegido'
        
            if not len(predios.iloc[U]['PreCZHF']) == 15:
                print("La longitud de la cadena no es 15")
                 
                return 'Sin información'
        else:
            print("No hay información de la cadena")
             
            pass
    
    def topografia():
        '''Extrae la topografía de la Zona Homogénea Física (área urbana)'''
        
        if predios.iloc[U]['PreCZHF'] is not None:
            if len(predios.iloc[U]['PreCZHF']) > 0 and len(predios.iloc[U]['PreCZHF']) == 15:
                if predios.iloc[U]['PreCZHF'][0] == '5' or predios.iloc[U]['PreCZHF'][0] == '6':
                    if predios.iloc[U]['PreCZHF'][5] == '1':
                        return 'Topografía plana: (Entre 0 y < 7%)'
                    elif predios.iloc[U]['PreCZHF'][5] == '2':
                        return 'Topografía Inclinada: (Entre 7% y < 14%)'
                    elif predios.iloc[U]['PreCZHF'][5] == '3':
                        return 'Topografía Empinada: (14% o más)'
            else:
                print("La longitud de la cadena no es 15")
                 
                return 'Sin información'
        else:
             
            print("No hay información de la cadena")
            pass


    def clase_vias():
        '''Extrae la clase de vía de la Zona Homogénea Física (área urbana)'''
        
        if predios.iloc[U]['PreCZHF'] is not None:
            if len(predios.iloc[U]['PreCZHF']) == 15:
                if predios.iloc[U]['PreCZHF'][0] == '5' or predios.iloc[U]['PreCZHF'][0] == '6':
                    if predios.iloc[U]['PreCZHF'][8] == '1':
                        alpha = 'Sin vías'
                    elif predios.iloc[U]['PreCZHF'][8] == '2':
                        alpha = 'Peatonles sin pavimentar'
                    elif predios.iloc[U]['PreCZHF'][8] == '3':
                        alpha = 'Peatonales pavimentadas'
                    elif predios.iloc[U]['PreCZHF'][8] == '4':
                        alpha = 'Vehiculares sin pavimentar'
                    elif predios.iloc[U]['PreCZHF'][8] == '5':
                        alpha = 'Vehiculares pavimentadas'
                    return alpha
            
            if not len(predios.iloc[U]['PreCZHF']) == 15:
                print("La longitud de la cadena no es 15")
                 
                return 'Sin información'
        else:
            print("No hay información de la cadena")
             
            pass

    def estado_vias():
        '''Extrae el estado de la vía de la Zona Homogénea Física (área urbana)'''
        
        if predios.iloc[U]['PreCZHF'] is not None:
            if len(predios.iloc[U]['PreCZHF']) == 15:
                if predios.iloc[U]['PreCZHF'][0] == '5' or predios.iloc[U]['PreCZHF'][0] == '6':
                    if predios.iloc[U]['PreCZHF'][9] == '0':
                        alpha = 'Sin vías'
                    elif predios.iloc[U]['PreCZHF'][9] == '1':
                        alpha = 'Estado vías Malo'
                    elif predios.iloc[U]['PreCZHF'][9] == '2':
                        alpha = 'Estado vías Regular'
                    elif predios.iloc[U]['PreCZHF'][9] == '3':
                        alpha = 'Estado vías Bueno'
                    elif predios.iloc[U]['PreCZHF'][9] == '4':
                        alpha = 'Estado vías Excelente'
                    return alpha
            
            if not len(predios.iloc[U]['PreCZHF']) == 15:
                print("La longitud de la cadena no es 15")
                 
                return 'Sin información'
        else:
            print("No hay información de la cadena")
             
            pass

    def influencia_vias():
        '''Extrae la influencia de la vía de la Zona Homogénea Física (área urbana)'''
        
        if predios.iloc[U]['PreCZHF'] is not None:
            if len(predios.iloc[U]['PreCZHF']) == 15:
                if predios.iloc[U]['PreCZHF'][0] == '5' or predios.iloc[U]['PreCZHF'][0] == '6':
                    if predios.iloc[U]['PreCZHF'][10] == '0':
                        alpha = 'Sin vías'
                    elif predios.iloc[U]['PreCZHF'][10] == '1':
                        alpha = 'Vial local'
                    elif predios.iloc[U]['PreCZHF'][10] == '2':
                        alpha = 'Vial zonal o Intermedia'
                    elif predios.iloc[U]['PreCZHF'][10] == '3':
                        alpha = 'Arterial complementario'
                    elif predios.iloc[U]['PreCZHF'][10] == '4':
                        alpha = 'Arterial basico o principal'
                    return alpha
            
            if not len(predios.iloc[U]['PreCZHF']) == 15:
                print("La longitud de la cadena no es 15")
                 
                return 'Sin información'
        else:
            print("No hay información de la cadena")
             
            pass
            

    def estado_estructura():
        '''Extrae el estado de la estructura (en función de la tipología y la vetustez) de la base predios'''
        
        estado = None
        if (str(predios.iloc[U]['PreECons']) == 'nan' or str(predios.iloc[U]['PreECons']) == 'None'):
             
            return 'Sin información'
        elif int(predios.iloc[U]['PreECons']) == 141:
            estado = 'Malo'
        elif int(predios.iloc[U]['PreECons']) == 142:
            estado = 'Regular'
        elif int(predios.iloc[U]['PreECons']) == 143:
            estado = 'Bueno'
        elif int(predios.iloc[U]['PreECons']) == 144:
            estado = 'Excelente'
        return estado
            

    def bloque1():
        '''Extrae el área del terreno, área construida, año construcción, área uso'''
        
        area_terreno = predios.iloc[U]['PreATerre'][0:coma('PreATerre')+3] #+3 para 2 decimales
        area_construida =  predios.iloc[U]['PreAConst'][0:coma('PreAConst')+3]
        año_construccion = None
        area_uso = None
        if (str(predios.iloc[U]['PreVetustz']) == 'nan' or str(predios.iloc[U]['PreVetustz']) == "None"):
             
            return 'Sin información'
        if not (str(predios.iloc[U]['PreVetustz']) == 'nan' or str(predios.iloc[U]['PreVetustz']) == "None"):
            año_construccion = str(int(predios.iloc[U]['PreVetustz']))
        if not (str(predios.iloc[U]['PreAUso']) == 'nan' or str(predios.iloc[U]['PreAUso']) == 'None'):
            area_uso = predios.iloc[U]['PreAUso'][0:coma('PreAUso')+3] 
        print(año_construccion)
        return area_terreno, area_construida, año_construccion, area_uso
        

    def fachada():
        '''Extrae el tipo de acabado de la fachada'''
        
        alpha = None
        if not (str(predios.iloc[U]['PreAFachad']) == 'None' or str(predios.iloc[U]['PreAFachad']) == 'nan'):
            if int(predios.iloc[U]['PreAFachad']) == 211:
                alpha = 'Pobre'
            elif int(predios.iloc[U]['PreAFachad']) == 212:
                alpha = 'Sencilla'
            elif int(predios.iloc[U]['PreAFachad']) == 213:
                alpha = 'Regular'
            elif int(predios.iloc[U]['PreAFachad']) == 214:
                alpha = 'Buena'
            elif int(predios.iloc[U]['PreAFachad']) == 215:
                alpha = 'Lujosa'
            return alpha
        else:
            return 'Sin información'
             

    def cubrimiento_muros():
        '''Tipo de cubierta y muros de los Acabados
        '''
        
        alpha = None
        if not (str(predios.iloc[U]['PreACubier']) == 'nan' or str(predios.iloc[U]['PreACubier']) == 'None'):
            if int(predios.iloc[U]['PreACubier']) == 221:
                alpha = 'Sin Cubrimiento'
            elif int(predios.iloc[U]['PreACubier']) == 222:
                alpha = 'Pañete, Ladrillo prensado'
            elif int(predios.iloc[U]['PreACubier']) == 223:
                alpha = 'Estuco, Cerámica, Papel colgadura'
            elif int(predios.iloc[U]['PreACubier']) == 224:
                alpha = 'Madera, Piedra ornamental'
            elif int(predios.iloc[U]['PreACubier']) == 225:
                alpha = 'Marmol, Lujos y Otros'
            return alpha
        else:
            return 'Sin información'
             

    def acabado_pisos():
        '''Tipo de acabado de los pisos.
        '''
        
        alpha = None
        if not (str(predios.iloc[U]['PreAPisos']) == 'None' or str(predios.iloc[U]['PreAPisos']) == 'nan'):
            if int(predios.iloc[U]['PreAPisos']) == 231:
                alpha = 'Tierra pisada'
            elif int(predios.iloc[U]['PreAPisos']) == 232:
                alpha = 'Cemento, Madera burda'
            elif int(predios.iloc[U]['PreAPisos']) == 233:
                alpha = 'Baldosa común, Cemento, Tablón, Ladrillo'
            elif int(predios.iloc[U]['PreAPisos']) == 234:
                alpha = 'Listón Machihembriado'
            elif int(predios.iloc[U]['PreAPisos']) == 235:
                alpha = 'Tableta, Caucho, Acrílico, Granito, Baldosa fina'
            elif int(predios.iloc[U]['PreAPisos']) == 236:
                alpha = 'Parquet, Alfombra, Retal de marmol (grano pequeño)'
            elif int(predios.iloc[U]['PreAPisos']) == 237:
                alpha = 'Retal marmol, Marmol, Otros lujos'
            return alpha
        else:
            return 'Sin información'
             

    def estado_acabados():
        '''Se refiere al estado de los acabados en función de la “calidad de los materiales” y de su “estado de conservación”. Puede ser: mala, regular, buena o excelente.
        '''     
           
        alpha = None
        if not predios.iloc[U]['PreACons'] == None:
            if int(predios.iloc[U]['PreACons']) == 0:
                alpha = 'No se sabe'
            elif int(predios.iloc[U]['PreACons']) == 241:
                alpha = 'Malo'
            elif int(predios.iloc[U]['PreACons']) == 242:
                alpha = 'Regular'
            elif int(predios.iloc[U]['PreACons']) == 243:
                alpha = 'Bueno'
            elif int(predios.iloc[U]['PreACons']) == 244:
                alpha = 'Excelente'
            return alpha
        else:
             
            return 'Sin información'

    def muros():
        '''Tipo de muros de la estructura. Se refiere a los muros divisorios que no forman parte del armazón o estructura de la edificación.
        '''
        
        alpha = None
        if not (str(predios.iloc[U]['PreEMuros']) == 'nan' or str(predios.iloc[U]['PreEMuros']) == 'None'):
            if int(predios.iloc[U]['PreEMuros']) == 121:
                alpha = 'Materiales de desecho, esterilla'
            elif int(predios.iloc[U]['PreEMuros']) == 122:
                alpha = 'Bahareque, adobe, tapia'
            elif int(predios.iloc[U]['PreEMuros']) == 123:
                alpha = 'Madera'
            elif int(predios.iloc[U]['PreEMuros']) == 124:
                alpha = 'Concreto prefabricado'
            elif int(predios.iloc[U]['PreEMuros']) == 125:
                alpha = 'Bloque, ladrillo'
            return alpha
        else:
             
            return 'Sin información'

    def armazon():
        
        '''
        '''
        alpha = None
        if not (str(predios.iloc[U]['PreEArmaz']) == 'nan' or str(predios.iloc[U]['PreEArmaz']) == 'None'):
            if int(predios.iloc[U]['PreEArmaz']) == 0:
                alpha = 'No se sabe'
            elif int(predios.iloc[U]['PreEArmaz']) == 111:
                alpha = 'Madera'
            elif int(predios.iloc[U]['PreEArmaz']) == 112:
                alpha = 'Prefabricado'
            elif int(predios.iloc[U]['PreEArmaz']) == 113:
                alpha = 'Mamposteria'
            elif int(predios.iloc[U]['PreEArmaz']) == 114:
                alpha = 'Concreto'
            elif int(predios.iloc[U]['PreEArmaz']) == 115:
                alpha = 'Concreto'
            return alpha
        else:
             
            return 'Sin información'

    def cubierta():
        
        '''
        '''
        alpha = None
        if not (str(predios.iloc[U]['PreECubier']) == 'nan' or str(predios.iloc[U]['PreECubier']) == 'None'):
            if int(predios.iloc[U]['PreECubier']) == 131:
                alpha = 'Materiales de desechos, tejas asfálticas'
            elif int(predios.iloc[U]['PreECubier']) == 132:
                alpha = 'Zinc, teja de barro, eternit rústico'
            elif int(predios.iloc[U]['PreECubier']) == 133:
                alpha = 'Entrepiso (cubierta provisional) prefabricado'
            elif int(predios.iloc[U]['PreECubier']) == 134:
                alpha = 'Eternit o teja de barro (cubierta sencilla)'
            elif int(predios.iloc[U]['PreECubier']) == 135:
                alpha = 'Azotea, aluminio, placa sencilla con eternit, o teja de barro'
            elif int(predios.iloc[U]['PreECubier']) == 136:
                alpha = 'Placa impermeabilizada, cubierta lujosa u ornamental'
            return alpha
        else:
             
            return 'Sin información'

    def cerchas():
        
        alpha = None
        '''
        '''
        if str(predios.iloc[U]['PreCIndus']) == 'nan':
             
            return 'Sin información'
        else:
            if predios.iloc[U]['PreCIndus'] == 511:
                alpha = '''
                Caracterización de las cerchas: ''' + 'madera'
            elif predios.iloc[U]['PreCIndus'] == 512:
                alpha = 'Caracterización de las cerchas: ' + 'metálica liviana (luz menor a 10 m)'
            elif predios.iloc[U]['PreCIndus'] == 513:
                alpha = 'Caracterización de las cerchas: ' + 'metálica mediana (luz 10-20 m)'
            elif predios.iloc[U]['PreCIndus'] == 514:
                alpha = 'Caracterización de las cerchas: ' + 'metálica pesada (luz mayor a 20 )'
            elif predios.iloc[U]['PreCIndus'] == 521:
                alpha = 'Caracterización de las cerchas: ' + 'altura mayor a 7mts en columna - puente grúa'
            else:
                alpha = 'No se sabe'
            return alpha

    def tipo():
        '''Tipo de Predio según clasificación de la UAECD en función del propietario
        '''
        alpha = None
        for i in range(0,len(TUso.iloc[41:69,:])):
            if str(TUso.iloc[41:69,:].iloc[i].iloc[0]) == str(predios.iloc[U]['PreCDestin']):
                alpha = TUso.iloc[41:69,:].iloc[i].iloc[2]                 
                return alpha
        
    def edificabilidad():
        
        '''Si es zona de alto riesgo no mitigable, en cuyo caso hay peligro de la vida por remoción en masa
        '''
        alpha = None
        if str(predios.iloc[U]['PreCZHF'])[0] == '5' or str(predios.iloc[U]['PreCZHF'])[0] == '6':
            if str(predios.iloc[U]['PreCZHF'])[3:5] == '65':
                alpha = 'Tratamiento Urbanistico Zonas de alto Riesgo no mitigable'
                return alpha
            else:
                alpha = "No figura"
                return alpha
        else:
             
            return 'Sin información'
    

    CatastrO = [] #Lista con los datos de catastro
    for k in range(0,len(DireccioN)):
        tupla = 0
        if not len(predios) == 0:
            tupla = bloque1(), armazon(), muros(), cubierta(), estado_estructura(), fachada(), estado_acabados(), tipo(), topografia(), cerchas(), edificabilidad(), clase_suelo(), clase_vias(), estado_vias(), influencia_vias(), cubrimiento_muros(), acabado_pisos()
        CatastrO.append(tupla)

    PrecusO = [] #Usos de los predios
    for k in range(0,len(predios["PreCUso"].unique())):
        if not len(predios) == 0:
            PrecusO.append(PreCUso(k))
        else:
            PrecusO[0] = None

    #Centroide del polígono del lote

    LatloN = [(None,None)]

    if not len(lotes) == 0:
        LatloN = []
        LatloN.append((lotes['geom'].iloc[0].centroid.y, lotes['geom'].iloc[0].centroid.x))

    if not type(construccion) == type(None):
        ConstruccioN = []
        ConstruccioN.append(construccion['ConNPisos'])
        ConstruccioN.append(construccion['ConTSemis'])
        ConstruccioN.append(construccion['ConNSotano'])

    DIRECCION = DireccioN[0]
    LATITUD = LatloN[0][0]
    LONGITUD = LatloN[0][1]
    
    if LATITUD is None and LONGITUD is None:
        geolocalizador_entrada = {'direccion': DireccioN[0],
                'ciudad': MunicipiO[0].upper().replace('Á', 'A'), 'f': 'json'}

        # GENERACIÓN DE LAS COORDENADAS A PARTIR DE LA DIRECCIÓN
        geolocalizador = 'https://www.segurosbolivar.com/arcgis/rest/services/Servicios_SB/geoEsri/GPServer/geoEsri/execute'
        geolocalizador_salida = requests.get(url=geolocalizador,
                        headers={'content-type': 'application/json'},
                        params=geolocalizador_entrada)
        if "results" in geolocalizador_salida.json() and geolocalizador_salida.json()["results"]:
            for result in geolocalizador_salida.json()["results"]:
                if result.get("value"):
                    coordenadas = result["value"]
                    print("Coordenadas encontradas:", coordenadas)
                    try:
                        print(f"La salida de la geolocalización es: {geolocalizador_salida.json()}")
                        LatituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[0]
                        LongituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[1]
                    except:
                        pass
                    LATITUD = LatituD[0]
                    LONGITUD = LongituD[0]
                    break 
            else:
                geolocalizador_entrada = {'direccion': direccion_basica,
                'ciudad': MunicipiO[0].upper().replace('Á', 'A'), 'f': 'json'}
                geolocalizador_salida = requests.get(url=geolocalizador,
                                headers={'content-type': 'application/json'},
                                params=geolocalizador_entrada)
                try:
                    print(f"La salida de la geolocalización es: {geolocalizador_salida.json()}")
                    LatituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[0]
                    LongituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[1]
                except:
                    pass
                LATITUD = LatituD[0]
                LONGITUD = LongituD[0]
        else:
            print("No hay resultados en el JSON.")
            

    print("ESTA ES LA DIRECCION ", DIRECCION)
    print("ESTA ES LA LATITUD", LATITUD)
    print("ESTA ES LA LONGITUD", LONGITUD)
    
    
    try:
        if DIRECCION is None or LATITUD is None or LONGITUD is None:
            print("La dirección es none")
            raise HTTPException(status_code=101, detail=f"Dirección: {direccion}, NIT: {nit}. Coordenadas no existentes para la dirección")
    except HTTPException as e:
        return e
    
    ################## API NEARBY SEARCH #######################
    def nearby_search_maps(latitud, longitud):
        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
        params = {
            'location': f'{latitud}, {longitud}',
            'radius': 50,
            'type': '', 
            'key': 'AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc' 
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        ruta_json = 'Archivos/data.json'

        with open(ruta_json, 'w') as f:
            json.dump(data, f)
        
        # with open('Archivos/data.json') as json_file:
        #     data = json.load(json_file)
        
        m = folium.Map(
            location=[float(latitud), float(longitud)],
            zoom_start=20,
            width=1450,
            height=950
            )
        
        tooltip = f"{direccion}"
        folium.Marker(
            [latitud, longitud],
            popup=f"{direccion}",
            tooltip=tooltip,
            icon=folium.Icon(icon = "location-dot", color = "red", prefix = "fa"),
        ).add_to(m)
        
        locales = []
        coordenadas = []
        tipos = []

        for result in data['results']:
            tooltip = result['name']
            lat = result['geometry']['location']['lat']
            lng = result['geometry']['location']['lng']
            locales.append([result['name'], result['types'][0]])
            coordenadas.append([result['geometry']['location']['lat'], result['geometry']['location']['lng']])
            tipos.append(result['types'])
            tipo_negocio = result['types']
            
            if tipo_negocio[0] == 'store' or tipo_negocio[0] == 'hardware_store' or tipo_negocio[0] == 'bicycle_store' or tipo_negocio[0] == 'furniture_store' or tipo_negocio[0] == 'shoe_store' or tipo_negocio[0] == 'convenience_store' or tipo_negocio[0] == 'laundry' or tipo_negocio[0] == 'electronics_store' or tipo_negocio[0] == 'florist' or tipo_negocio[0] == 'book_store' or tipo_negocio[0] == 'locksmith' or tipo_negocio[0] == 'liquor_store' or tipo_negocio[0] == 'pet_store' or tipo_negocio[0] == 'jewelry_store':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "store", color='blue', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'home_goods_store':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "house", color='lightblue', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'storage':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "warehouse", color='darkgreen', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'clothing_store':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "shirt", color='pink', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'moving_company':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "truck-moving", color='cadetblue', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'point_of_interest' or tipo_negocio[0] == 'tourist_attraction' or tipo_negocio[0] == 'art_gallery':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "store", color='green', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'embassy':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "building-flag", color='purple', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'health' or tipo_negocio[0] == 'pharmacy' or tipo_negocio[0] == 'doctor' or tipo_negocio[0] == 'dentist' or tipo_negocio[0] == 'hospital' or tipo_negocio[0] == 'physiotherapist' or tipo_negocio[0] == 'drugstore':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "star-of-life", color='darkgreen', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'restaurant' or tipo_negocio[0] == 'bakery' or tipo_negocio[0] == 'food' or tipo_negocio[0] == 'cafe' or tipo_negocio[0] == 'meal_delivery':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "utensils", color='orange', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'grocery_or_supermarket' or tipo_negocio[0] == 'supermarket':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "cart-shopping", color='gray', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'post_office' or tipo_negocio[0] == 'real_estate_agency':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "envelope", color='darkpurple', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'lodging' or tipo_negocio[0] == 'travel_agency' :
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "hotel", color='lightgray', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'accounting' or tipo_negocio[0] == 'atm' or tipo_negocio[0] == 'finances' or tipo_negocio[0] == 'bank':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "piggy-bank", color='darkpurple', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'school':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "school", color='beige', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'general_contractor':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "handshake", color='darkblue', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'real_estate_agency':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "building-wheat", color='darkpurple', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'insurance_agency':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "shield", color='darkgreen', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'car_wash' or tipo_negocio[0] == 'car_repair' or tipo_negocio[0] == 'car_dealer' or tipo_negocio[0] == 'parking':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "car", color='lightred', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'beauty_salon' or tipo_negocio[0] == 'hair_care' or tipo_negocio[0] == 'spa':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "scissors", color='lightred', prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'laundry':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "jug-detergent", color="purple", prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'church':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "church", color="darkred", prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'bar' or tipo_negocio[0] == 'night_club':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "wine-bottle", color="darkred", prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'shopping_mall':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "bag-shopping", color="darkgreen", prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'local_government_office':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "place-of-worship", color="darkgreen", prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'lawyer':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "gavel", color="darkred", prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'park':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "tree", color="lightgreen", prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'casino':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "dice", color="black", prefix = "fa"),
                    ).add_to(m)
            if tipo_negocio[0] == 'gym':
                folium.Marker(
                    [lat, lng],
                    popup=result['name'],
                    tooltip=tooltip,
                    icon=folium.Icon(icon = "dumbbell", color="black", prefix = "fa"),
                    ).add_to(m)
            
        tipo_mapa = {
            'locality' : "Localidad",
            'point_of_interest' : "Punto de interés",
            'store' : "Tienda",
            'home_goods_store' : "Artículos del hogar",
            'moving_company' : 'Empresa de mudanzas',
            'hardware_store' : "Ferretería",
            'storage' : "Almacenamiento",
            'embassy' : "Embajada",
            'clothing_store': "Tienda de ropa",
            'insurance_agency' : "Agencia de seguros",
            'health' : "Salud",
            'pharmacy' : "Farmacía",
            'restaurant' : "Restaurante",
            'bakery' : "Panadería",
            'food' : "Comida",
            'grocery_or_supermarket' : "Tienda o supermercado",
            'supermarket' : "Supermercado",
            'lodging' : "Hotel",
            'bicycle_store' : "Tienda de bicicletas",
            'post_office' : "Oficina de correo",
            'accounting' : "Contabilidad",
            'school' : "Escuela",
            'doctor' : "Servicio de salud",
            'travel_agency' : "Agencia de viajes",
            'real_estate_agency' : "Agencia inmobiliaria",
            'general_contractor' : "Contratista general",
            'dentist' : "Dentista",
            'hospital' : "Hospital",
            'furniture_store' : "Tienda de muebles",
            'car_repair' : "Taller de carros",
            'car_wash' : "Lava carros",
            'shoe_store' : "Tienda de zapatos",
            'convenience_store' : "Miscelánea", 
            'beauty_salon' : "Salón de belleza", 
            'cafe' : "Café",
            'hair_care' : "Salón de belleza",
            'laundry' : "Lavandería",
            'physiotherapist' : "Fisioterapía",
            'car_dealer' : "Venta de carros",
            'church' : "Iglesia",
            'atm' : "Banco",
            'finance' : "Finanzas",
            'bar' : "Bar",
            'shopping_mall' : "Centro Comercial",
            'local_government_office' : "Oficina Gubernamental",
            'lawyer' : "Firma de abogados",
            'park' : "Parque",
            'tourist_attraction' : "Atracción turística",
            'electronics_store' : "TIenda electrónica",
            'parking' : "Parqueadero",
            'florist' : "Floristería",
            'spa' : "Spa",
            'art_gallery' : "Galería de arte",
            'book_store' : "Tienda de líbros",
            'locksmith' : "Cerrajero",
            'drugstore' : "Drogería",
            'bank' : "Banco",
            'liquor_store' : "Licorería",
            'night_club' : "Discoteca",
            'pet_store' : "Tienda de mascotas",
            'casino' : "Casino",
            'jewelry_store' : "Joyería",
            'gym' : "Gimnasio",
            'meal_delivery' : "Entrega de comida",
        }
        
        clasificacion_incendio = {
            'point_of_interest' : "Medio",
            'store' : "Medio",
            'home_goods_store' : "Medio",
            'moving_company' : 'Medio',
            'hardware_store' : "Medio - bajo",
            'storage' : "Medio - Alto",
            'embassy' : "Medio - Alto",
            'clothing_store': "Medio",
            'insurance_agency' : "Bajo",
            'health' : "Bajo",
            'pharmacy' : "Bajo",
            'restaurant' : "Medio",
            'bakery' : "Medio",
            'food' : "Medio",
            'grocery_or_supermarket' : "Medio",
            'supermarket' : "Medio",
            'lodging' : "Bajo",
            'bicycle_store' : "Medio - Bajo",
            'post_office' : "Medio - Bajo",
            'accounting' : "Bajo",
            'school' : "Bajo",
            'doctor' : "Bajo",
            'travel_agency' : "Bajo",
            'real_estate_agency' : "Bajo",
            'general_contractor' : "Medio - Bajo",
            'dentist' : "Bajo",
            'hospital' : "Medio - Bajo",
            'furniture_store' : "Medio - Alto",
            'car_repair' : "Medio",
            'car_wash' : "Medio - Bajo",
            'shoe_store' : "Medio",
            'convenience_store' : "Miscelánea", 
            'beauty_salon' : "Medio - Bajo", 
            'cafe' : "Medio - Bajo",
            'hair_care' : "Medio",
            'laundry' : "Medio - Bajo",
            'physiotherapist' : "Bajo",
            'car_dealer' : "Bajo",
            'church' : "Medio - Bajo",
            'atm' : "Bajo",
            'finance' : "Bajo",
            'bar' : "Alto",
            'shopping_mall' : "Medio - Bajo",
            'local_government_office' : "Medio - Alto",
            'lawyer' : "Bajo",
            'park' : "Bajo",
            'tourist_attraction' : "Bajo",
            'electronics_store' : "Medio",
            'parking' : "Bajo",
            'florist' : "Medio - Bajo",
            'spa' : "Bajo",
            'book_store' : "Medio - Bajo",
            'locksmith' : "Bajo",
            'drugstore' : "Bajo",
            'bank' : "Bajo",
            'liquor_store' : "Medio - Alto",
            'night_club' : "Alto",
            'pet_store' : "Medio - Bajo",
            'casino' : "Medio - Bajo",
            'jewelry_store' : "Bajo",
            'gym' : "Bajo",
            'art_gallery' : "Bajo",
            'meal_delivery' : "Medio",
        }
        
        categorias = {
            'Tienda' : ['Tienda', 'Ferretería', 'Tienda de bicicletas','Tienda de muebles','Tienda de zapatos','Miscelánea', 'TIenda electrónica', 'Floristería', 'Tienda de líbros', 'Cerrajero', 'Licorería', 'Tienda de mascotas', 'Joyería'],
            'Artículos del hogar' : ['Artículos del hogar'],
            'Almacenamiento' : ['Almacenamiento'],
            'Punto de interés' :['Punto de interés', "Atracción turística", "Galeria de arte"],
            'Empresa de mudanzas' : ['Empresa de mudanzas'],
            'Embajada':['Embajada'],
            'Tienda de ropa':['Tienda de ropa'] ,
            'Agencia de seguros':['Agencia de seguros'] ,
            'Salud':['Salud', 'Farmacía', 'Servicio de salud', 'Dentista', 'Hospital', 'Fisioterapía', 'Drogería'],
            'Tienda de ropa':['Tienda de ropa'],
            "Restaurante":['Restaurante', 'Panadería', 'Comida', 'Restaurante', 'Café', "Entrega de comida"],
            "Tienda o supermercado":['Tienda o supermercado', 'Supermercado'],
            "Hotel":['Hotel', 'Agencia de viajes'],
            "Agencia inmobiliaria":['Agencia inmobiliaria'],
            "Contratista":['Contratista general'],
            "Escuela":['Escuela'],
            "Oficina de correo":['Oficina de correo'],
            "Contabilidad":['Contabilidad', 'Cajero automático', 'Finanzas', 'Banco'],
            "Agencia inmobiliaria":['Agencia inmobiliaria'],
            "Automóviles":['Taller de carros', 'Lava carros', 'Venta de carros', 'Parqueadero'],
            "Belleza":['Salón de belleza', 'Spa'],
            "Lavandería":['Lavandería'],
            "Iglesia":['Iglesia'],
            "Bar":['Bar', 'Discoteca'],
            "Centro comercial":['Centro comercial'],
            "Oficina Gubernamental":['Oficina Gubernamental'],
            "Firma de abogados":['Firma de abogados'],
            "Parque":['Parque'],
            "Casino":['Casino'],
            "Gimnasio":['Gimnasio'],
        }
        
        tipos_excluir = ['locality', 'route','sublocality_level_1', 'transit_station']
        
        locales_clasif = []
        coordenada = []
        locales_tipo = []
        for local, coord, tipo in zip(locales, coordenadas, tipos):
            tipo_descr = tipo_mapa.get(local[1], local[1])
            lat = coord[0]
            lon = coord[1]
            
            if local[1] not in tipos_excluir:
                # Obtener la clasificación de incendio del diccionario
                clasif_incendio = clasificacion_incendio.get(local[1], "No clasificado")
                
                # Agregar a locales_clasif la tupla (nombre del local, tipo del local, clasificación de incendio)
                locales_clasif.append([local[0], tipo_descr, clasif_incendio])
                coordenada.append([lat, lon])
                
        tipos_presentes = set([local[1] for local in locales_clasif])

        legend_html = """
            <div style="position: fixed; 
            top: 10px; left: 10px; width: 250px; height: auto; 
            border:2px solid grey; z-index:9999; font-size:14px;
            background-color: rgba(255, 255, 255, 0.5);
            ">
            &nbsp; <span style="font-family: Arial, sans-serif; font-size: 16px; color: #333333; font-weight: bold;">Leyenda</span> <br>
            &nbsp; <i class="fa-solid fa-location-dot fa-2x" style="color:red"></i> Predio <br>
        """
        
        added_categories = set()
        
        for categoria, subcategorias in categorias.items():
            for tipo_presente in tipos_presentes:
                if tipo_presente in subcategorias and categoria not in added_categories:          
                    icono = '',
                    color = ''
                    if categoria == 'Tienda':
                        icono = "store"
                        color = "rgb(67, 179, 255)"
                    if categoria == 'Artículos del hogar':
                        icono = "house"
                        color = "rgb(142, 209, 255)"
                    if categoria == 'Almacenamiento':
                        icono = "warehouse"
                        color = "darkgreen"
                    if categoria == 'Punto de interés':
                        icono = "store"
                        color = "rgb(86,201,98)"
                    if categoria == 'Empresa de mudanzas':
                        icono = "truck"
                        color = "rgb(34,67,124)"
                    if categoria == 'Embajada':
                        icono = "building-flag"
                        color = "purple"
                    if categoria == 'Tienda de ropa':
                        icono = "shirt"
                        color = "pink"
                    if categoria == 'Agencia de seguros':
                        icono = "shield"
                        color = "darkgreen"
                    if categoria == 'Salud':
                        icono = "star-of-life"
                        color = "green"
                    if categoria == 'Restaurante':
                        icono = "utensils"
                        color = "orange"
                    if categoria == 'Tienda o supermercado':
                        icono = "cart-shopping"
                        color = "gray"
                    if categoria == 'Hotel':
                        icono = "hotel"
                        color = "gray"
                    if categoria == 'Oficina de correo':
                        icono = "envelope"
                        color = "yellow"
                    if categoria == 'Contabilidad':
                        icono = "piggy-bank"
                        color = "rgb(65,6,97)"
                    if categoria == 'Escuela':
                        icono = "school"
                        color = "rgb(245,221,162)"
                    if categoria == 'Contratista':
                        icono = "handshake"
                        color = "darkblue"
                    if categoria == 'Agencia inmobiliaria':
                        icono = "building-wheat"
                        color = "darkpurle"
                    if categoria == 'Automóviles':
                        icono = "car"
                        color = "rgb(255,142,124)"
                    if categoria == 'Belleza':
                        icono = "scissors"
                        color = "rgb(255,142,124)"
                    if categoria == 'Lavandería':
                        icono = "jug-detergent"
                        color = "rgb(203,31,233)"
                    if categoria == 'Iglesia':
                        icono = "church"
                        color = "rgb(140,2,2)"
                    if categoria == 'Bar':
                        icono = "wine-bottle"
                        color = "darkred"
                    if categoria == 'Centro comercial':
                        icono = "bag-shopping"
                        color = "darkgreen"
                    if categoria == 'Oficina Gubernamental':
                        icono = "place-of-worship"
                        color = "darkgreen"
                    if categoria == 'Firma de abogados':
                        icono = "gavel"
                        color = "darkred"
                    if categoria == 'Parque':
                        icono = "tree"
                        color = "lightgreen"
                    if categoria == 'Casino':
                        icono = "dice"
                        color = "black"
                    if categoria == 'Gimnasio':
                        icono = "dumbbell"
                        color = "black"
                    legend_html += f'&nbsp; <i class="fa-solid fa-{icono} fa-2x" style="color:{color}"></i> {categoria} <br>'
                    added_categories.add(categoria)
    
        legend_html += """
        </div>
        """
        
        m.get_root().html.add_child(folium.Element(legend_html))
        m.save('Archivos/mapa_nearby_search.html')
        
        img_map = m._to_png(5)
        img = Image.open(io.BytesIO(img_map))
        img.save("Archivos/mapa.png")
        
        os.remove("Archivos/mapa_nearby_search.html")
        
        return img, locales_clasif, coordenada
    
    ################ FUNCIÓN PARA CALCULAR DISTANCIA DE ESTABLECIMIENTOS CERCANOS #######################
    
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000

        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        distance = round(distance,1)
        
        return distance
    
    
    ## VERIFICACIÓN INFORMACIÓN CATASTRO
    info_catastro = True
    if len(predios) == 0:
        print("El predio no tiene información en la base de datos del catastro")
        info_catastro = False
        
    if info_catastro == True:
        def codigo_barrio():
            '''Extrae el código del barrio'''
            return predios.iloc[U]['PreCBarrio']

        def match_sector(self):
            '''
            '''
            for index, s in enumerate(sector['CODIGO_BARRIO']):
                if str(int(s)) == str(self):
                    return index, s
                # Si no se encuentra coincidencia, devolver una tupla vacía
            return 0, 0

        SectoR = []
        for i in range(0,len(DireccioN)):
            if not len(predios) == 0:
                SectoR.append((sector['NOMBRE_BARRIO'].iloc[match_sector(codigo_barrio())[0]], sector['NOMBRE_UPZ'].iloc[match_sector(codigo_barrio())[0]], sector['NOMBRE_LOCALIDAD'].iloc[match_sector(codigo_barrio())[0]]))
            else:
                SectoR.append((0,0,0))

        colores = [(.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5), (.2,.2,1, .5), (1,0,0, .5), (.3,0,.3, .5), (0,.8,.5, .5), (.3,.5,.7, .5), (.1,.2,.3, .5), (.6,.45,1, .5), (1,0.33,0.11, .5), (.3,0.77,.34, .5), (.1,.45,.5, .5), (.65,.5,.7, .5), (.1,.65,.3, .5)]
        colores2 = [(.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1), (.2,.2,1, 1), (1,0,0, 1), (.2,0,.2, 1), (0,.8,.5, 1), (.3,.5,.7, 1), (.1,.2,.3, 1), (.6,.45,1, 1), (1,0.33,0.11, 1), (.3,0.77,.34, 1), (.1,.45,.5, 1), (.65,.5,.7, 1), (.1,.65,.3, 1)]
        
        #Gráfica del polígono. Mercator, de WGS84.

        if not type(construccion) == type(None):
            if not len(construccion) == 0:
                fig, ax = plt.subplots(figsize = (8,6),)
                max_vectores = 5
                for k in range(0, min(len(construccion['geom']), max_vectores)):
                    if k < len(colores):
                        gpd.GeoSeries(construccion['geom'][k], crs={'init' :'epsg:4686'}).to_crs(epsg=3395).plot(color = colores[k], ax = ax)
                        x = gpd.GeoSeries(construccion["geom"].iloc[k].centroid, crs={'init' :'epsg:4326'}).to_crs(epsg=3395).x
                        y = gpd.GeoSeries(construccion["geom"].iloc[k].centroid, crs={'init' :'epsg:4326'}).to_crs(epsg=3395).y
                        ax.annotate(f"{ConstruccioN[0].iloc[k]} PISO(S)", color =colores2[k], xy=(x, y), xycoords='data',
                                xytext=(1/(k+2), 2/(k+2)-.1), textcoords='axes fraction',
                                arrowprops=dict(facecolor=colores[k], shrink=0.05),
                                horizontalalignment='right', verticalalignment='top',)
                gpd.GeoSeries(lotes['geom'][0], crs={'init' :'epsg:4686'}).to_crs(epsg=3395).plot(color = (0,0,0,.1), ax = ax)
                plt.axis('equal')
                plt.title(label="Mercator");
                fig.savefig("Archivos/PNG/ID/" + str(DireccioN[0]) + ".png", dpi=100)
        else:
            if not len(lotes) == 0:
                fig, ax = plt.subplots(figsize = (8,6),)
                gpd.GeoSeries(lotes['geom'][0], crs={'init' :'epsg:4686'}).to_crs(epsg=3395).plot(color = (0,0,0,.1), ax = ax)
                plt.axis('equal')
                plt.title(label="Mercator");
                fig.savefig("Archivos/PNG/ID/" + str(DireccioN[0]) + ".png", dpi=100)
            else:
                fig, ax = plt.subplots(figsize = (8,6),)
                plt.axis('equal')
                plt.title(label="Mercator");
                fig.savefig("Archivos/PNG/ID/" + str(DireccioN[0]) + ".png", dpi=100)
        
        if len(predios) > 0:
            sql_avaluos = f"""SELECT * FROM avaluos_2019
            WHERE STRPOS('{'0' + '0' + predios["Barmanpre"][U]}', "MANZANA_ID") = 1"""
            avaluos = pd.read_sql(sql_avaluos, con)
            print(avaluos)
            
            sql_estrato = f"""SELECT * FROM estrato_socioeconomico_2021
            WHERE STRPOS("ESoCLote", '{'0' + '0' + predios["Barmanpre"][U]}') = 1"""
            estrato = pd.read_sql(sql_estrato, con)

            if len(estrato) == 0:
                sql_estrato = f"""SELECT * FROM estrato_socioeconomico_2021
                WHERE STRPOS("ESoCLote", '{'0' + '0' + predios["Barmanpre"][U][0:len(predios["Barmanpre"][U])-3]}') = 1"""
                estrato = pd.read_sql(sql_estrato, con)
                if not len(estrato) == 0:
                    estrato = estrato.mode().iloc[0]

            sql_valor_metro = f"""SELECT * FROM valor_metro_cuadrado_2020
            WHERE STRPOS('{'0' + '0' + predios["Barmanpre"][U]}', "MANCODIGO") = 1"""
            valor_metro = pd.read_sql(sql_valor_metro, con)

    #IMAGEN MAPA ESTÁTICO - ENTORNO
    f =open('Archivos/Mapas/ID/'+str(DIRECCION)+'ENTORNO.png','wb')
    f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/staticmap?center='+str(LATITUD)+','+str(LONGITUD)+'&zoom=20&size=600x600&maptype=satellite&markers=color:red%7Clabel:%7C'+str(LATITUD)+','+str(LONGITUD)+'&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
    f.close()
    
    
    
#RECOLECCIÓN DE INFORMACIÓN EMPRESARIAL

    #########

    modelo = 'Perfil cliente'

    version = '2.0'

    ramo = "Property"

    poliza = "Daños materiales"

    country = "Colombia"

    alcance = "Suscripción, renovación, prevención y comerciales"

    division = "Empresas"

    ciiu = pd.read_excel(r"Archivos/Estructura-detallada-CIIU-4AC-2020-.xls")
    
    ciiu_Politicas = pd.read_excel(r"Archivos/Politicas_ID.xlsx")
    
    # CÓDIGO PARA SABER QUE CÓDIGOS CIIU HACEN FALTA EN LA DB DE POLÍTICAS
    # ciiu_Dane = pd.read_excel(r"/home/ingeniero_digital/principal/Modelo_Incendio_Bog/Estructura-detallada-CIIU-4AC-2020-.xls", skiprows=lambda x: x == 0 or not str(x).replace('.', '', 1).isdigit())
    
    # valores_columna_dane = [int(valor) if not pd.isna(valor) else None for valor in ciiu_Dane.iloc[:, 2].tolist()]
    # valores_columna_ciiu = ciiu_Politicas["CIIU"].tolist()
    
    # faltantes = [valor for valor in valores_columna_dane if valor not in valores_columna_ciiu]
    # print(f"Los valores que hacen falta son: {faltantes}")
    #Se lee el excel con los datos de entrada y políticas

    # save2 = pd.read_excel("PLATAFORMA/plataforma_proyecto/biblioteca_modelos/save2.xlsx")
    
    if is_cc == False:
        nit = save2.iloc[0].iloc[2]
        if str(nit) == 'nan':
            nit = 0
        
        sql_dane = f"""SELECT * FROM dane_2020
        WHERE "NIT" = '{int(nit)}'"""
        dane = pd.read_sql(sql_dane, con) 

        sql_emis = f"""SELECT * FROM emis_0521
        WHERE "n_id" = '{int(nit)}'"""
        emis = pd.read_sql(sql_emis, con) 
    else:
        pass

    IsAseg = True
    IsAlerta = False
    FueraSus = False
    razon_social = 'None'
    ciiu_dado = []
    ciiu_numero = []
    departamento_principal = 'None'
    direccion_principal = 'None'
    municipio_principal = 'None'
    telefono_principal = 'None'
    telefono2_principal = 'None'
    nombre_comercial = 'None'

    if is_cc == False:
        if not len(dane) == 0: 
            razon_social = dane['RAZON_SOCIAL'].iloc[0]
            nombre_comercial = None
            for i in range(0,len(dane)):
                if not str(dane['NOMBRE_COMERCIAL'].iloc[i]) == 'nan':
                    nombre_comercial = dane['NOMBRE_COMERCIAL'].iloc[i]
            direccion_principal = dane['DIRECCION'].iloc[0]
            departamento_principal = dane['NOMBRE_DPTO'].iloc[0]
            municipio_principal = dane['NOMBRE_MPIO'].iloc[0]
            telefono_principal = str(int(dane['TELEFONO1'].iloc[0]))
            telefono2_principal = str(int(dane['TELEFONO1'].iloc[0]))

            def match_ciiu(self):
                '''Retorna el índice de la actividad económica correspondiente al código CIIU
                params:
                self = código CIIU correspondiente al NIT
                '''
                for index, s in enumerate(ciiu['Unnamed: 2']):
                    if str(s) == str(self) or str(s) == '0' + str(self):
                        return index, s
                        break
                    elif str(self)[:3] == str(ciiu['Unnamed: 3'].iloc[index]) or str(self) == '0' + str(ciiu['Unnamed: 3'].iloc[index]):
                        return index, ciiu['Unnamed: 1'].iloc[index]

            for i in range(len(dane)):
                result = match_ciiu(int(dane['CIIU_ID_CIIU_4'].iloc[i]))
                if result is not None:
                    ciiu_dado.append(ciiu['Unnamed: 3'].iloc[result[0]])
                else:
                    ciiu_dado.append(None)
            for i in range(0, len(dane)):
                ciiu_numero.append(str(int(dane['CIIU_ID_CIIU_4'].iloc[i])))
        
        try:
            if len(ciiu_numero) == 0:
                return HTTPException(status_code=102, detail=f"Dirección: {direccion}, NIT: {nit}. El NIT no posee actividad económica")
        except HTTPException as e:
            raise e
            
        
        ciiu_numero_float = [float(x) for x in ciiu_numero]

        filtro = ciiu_Politicas["CIIU"].isin(ciiu_numero_float)
        riesgos_politicas = ciiu_Politicas[filtro]

        ciiu_numero_index = {float(numero): index for index, numero in enumerate(ciiu_numero)}

        riesgos_politicas["CIIU"] = riesgos_politicas["CIIU"].astype(float)
        riesgos_politicas["Order"] = riesgos_politicas["CIIU"].map(ciiu_numero_index)
        riesgos_politicas = riesgos_politicas.sort_values("Order")

        riesgos_politicas = riesgos_politicas.drop(columns=["Order"])
        print(riesgos_politicas[["CIIU", "Incendio", "All Risk", "Sustracción", "R.M", "E.E", "Manejo", "RC"]])
        
        for ciiu_principal in ciiu_numero:
            ciiu_principal_float = float(ciiu_principal)
            filtro2 = ciiu_Politicas["CIIU"].eq(ciiu_principal_float)
            riesgos_pp = ciiu_Politicas[filtro2]
            
            if not riesgos_pp.empty:
                
                politicas_incendio = riesgos_politicas["Incendio"].iloc[0] 
                
                if any(riesgos_politicas[col].iloc[0] == 5.0 for col in ["CIIU","Incendio", "All Risk", "Sustracción","R.M","E.E"]):
                    IsAseg = False
                    print("No es asegurable por políticas")
                if riesgos_politicas["Sustracción"].iloc[0] == 5.0:
                    FueraSus = True
                if any((riesgos_politicas[col].iloc[1:] == 5.0).any() for col in ["CIIU","Incendio", "All Risk", "Sustracción","R.M","E.E", "Manejo", "RC"]):
                    IsAlerta = True
                    print("Se genera alerta por riesgo en actividades secundarias")
                elif IsAseg == True:
                    print("Es asegurable según políticas") 

            if riesgos_pp.empty:
                print("La lista está vacía")
        print(FueraSus)
    
    else:
        razon_social = "Persona Natural"
        politicas_incendio = 3.0
        
  
    #############################################
    #coding: utf-8
    #Biblioteca de Modelos

    modelo = 'Modelo de integración'

    version = '1.0'

    ramo = "Property"

    poliza = "Daños materiales"

    country = "Colombia"

    alcance = "Suscripción y prevención"

    division = "Empresas"


    #https://2.python-requests.org/es/latest/user/quickstart.html
    EntradaApiMapas = {'latitud': str(LATITUD),
            'longitud': str(LONGITUD), 'f': 'json'}

    #API Mapas
    ApiMapas = 'https://www.segurosbolivar.com/arcgis/rest/services/Servicios_SB/ingDigVerDos/GPServer/ingDig/execute'

    resultado_api_mapas = requests.get(url=ApiMapas,
                    headers={'content-type': 'application/json'},
                    params=EntradaApiMapas)
    EntradaManzaneoPymes = {'latitud': str(LATITUD),
            'longitud': str(LONGITUD), 'f': 'json'}
    
    ConceptoManzaneo = []
    
    if resultado_api_mapas.status_code == 200:
        alpha = resultado_api_mapas.json()
        print('Éxitoso')
        if "error" in alpha:
            print("La API devolvió un error:", alpha["error"])        
    else:
        print('Hay un error')
    alpha = resultado_api_mapas.json() 
    MatrizAmenazas = []
    MatrizAmenazasManzaneo = []
    ValoreS = []

    if "error" in alpha:
        pass
    if "results" in alpha:  
        if not alpha['results'][0]['value']['features'] == []:
            MatrizAmenazasManzaneo = [alpha['results'][0]['value']['features'][0]['attributes']['INCENDIO'], 
            alpha['results'][0]['value']['features'][0]['attributes']['SUSTRACCION'], 
            alpha['results'][0]['value']['features'][0]['attributes']['ANEGACION'], 
            alpha['results'][0]['value']['features'][0]['attributes']['TERREMOTO'], 
            alpha['results'][0]['value']['features'][0]['attributes']['AMIT'],
            alpha['results'][0]['value']['features'][0]['attributes']['DANO_ELECT'], 
            alpha['results'][0]['value']['features'][0]['attributes']['VIENTOS']]
            
            MatrizAmenazas = [alpha['results'][0]['value']['features'][0]['attributes']['TERREMO'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['VIENTO'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['REMOCI'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['SUSTRA'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['ORDENPU'].capitalize(),
            alpha['results'][0]['value']['features'][0]['attributes']['RAYO'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['INUNDA'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['AMIT_1'].capitalize()]
            
            ValoreS.append((
                    alpha['results'][0]['value']['features'][0]['attributes']['DIS_HIDRA'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Tipo_Espac'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Tipo_Mater'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Material'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Nombre_1'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Estación'],
                    alpha['results'][0]['value']['features'][0]['attributes']['DIS_BOMBERO'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Dirección'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Teléfonos'],
                    alpha['results'][0]['value']['features'][0]['attributes']['DIS_CAI'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Descripción'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Horario'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Direccion_Sitio'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Telefono'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Correo_Electronico'],
                    alpha['results'][0]['value']['features'][0]['attributes']['DIS_POLI'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Descripción_1'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Dirección_Sitio'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Telefono_1'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Correo_Electronico_1'],                        
                    alpha['results'][0]['value']['features'][0]['attributes']['Presion'],
                    alpha['results'][0]['value']['features'][0]['attributes']['DIS_TRANSMI'],
                    alpha['results'][0]['value']['features'][0]['attributes']['DIS_HOSPI'],
                    alpha['results'][0]['value']['features'][0]['attributes']['DIS_IPS'],
                    alpha['results'][0]['value']['features'][0]['attributes']['DIS_SERVI'],
                    alpha['results'][0]['value']['features'][0]['attributes']['NIVEL_SUST'],
                    alpha['results'][0]['value']['features'][0]['attributes']['PARARRAYOS'],
                    alpha['results'][0]['value']['features'][0]['attributes']['RED_ELECTRICA'],
                    alpha['results'][0]['value']['features'][0]['attributes']['USO'],
                    alpha['results'][0]['value']['features'][0]['attributes']['RESTAURANTES'],
                    alpha['results'][0]['value']['features'][0]['attributes']['ACT_INCENDIO'],
                    alpha['results'][0]['value']['features'][0]['attributes']['G_AMEN_PRE'],
                    alpha['results'][0]['value']['features'][0]['attributes']['amenazaEncharca'],
                    alpha['results'][0]['value']['features'][0]['attributes']['INUNDA'],
                    alpha['results'][0]['value']['features'][0]['attributes']['TIPO_ZI'],
                    alpha['results'][0]['value']['features'][0]['attributes']['NOMBRE_ZI']
                    ))
            ConceptoManzaneo = []
            ConceptoManzaneo.append(alpha["results"][0]["value"]["features"][0]["attributes"]['PROHIB'])
    else:
        print("No hay resultados en alpha")
        pass

    print("paso cuadro de amenaza")
    
    # ConceptoManzaneo = [None]
    # if not alpha["results"][0]["value"]["features"] == []:
    #     ConceptoManzaneo = []
    #     ConceptoManzaneo.append(alpha["results"][0]["value"]["features"][0]["attributes"]['PROHIB'])

    colors = ['rgb(51.0, 128.0, 0.0)', 'rgb(102.0, 128.0, 0.0)', 'rgb(128.0, 102.0, 0.0)', 'rgb(128.0, 51.0, 0.0)', 'rgb(128.0, 0.0, 0.0)']
    colors2 = n_colors('rgb(249, 249, 249)', 'rgb(179, 179, 179)', 5, colortype='rgb')
    ame = []
    for i in range(0, len(MatrizAmenazas)):
        if (MatrizAmenazas[i].lower() == "bajo" or MatrizAmenazas[i].lower() == "baja" or MatrizAmenazas[i].lower() == "baja o muy baja"):
            ame.append(0)
        elif (MatrizAmenazas[i].lower() == "media baja" or MatrizAmenazas[i].lower() == "medio bajo" or MatrizAmenazas[i].lower() == "medio-bajo"):
            ame.append(1)
        elif (MatrizAmenazas[i].lower() == "media" or MatrizAmenazas[i].lower() == "medio"):
            ame.append(2)
        elif (MatrizAmenazas[i].lower() == "media alta" or MatrizAmenazas[i].lower() == "medio alto" or MatrizAmenazas[i].lower() == "medio-alto"):
            ame.append(3)
        elif (MatrizAmenazas[i].lower() == "alto" or MatrizAmenazas[i].lower() == "alta"):
            ame.append(4)
        elif (MatrizAmenazas[i].lower() == "sin información" or MatrizAmenazas[i].lower() == "sin informacion"):
            ame.append(0)

    #####################

    #Tabla de color con las amenazas

    goldbach = pd.concat([pd.Series(["Terremoto", "Vientos", "Remoción en masa", "Sustracción", "Orden Público", "Rayos", "Inundación", "AMIT"]), pd.Series(ame), pd.Series(MatrizAmenazas)], axis=1).sort_values(by=[1],axis=0)
    goldbach = goldbach.fillna(value={1:"0"})
    goldbach[1] = goldbach[1].astype(int)


    fig = go.Figure(data=[go.Table(header=dict(align=['right','center'],values=['AMENAZA', 'NIVEL'],     line_color='rgb(249,249,249)', fill_color='rgb(249,249,249)',font=dict(color='black', size=10)),
                    cells=dict(align=['right','center'],values=[goldbach[0], goldbach[2]],
                        line_color=[np.array(colors2)[goldbach[1]],np.array(colors)[goldbach[1]]],
        fill_color=[np.array(colors2)[goldbach[1]],np.array(colors)[goldbach[1]]], font=dict(color=["black", "white"], size=10)))
        ])

    fig.update_layout(
        autosize=True,
        width=360.6,
        height=206.4,
            margin=dict(
            l=0,
            r=0,
            b=0,
            t=6.4,
            pad=4
        ),
        paper_bgcolor="rgb(249,249,249)",
    )
    print("paso tabla")
    fig.write_image("Archivos/PNG/ID/" + str(DireccioN[0]) + "_tabla" + ".png", scale=2) # scale=4
    
# MATRIZ MANZANEO    

    

    colors = ['rgb(51.0, 128.0, 0.0)', 'rgb(102.0, 128.0, 0.0)', 'rgb(128.0, 102.0, 0.0)', 'rgb(128.0, 51.0, 0.0)', 'rgb(128.0, 0.0, 0.0)']
    colors2 = n_colors('rgb(249, 249, 249)', 'rgb(179, 179, 179)', 5, colortype='rgb')

    ameManz = []
    ameManzIn = ["No hay información"]
    IsNone = True

    print(MatrizAmenazasManzaneo)

    for i, elem in enumerate(MatrizAmenazasManzaneo, start = 1):
        if elem is not None:
            IsNone = False
            try:
                if (elem.lower() == "bajo" or elem.lower() == "baja" or elem.lower() == "baja o muy baja"):
                    ameManz.append(0)
                elif (elem.lower() == "media baja" or elem.lower() == "medio bajo" or elem.lower() == "medio-bajo"):
                    ameManz.append(1)
                elif (elem.lower() == "media" or elem.lower() == "medio"):
                    ameManz.append(2)
                elif (elem.lower() == "media alta" or elem.lower() == "medio alto" or elem.lower() == "medio-alto"):
                    ameManz.append(3)
                elif (elem.lower() == "alto" or elem.lower() == "alta"):
                    ameManz.append(4)
                elif (elem.lower() == "sin información" or elem.lower() == "sin informacion"):
                    ameManz.append(0)
            except AttributeError as e:
                print(f"Error en el índice {i}: {e}")
        elif elem is None:
            ameManz.append(0)
            IsNone = True
            print("Es none")
            print(ameManzIn)

    MatrizAmenazasManzaneo = ["Sin información" if pd.isna(val) else val for val in MatrizAmenazasManzaneo]

    goldbach = pd.concat([pd.Series(["Incendio_M", "Sustraccion_M", "Anegacion_M", "Terremoto_M", "AMIT_M", "Daño Electrico_M", "Vientos_M"]), pd.Series(ameManz), pd.Series(MatrizAmenazasManzaneo)], axis=1).sort_values(by=[1], axis=0)
    goldbach = goldbach.fillna(value={1: "0"})
    goldbach[1] = goldbach[1].astype(int)


    fig2 = go.Figure(data=[go.Table(header=dict(align=['right','center'],values=['AMENAZA', 'NIVEL'],     line_color='rgb(249,249,249)', fill_color='rgb(249,249,249)',font=dict(color='black', size=10)),
                    cells=dict(align=['right','center'],values=[goldbach[0], goldbach[2]],
                        line_color=[np.array(colors2)[goldbach[1]],np.array(colors)[goldbach[1]]],
        fill_color=[np.array(colors2)[goldbach[1]],np.array(colors)[goldbach[1]]], font=dict(color=["black", "white"], size=10)))
        ])

    fig2.update_layout(
        autosize=True,
        width=300.6,
        height=200.4,
            margin=dict(
            l=0,
            r=0,
            b=0,
            t=6.4,
            pad=4
        ),
        paper_bgcolor="rgb(249,249,249)",
    )
    print("paso tabla")


    fig2.write_image("Archivos/PNG/ID/" + str(DireccioN[0]) + "_tablaM" + ".png", scale=4) # scale=4
    
    
    class PDF(FPDF):
        def footer(self):
            # Position at 1.5 cm from bottom
            self.set_y(-0.59)
            # Arial italic 8
            self.set_font('Arial', 'I', 8)
            # Text color in gray
            self.set_text_color(128)
            # Page number
            self.cell(0, .4, 'Page ' + str(self.page_no()), 0, 0, 'C')

    #################

    amenaza_terremoto = None
    if not MatrizAmenazas == []:
        amenaza_terremoto = MatrizAmenazas[0]
        if "MEDIO-BAJO" in amenaza_terremoto.upper():
            amenaza_terremoto = 2
        elif "MEDIO-ALTO" in amenaza_terremoto.upper():
            amenaza_terremoto = 4
        elif "BAJO" in amenaza_terremoto.upper():
            amenaza_terremoto = 1
        elif "MEDIO" in amenaza_terremoto.upper():
            amenaza_terremoto = 3
        elif "ALTO" in amenaza_terremoto.upper():
            amenaza_terremoto = 5

    amenaza_terremoto_niveles_descripcion = "bajo < 0.3 G, medio-bajo 0.3 < Sa <== 0.4 G, medio 0.4 < Sa <== 0.7 G, medio alto 0.7 < Sa <== 0.8 G, alto Sa > 0.8 G"
    terremoto_riesgo = None

    
    

    #Base de datos SIRE
    sql_sire = f"""SELECT * FROM "SIRE_0221"
    WHERE STRPOS("Dirección", '{DIRECCION}') = 1"""
    sire = pd.read_sql(sql_sire, con) 

    #Texto para el PDF

    if info_catastro == True:
        if len(ConceptoManzaneo) == 0:
            
            ConceptoManzaneo = "Sin información"
            pass
        else:
            alerta_sire = f"""Alerta SIRE:
            {sire[["Fecha reporte", "Tipo de afectación"]]}.
        Alerta Zona de Alto Riesgo no mitigable: {CatastrO[0][10]}.
        Concepto manzaneo: {ConceptoManzaneo[0]}
    """
    if is_cc == True:
        tomador = "Persona Natural"
        perfil_txt = razon_social
        numero_pisos = ConstruccioN[0]
        numero_semi_sotanos = ConstruccioN[1]
        numero_sotanos = ConstruccioN[2]
        numero_piso_semi_sotanos_sotanos = pd.concat([pd.DataFrame(numero_pisos), pd.DataFrame(numero_semi_sotanos), pd.DataFrame(numero_sotanos)], axis = 1)
        detalle_propiedad = f"""Área terreno: {CatastrO[0][0][0]} m2. Año de la construcción: {CatastrO[0][0][2]}. Área construida: {CatastrO[0][0][1]} m2. Área uso: {CatastrO[0][0][3]} m2.
        Clasificación del predio en función del tipo de propiedad: {CatastrO[0][7]}.
        Zona Homogénea Física. {CatastrO[0][8]}. {CatastrO[0][11]}. Vías: {CatastrO[0][12]}, {CatastrO[0][13]}, {CatastrO[0][14]}.
        Estrato socioeconómico. Valor metro cuadrado terreno, avalúo comercial y avalúo catastral (manzana):
        {estrato[["ESoChip", "ESoEstrato"]]}
        {valor_metro[["V_REF", "ANO"]].sort_values(by=["ANO"],axis=0)}
        {avaluos[["AVALUO_COM", "AVALUO_CAT"]]}
        """
        acabados_property = f"""Tipo de acabado de la fachada: {CatastrO[0][5]}. Tipo de cubierta y muros de los Acabados: {CatastrO[0][15]}. Tipo de acabado de los pisos: {CatastrO[0][16]}. Estado de los acabados: {CatastrO[0][6]}.
        """
        estructura_property = f"""PreFCalif: {predios["PreFCalif"].iloc[U]}
        Tipo de armazón: {CatastrO[0][1]}. Tipo de muros: {CatastrO[0][2]}. Tipo de cubierta: {CatastrO[0][3]}. Estado de la estructura: {CatastrO[0][4]}. {CatastrO[0][9]}
        """
        construcciones_lote = f"""Número de pisos, semisótanos y sótanos:
        {numero_piso_semi_sotanos_sotanos}
        """
    elif info_catastro == False:
        perfil_txt = ""
        perfil_emis = ""
        if not list(razon_social) == []:
            perfil_txt = f"""Razón social: {razon_social}
        Actividad económica: {ciiu_numero} {ciiu_dado}.
        Departamento: {departamento_principal}, municipio: {municipio_principal}, dirección principal: {direccion_principal}, teléfono(s): {telefono_principal} / {telefono2_principal}
        """
        perfil_emis = f"""{emis}"""
        numero_pisos = "Sin información"
        numero_semi_sotanos = "Sin información"
        numero_sotanos = "Sin información"
        numero_piso_semi_sotanos_sotanos = "Sin información"
        detalle_propiedad = f"""Área terreno: Sin información m2. Año de la construcción: Sin información. Área construida: Sin información
        Clasificación del predio en función del tipo de propiedad: Sin información.
        Zona Homogénea Física. Sin información. Sin información. Vías: Sin información, Sin información, Sin información.
        Estrato socioeconómico. Valor metro cuadrado terreno, avalúo comercial y avalúo catastral (manzana): Sin información
        """
        acabados_property = f"""Tipo de acabado de la fachada: Sin información. Tipo de cubierta y muros de los Acabados: Sin información. Tipo de acabado de los pisos: Sin información. Estado de los acabados: Sin información.
        """
        estructura_property = f"""PreFCalif: Sin información
        Tipo de armazón: Sin información. Tipo de muros: Sin información. Tipo de cubierta: Sin información. Estado de la estructura: Sin información. Sin información
        """
        construcciones_lote = f"""Número de pisos, semisótanos y sótanos:
        {numero_piso_semi_sotanos_sotanos}
        """
        if not nombre_comercial == None:
            tomador = nombre_comercial
        else:
            tomador = razon_social
        input = f"""{DireccioN[0]}"""
    else:    
        perfil_txt = ""
        perfil_emis = ""
        if not list(razon_social) == []:
            perfil_txt = f"""Razón social: {razon_social}
        Actividad económica: {ciiu_numero} {ciiu_dado}.
        Departamento: {departamento_principal}, municipio: {municipio_principal}, dirección principal: {direccion_principal}, teléfono(s): {telefono_principal} / {telefono2_principal}
        """
        perfil_emis = f"""{emis}"""
        numero_pisos = ConstruccioN[0]
        numero_semi_sotanos = ConstruccioN[1]
        numero_sotanos = ConstruccioN[2]
        numero_piso_semi_sotanos_sotanos = pd.concat([pd.DataFrame(numero_pisos), pd.DataFrame(numero_semi_sotanos), pd.DataFrame(numero_sotanos)], axis = 1)
        detalle_propiedad = f"""Área terreno: {CatastrO[0][0][0]} m2. Año de la construcción: {CatastrO[0][0][2]}. Área construida: {CatastrO[0][0][1]} m2. Área uso: {CatastrO[0][0][3]} m2.
        Clasificación del predio en función del tipo de propiedad: {CatastrO[0][7]}.
        Zona Homogénea Física. {CatastrO[0][8]}. {CatastrO[0][11]}. Vías: {CatastrO[0][12]}, {CatastrO[0][13]}, {CatastrO[0][14]}.
        Estrato socioeconómico. Valor metro cuadrado terreno, avalúo comercial y avalúo catastral (manzana):
        {estrato[["ESoChip", "ESoEstrato"]]}
        {valor_metro[["V_REF", "ANO"]].sort_values(by=["ANO"],axis=0)}
        {avaluos[["AVALUO_COM", "AVALUO_CAT"]]}
        """
        acabados_property = f"""Tipo de acabado de la fachada: {CatastrO[0][5]}. Tipo de cubierta y muros de los Acabados: {CatastrO[0][15]}. Tipo de acabado de los pisos: {CatastrO[0][16]}. Estado de los acabados: {CatastrO[0][6]}.
        """
        estructura_property = f"""PreFCalif: {predios["PreFCalif"].iloc[U]}
        Tipo de armazón: {CatastrO[0][1]}. Tipo de muros: {CatastrO[0][2]}. Tipo de cubierta: {CatastrO[0][3]}. Estado de la estructura: {CatastrO[0][4]}. {CatastrO[0][9]}
        """
        construcciones_lote = f"""Número de pisos, semisótanos y sótanos:
        {numero_piso_semi_sotanos_sotanos}
        """
        if not nombre_comercial == None:
            tomador = nombre_comercial
        else:
            tomador = razon_social
        input = f"""{DireccioN[0]}
        
    Barrio: {SectoR[0][0]}
    UPZ: {SectoR[0][1]}
    Localidad: {SectoR[0][2]}
    {municipio}
    Latitud, longitud: {LatloN[0]}
    NIT: {nit}
    {tomador}
    Valor a asegurar: {valor_a_asegurar}

"""
    bomberos = ""
    if not ValoreS == []:
        bomberos = f"""Distancia a hidrante: {round(ValoreS[0][0], 2)} m, {ValoreS[0][1]}, {ValoreS[0][2]}, {ValoreS[0][3]}. {ValoreS[0][5]} {ValoreS[0][4]}, distancia {round(ValoreS[0][6], 2)} m, {ValoreS[0][7]}, contacto {ValoreS[0][8]}.
"""
    policia = ""
    if not ValoreS == []:
        policia = f"""Distancia CAI: {round(ValoreS[0][9], 2)} m, {ValoreS[0][10]}, {ValoreS[0][12]}, atención {ValoreS[0][11]}, teléfono {ValoreS[0][13]}, correo {ValoreS[0][14]}. Distancia estación: {round(ValoreS[0][15], 2)} m, {ValoreS[0][16]}, {ValoreS[0][17]}, contacto {ValoreS[0][18]}, {ValoreS[0][19]}.
"""

    sql_incurridos = f"""SELECT * FROM siniestros_incurrido
                    WHERE "KEY_ID_ASEGURADO" = '{str(nit)}'"""

    incurrido = pd.read_sql(sql_incurridos, con) 
    
    if incurrido.empty:
        pass
    else:
        
        def separar_fecha(fecha):
            partes_fecha = fecha.split("/")
            dia = int(partes_fecha[0])
            mes = int(partes_fecha[1])
            año = int(partes_fecha[2])
            return dia, mes, año

        fechas_separadas = incurrido["FECHA_SINIESTRO"].apply(separar_fecha)
        fechas_separadas_df = pd.DataFrame(fechas_separadas.tolist(), columns=["DIA", "MES", "AÑO"])
        incurrido = pd.concat([incurrido, fechas_separadas_df], axis=1)
        
        incurrido["AÑO"] = incurrido["AÑO"].astype(int)
        incurrido_ordenado = incurrido.sort_values(by="AÑO")
        
        print(incurrido_ordenado)
        
        conteo_cobertura = incurrido["NOMBRE_COBERTURA"].value_counts()
        print(conteo_cobertura.tolist())
        
        sql_total_incurridos = f"""SELECT SUM("INCURRIDO") AS TOTAL_INCURRIDO FROM "siniestros_incurrido"
                        WHERE "KEY_ID_ASEGURADO" = '{str(nit)}'"""
        total_incurrido = pd.read_sql(sql_total_incurridos, con)         
      
        sql_fechas_incurridos = f"""SELECT "FECHA_SINIESTRO", "INCURRIDO" FROM "siniestros_incurrido"
                        WHERE "KEY_ID_ASEGURADO" = '{str(nit)}'"""
        fechas_incurrido = pd.read_sql(sql_fechas_incurridos, con) 

        fechas_separadas = fechas_incurrido["FECHA_SINIESTRO"].apply(separar_fecha)
        fechas_separadas_df = pd.DataFrame(fechas_separadas.tolist(), columns=["DIA", "MES", "AÑO"])
        fechas_incurrido = pd.concat([fechas_incurrido, fechas_separadas_df], axis=1)
        fechas_incurrido_ordenado = fechas_incurrido.sort_values(by="AÑO") 

        total_años = fechas_incurrido_ordenado["AÑO"].nunique()  
        total_incurrido = fechas_incurrido_ordenado["INCURRIDO"].sum()
                
        promedio_incurridos_anual = total_incurrido/total_años
        
        print(f'El total de años es: {total_años}')
        print(f'El total de incurrido es: {total_incurrido}')
        
        total_incurrido_formateado = "{:,.0f}".format(total_incurrido)
        promedio_incurrido_formateado = "{:,.0f}".format(promedio_incurridos_anual)
        
        
    if is_cc == False:
        sql_siar = f"""SELECT * FROM "SIAR_BD"
        WHERE "NUMERO_IDENTIFICACION_CLIENTE" = '{int(nit)}'
        """
        siar = pd.read_sql(sql_siar, con) 
        if not len(siar) == 0:
            lista = []
            lista2 = []
            lista3 = []
            for i in siar["ANO_SOLICITUD"].unique():
                lista.append((len(siar[siar["ANO_SOLICITUD"] == i]),i))
                lista2.append(len(siar[siar["ANO_SOLICITUD"] == i]))
            for i in lista:
                if i[0] == max(lista2):
                    lista3.append(i[1])
            siar = siar[siar["ANO_SOLICITUD"] == max(lista3)]
            siar = siar[['ENUNCIADO_PREGUNTA', 'VALOR_RESPUESTA']]
        else:
            siar = "No figura."
        sql_siniestros = f"""SELECT * FROM siniestros_nit_0621
        WHERE "NIT" = {nit}"""
        siniestros = pd.read_sql(sql_siniestros, con) 
        if len(siniestros) == 0:
            siniestros = "No presenta."
        siniestralidad = f"""{siniestros}
        """
        siar_base = f"""{siar}
        """
        
        print(siniestros)
        
    else:
        siniestralidad = "No hay información"
        pass

    #VALIDACIÓN DE IMÁGENES STREETVIEW VÁLIDAS
    response = requests.get('https://maps.googleapis.com/maps/api/streetview/metadata?size=1000x800&location='+str(LATITUD)+','+str(LONGITUD)+'&fov=90&heading=90&pitch=0&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc')

    if response.status_code == 200:
        
        data = response.json()
        print(data)
        if data.get("status") == "ZERO_RESULTS":
            imagen_funcional = False
        else:
            imagen_funcional = True
    else:
        print('La solicitud no fue exitosa. Código de estado:', response.status_code)
        imagen_funcional = False

    print(imagen_funcional)
    
        
    #ANEXOS
    #Mapas
    f =open('Archivos/Mapas/ID/'+str(DIRECCION)+'.png','wb')
    f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/staticmap?center='+str(LATITUD)+','+str(LONGITUD)+'&zoom=18&size=600x600&maptype=roadmap&markers=color:red%7Clabel:%7C'+str(LATITUD)+','+str(LONGITUD)+'&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
    f.close()
    f =open('Archivos/Mapas/ID/'+str(DIRECCION)+'S.png','wb')
    f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/staticmap?center='+str(LATITUD)+','+str(LONGITUD)+'&zoom=18&size=600x600&maptype=satellite&markers=color:red%7Clabel:%7C'+str(LATITUD)+','+str(LONGITUD)+'&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
    f.close()
    
    if imagen_funcional == True:
        #Streetview
        f = open('Archivos/Mapas/ID/'+str(DIRECCION)+'C0.jpeg','wb')
        f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/streetview?size=1000x800&location='+str(LATITUD)+','+str(LONGITUD)+'&fov=90&heading=0&pitch=0&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
        f.close()
        f = open('Archivos/Mapas/ID/'+str(DIRECCION)+'C90.jpeg','wb')
        f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/streetview?size=1000x800&location='+str(LATITUD)+','+str(LONGITUD)+'&fov=90&heading=90&pitch=0&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
        f.close()
        f = open('Archivos/Mapas/ID/'+str(DIRECCION)+'C180.jpeg','wb')
        f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/streetview?size=1000x800&location='+str(LATITUD)+','+str(LONGITUD)+'&fov=90&heading=180&pitch=0&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
        f.close()
        f = open('Archivos/Mapas/ID/'+str(DIRECCION)+'C270.jpeg','wb')
        f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/streetview?size=1000x800&location='+str(LATITUD)+','+str(LONGITUD)+'&fov=90&heading=270&pitch=0&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
        f.close()

    else:
        def formatear_direccion(direccion):
            # Dividir la dirección en partes
            partes = direccion.split()
            print(partes)
            # Obtener las partes relevantes de la dirección
            calle = partes[0]  # Suponiendo que siempre la primera parte es la calle
            numeros = partes[1]  # Suponiendo que la segunda parte son los números de la dirección
            calle_2 = partes[2] # Suponiendo que la última parte es la ciudad
            complemento = partes [3]

            # Formatear la dirección según el nuevo formato
            direccion_formateada = calle + numeros + ',' + calle_2  + '+' + complemento + ',Bogota,BOG'

            return direccion_formateada

        direccion_formateada = formatear_direccion(DIRECCION)
        print(direccion_formateada)
        
        #Streetview
        f = open('Archivos/Mapas/ID/'+str(DIRECCION)+'C0.jpeg','wb')
        f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/streetview?size=1000x800&location='+str(direccion_formateada)+'&fov=90&heading=0&pitch=0&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
        f.close()
        f = open('Archivos/Mapas/ID/'+str(DIRECCION)+'C90.jpeg','wb')
        f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/streetview?size=1000x800&location='+str(direccion_formateada)+'&fov=90&heading=90&pitch=0&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
        f.close()
        f = open('Archivos/Mapas/ID/'+str(DIRECCION)+'C180.jpeg','wb')
        f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/streetview?size=1000x800&location='+str(direccion_formateada)+'&fov=90&heading=180&pitch=0&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
        f.close()
        f = open('Archivos/Mapas/ID/'+str(DIRECCION)+'C270.jpeg','wb')
        f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/streetview?size=1000x800&location='+str(direccion_formateada)+'&fov=90&heading=270&pitch=0&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
        f.close()
        

    ## Modelo knn
    data = pd.read_excel('Archivos/predSistema.xlsx')
    #LIMPIEZA DE DATOS
    data = data.drop(data[data['Material']=="Mixtas u Otro*"].index)
    data = data.drop(data[data['Sistema']==" Desconocido"].index)
    nan_rows = data[data.isnull().any(1)]
    data = data.dropna(how='any')

    #MAPEAR LA COLUMNA DE INTERES
    #Aquellas propiedades que registan en material mixtas u otro no tienen ningun sistema, para este al igual que el de desconocido se dejara como porticos
    data['Sistema'] = data['Sistema'].map({'Muros':1, 'Pórticos':0, 'Dual':2, 'Reforzada':6, 'No reforzada':7,
        'Confinada':5, 'Prefabricado':3,' Reticular celulado':4, ' Pórticos no arriostrados':9,
        ' Pórticos y paneles en madera':0, ' bahareque ':10,
        ' Pórticos arriostrados':8}).astype(int)

    #Mapear columna de material para obtener una mejor visualización
    data['Material'] = data['Material'].map({'Concreto':1, 'Mamposteria':2,'Acero':4, 'Madera':5,'Adobe':6}).astype(int)

    x_data = data.drop(['Sistema'],axis=1)
    y_data = data['Sistema']
    MinMaxScaler = preprocessing.MinMaxScaler()
    X_data_minmax = MinMaxScaler.fit_transform(x_data)

    #Se realiza la division de los datos en entrenamiento y prueba, dejando el 80% y 20% respectivamente
    X_train, X_test, y_train, y_test = train_test_split(x_data, y_data,test_size=0.2, random_state = 1)
    knn_clf=KNeighborsClassifier(metric='minkowski', n_neighbors=5, p=2, weights='uniform')
    knn_clf.fit(X_train,y_train)
    ypred=knn_clf.predict(X_test)

    mat = 0
    escala = "NA"
    concepto = "NA"
    sis = "Desconocido"
    columnas =  pd.read_excel("Archivos/Columnas.xlsx")
    malla = pd.read_csv("Archivos/mallaRiesgoFinal (1).csv")
    distancias = []
    numRegion = 0

    col = 0
    
    if info_catastro == True:
        material = CatastrO[0][1]
        
        try:
            NPIS = max([int(temp)for temp in  str(ConstruccioN[0]).split() if temp.isdigit()])
        except:
            NPIS = "Sin información"
        if CatastrO[0][0][2] is not None:
            RCON = int(CatastrO[0][0][2])
        else:
            RCON = 1999 
    else:
        material = "Sin información"
        NPIS = "Sin información"
        RCON = "Sin información"
        
    sistema = ""
    
    if LATITUD is not None or LONGITUD is not None:
        if isinstance(LONGITUD, str):
            LONGITUD = float(LONGITUD)
    
        if isinstance(LATITUD, str):
            LATITUD = float(LATITUD)
        nlo = nsmallest(1, malla.iloc[:, 1], key=lambda x: abs(x-LONGITUD))[0]
        nla = nsmallest(1, malla.iloc[:, 2], key=lambda x: abs(x-LATITUD))[0]
        punto = [(nlo, nla)]
    else:
         
        punto = "Sin información"
        pass
        
    if material == "Concreto":
        mat = 1
    elif material == "Mamposteria":
        mat = 2
    elif material == "Acero":
        mat = 4
    elif material == "Madera":
        mat = 5
    elif material == "Adobe":
        mat = 6
    else:
        mat = "Sin información"

    # OBTENER NUMERO DE COLUMNA PARA LA INFORMACION RECIBIDA

    def obtenerColumna(NPIS, RCON, material, sistema):
        print("NPIS:",NPIS)
        print("RCON:",RCON)
        print("Material",material)
        print("Sistema:",sistema)
        for i in range (len(columnas)):
            if (material == columnas.iloc[i, 0]) and (sistema == columnas.iloc[i, 1]) and (columnas.iloc[i, 2] <= NPIS <= columnas.iloc[i, 3]) and (columnas.iloc[i, 4] <= RCON <= columnas.iloc[i, 5]):
                col = columnas.iloc[i, 6]
                return col

    for i in range(len(malla)):
        distancias.append(((distance.cdist(punto, [(malla.iloc[i][1], malla.iloc[i][2])], 'euclidean'))))
    
    puntoMalla = distancias.index(min(distancias))

    print(mat, NPIS, RCON)
    X_test = [[mat, NPIS, RCON, 1997]]
    try:
        sistema= knn_clf.predict(X_test)
    except:
        sis = "Desconocido"
    #TRANSFORMACIÓN SISTEMAS
    if sistema == 0:
        sis = "Pórticos"
    if sistema == 1:
        sis = "Muros"
    if sistema == 2:
        sis = "Dual"
    if sistema == 3:
        sis = "Prefabricado"
    if sistema == 4:
        sis = "Reticular"
    if sistema == 5:
        sis = "Confinada"
    if sistema == 6:
        sis = "Reforzada"
    if sistema == 7:
        sis = "Reforzada"
    if sistema == 8:
        sis = "Porticos arriostrados"
    if sistema == 9:
        sis = "Porticos no arriostrados"
    if sistema == 10:
        sis = "Bahareque"
    if sistema == 10:
        sis = "Adobe"
    print(puntoMalla)
    
    
    try:
        columna = obtenerColumna(NPIS, RCON, material, sis)
        riesgoSismo = (malla.iloc[puntoMalla][columna+2]*100)

        if riesgoSismo <= 3 :
            escala = "Muy Bajo"
            concepto = "Asegurable" 
        if 3 < riesgoSismo <= 15 :
            escala = "Bajo"
            concepto = "Asegurable" 
        if 15 < riesgoSismo <= 35 :
            escala = "Moderado"
            concepto = "Asegurable" 
        if 35 < riesgoSismo <= 55 :
            escala = "Alto"
            concepto = "No asegurable" 
        if 55 < riesgoSismo:
            escala = "Muy Alto"
            concepto = "No asegurable" 

        print("La columna es ", columna)
        print("Latitud cercana", nla)
        print("Longitud cercana", nlo)
        print("NPIS", NPIS)
        print("El punto de la malla es :", puntoMalla)
        print("El riesgo de sismo para esta propiedad es de:",riesgoSismo * 100, "%")
    except:
        riesgoSismo = "Desconocido"
        escala = "Moderado"
        concepto = "Sin información suficiente"
    
    if info_catastro == True:
        if RCON < 1985:
            norma = "Dada la fecha de construcción, se puede afirmar que la propiedad fue ejecutada sin ninguna norma sismo resistente, lo cual puede aumentar su nivel de riesgo ante un evento sismico. "
        if 1985 <= RCON < 1999:
            norma = "Esta propiedad fue construida después de la primera norma sismo resistente lo cual nos da un menor nivel de riesgo, debido a que ya se tienen las primeras consideraciones de diseño que evitan daños masivos en las estructuras por un sismo."
        if 1999 <= RCON < 2010:
            norma = "Esta propiedad fue construida después de la actualización a la norma sismo resistente de 1999 lo cual nos da un menor nivel de riesgo comparado a estructuas mas antiguas, debido a que ya se tienen mejores consideraciones de diseño que evitan daños masivos en las estructuras por un sismo."
        if RCON >= 2010:
            norma = "Dada la fecha de construccion es una estructura reciente y debe presentar un alto nivel de diseño,lo cual disminuye la probabilidad de tener afectaciones considerables ante eventos sismicos"
    else:
        norma = "Sin información"
        
    ant = pd.read_excel("Archivos/ANTIGUEDADES.xlsx")
    ult = pd.read_excel("Archivos/Siniestros_Reportados.xlsx")
    vig = pd.read_excel("Archivos/vigentes.xlsx")


    for i in range(len(vig)):
        if vig.iloc[i][0] == nit:
            vigencia = "Activo"
            break
        else:
            vigencia = "Inactivo"

    for i in range(len(ant)):
        if ant.iloc[i][0] == nit:
            antiguedad = ant.iloc[i][1]
            break

    for i in range(len(ult)):
        if ult.iloc[i][0] == nit:
            ultSiniestro = ult.iloc[i][1]
            break

    try:
        ultSiniestro = str(ultSiniestro).replace("'", "").replace(" 00:00:00", "")
    except:
        pass

    try:
        antiguedad = str(antiguedad).replace("'", "").replace(" 00:00:00", "")
        anti = True
    except:
        anti = False
        pass
    
    #MODELO SUSTRACCIÓN
    categorias = pd.read_excel("Archivos/categorias.xlsx")

    distancias = [ValoreS[0][6], ValoreS[0][9], ValoreS[0][22], ValoreS[0][23], ValoreS[0][21], ValoreS[0][24]]
    
    #CALCULO DE LAS CATEGORIAS DE ACUERDO AL ARCHIVO DESIGNADO (CON PROPORCIÓN)

    IPSCate = 3

    for i in reversed(range(len(categorias))):
        if categorias.iloc[i][3] == "No especificado":
            categorias.iloc[i][3] = 0
        if distancias[0]< categorias.iloc[i][2] and distancias[0]> categorias.iloc[i-1][2]:
            bomeberosCate = categorias.iloc[i-1][1]
        if distancias[1]< categorias.iloc[i][3] and distancias[1]> categorias.iloc[i-1][3]:
            CAICate = categorias.iloc[i-1][1]
        if distancias[2]< categorias.iloc[i][4] and distancias[2]> categorias.iloc[i-1][4]:
            hospitalesCate = categorias.iloc[i-1][1]
        if distancias[3]<= categorias.iloc[i][5] and distancias[3]> categorias.iloc[i-1][5]:
            IPSCate = categorias.iloc[i-1][1]
        if distancias[4]< categorias.iloc[i][6] and distancias[4]> categorias.iloc[i-1][6]:
            transmiCate = categorias.iloc[i-1][1]
        if distancias[5]< categorias.iloc[i][7] and distancias[5]> categorias.iloc[i-1][7]:
            gasolinaCate = categorias.iloc[i-1][1]
            
    print("Paso categorias")
    print(bomeberosCate)
    print(CAICate)
    print(hospitalesCate)
    print(IPSCate)
    print(transmiCate)
    print(gasolinaCate)
    
    calEntorno = round((bomeberosCate + CAICate + hospitalesCate + IPSCate + transmiCate + gasolinaCate) / 6)
    amenazaSus = ValoreS[0][25]
    riesgoSusV = round(calEntorno * amenazaSus)

    try:
        if calEntorno == 1:
            ento = "Baja"
            apre = "Favorable"
        if calEntorno == 2:
            ento = "Media baja"
            apre = "Favorable"
        if calEntorno == 3:
            ento = "Media"
            apre = "Favorable"
        if calEntorno == 4:
            ento = "Media alta"
            apre = "Desfavorable"
        
        if calEntorno == 5:
            ento = "Alta"
    except:
        ento = "Sin info"
    
    try:
        if amenazaSus == 1:
            proRobo = "Baja"
        if amenazaSus == 2:
            proRobo = "Media baja"
        if amenazaSus == 3:
            proRobo = "Media"
        if amenazaSus == 4:
            proRobo = "Media alta"
        if amenazaSus == 5:
            proRobo = "Alta"
    except:
        proRobo = "Sin info"
    print(proRobo)
    try:
        if 0 < riesgoSusV <= 2:
            riesgoSus = "Baja"
            conceptoSus = "Asegurable"
        if 2 < riesgoSusV <= 5:
            riesgoSus = "Media baja"
            conceptoSus = "Asegurable"
        if 5 < riesgoSusV <= 10:
            riesgoSus = "Media"
            conceptoSus = "Asegurable"
        if 10 < riesgoSusV <= 15:
            riesgoSus = "Media Alta"
            conceptoSus = "No asegurable"
        if 15 < riesgoSusV <= 20:
            riesgoSus = "Alta"
            conceptoSus = "No asegurable"
        if FueraSus == True:
            conceptoSus = "No asegurable"
    except:
        riesgoSus = "Media"
        conceptoSus = "Sin información suficiente"
         
    
    if ValoreS[0][34] is not None: 
        conceptoSus = "Asegurable"
        
        print(conceptoSus)



    #MODELO INCENDIO 

    #Bases Necesarias

    Base = pd.read_excel(r"Archivos/Modelo_Indencio.xlsx",
                        sheet_name="MODELO_COMPLETO", skiprows=1) # Informaccion del modelo completo

    Base2 = pd.read_excel(r"Archivos/Modelo_Indencio.xlsx",
                        sheet_name="MODELO_SIN_MANZANEO", skiprows=1) # Informaccion del modelo completo

    Politicas = pd.read_excel(r"Archivos/Calificacion act. property 2021.xlsx")

    ModeloCompleto = Base[["Nomenclatura", "Dominio", "Tipo", "Puntaje", "Peso"]] # Seleccion de algunas variables del modelo
    ModeloSinManz = Base2[["Nomenclatura", "Dominio", "Tipo", "Puntaje", "Peso"]]

    NombreVariables = ModeloCompleto.iloc[:, 0].unique() # Variables contempladas en el modelo
    NombreVariables2 = ModeloSinManz.iloc[:, 0].unique()

    pararrayos_inc = ValoreS[0][26]
    red_electrica_inc = ValoreS[0][27]
    uso_inc = ValoreS[0][28]
    restaurantes_inc = ValoreS[0][29]
    act_incendio_inc = ValoreS[0][30]
    g_amen_pre_inc = ValoreS[0][31]
    distHidrante = ValoreS[0][0] 
    distBomberos = ValoreS[0][6]

    
    if (pararrayos_inc is None) or (pd.isna(pararrayos_inc) == True):
        pararrayos_inc = "Sin Información"
         

    if (red_electrica_inc is None) or (pd.isna(red_electrica_inc) == True):
        red_electrica_inc = "Sin Información"
         

    if (uso_inc is None) or (pd.isna(uso_inc) == True):
        uso_inc = "Sin Información"
         

    if (restaurantes_inc is None) or (pd.isna(restaurantes_inc) == True):
        restaurantes_inc = "Sin Información"
         

    if (act_incendio_inc is None) or (pd.isna(act_incendio_inc) == True):
        act_incendio_inc = "Sin Información"
         

    if (g_amen_pre_inc is None) or (pd.isna(g_amen_pre_inc) == True):
        g_amen_pre_inc = "Sin Información"
         

    if (material is None) or (pd.isna(material) == True):
        material = "Sin Información"
         

    if (distHidrante is None) or (pd.isna(distHidrante) == True):
        distHidrante_inc = "Sin Información"
         
    if distHidrante <= 10:
        distHidrante_inc = "Menor a 10 metros"
    elif distHidrante >= 11 and distHidrante <= 20:
        distHidrante_inc = "Entre 11 y 20 metros"
    elif distHidrante >= 21 and distHidrante <= 30:
        distHidrante_inc = "Entre 21 y 30 metros"
    elif distHidrante >= 31 and distHidrante <= 40:
        distHidrante_inc = "Entre 31 y 40 metros"
    else:
        distHidrante_inc = "Mayor a 41 metros"

    if (distBomberos is None) or (pd.isna(distBomberos) == True):
        distBomberos_inc = "Sin Información"
         
    if distBomberos <= 1000:
        distBomberos_inc = "Menor a 1 km"
    elif distBomberos >= 1000 and distBomberos <= 3000:
        distBomberos_inc = "Entre 1 km y 3 km"
    elif distBomberos >= 3000 and distBomberos <= 7000:
        distBomberos_inc = "Entre 3 km y 7 km"
    elif distBomberos >= 7000 and distBomberos <= 10000:
        distBomberos_inc = "Entre 7 km y 10 km"
    else:
        distBomberos_inc = "Mayor a 10 km"

    if info_catastro == True:
        if (RCON is None) or (pd.isna(RCON) == True):
            RCON_inc = "Sin Información"
        
        if RCON < 1985:
            RCON_inc = "Previo a 1985"
        elif RCON >= 1985 and RCON <= 1997:
            RCON_inc = "Entre 1985 y 1997"
        elif RCON >= 1998 and RCON <= 2010:
            RCON_inc = "Entre 1998 y 2010"
        elif RCON >= 2011 and RCON <= 2022:
            RCON_inc = "Entre 2011 y 2022"
        else:
            RCON_inc = "Posterior a 2022"
    else:
        RCON_inc = "Sin información"

    print(NPIS)
    
    if NPIS == "Sin información":
        NPIS_inc = "Sin información"
    else:
        if NPIS == 1:
            NPIS_inc = "1 Piso"
        elif 2 <= NPIS <= 3:
            NPIS_inc = "Entre 2 y 3 pisos"
        elif 4 <= NPIS <= 7:
            NPIS_inc = "Entre 4 y 7 pisos"
        elif 8 <= NPIS <= 15:
            NPIS_inc = "Entre 8 y 15 Pisos"
        elif 16 <= NPIS <= 25:
            NPIS_inc = "Entre 16 y 25 pisos"
        elif 26 <= NPIS <= 35:
            NPIS_inc = "Entre 26 y 35 pisos"
        else:
            NPIS_inc = "Más de 35 pisos"


    longit_ciiu = len(ciiu_numero)
    
    print(f"La longitud del código CIUU es: {longit_ciiu}")
    print(f"El código CIIU es: {ciiu_numero}")
    
    if longit_ciiu == 0:
        print("No posee descripción de actividades económicas")
    
    # if is_cc == False:
    #     if ciiu_numero:  # Verificar si ciiu_numero no está vacío
    #         if any(int(ciiu_numero[0]) == Politicas["CODIGO CIIU"]):
    #             # politicas_incendio = Politicas["Politicas Incendio"][Politicas["CODIGO CIIU"]==int(ciiu_numero[0])].iloc[0]
    #             if politicas_incendio == "Sin Información":
    #                 politicas_incendio = Politicas["Calificación PR"][Politicas["CODIGO CIIU"]==int(ciiu_numero[0])].iloc[0]
    #         else:
    #             politicas_incendio = "Sin Información"
    #     else:
    #         politicas_incendio = "Sin Información" 
    # else:
    #     politicas_incendio = "Riesgo Tipo 3"
    
    Fila = [RCON_inc, NPIS_inc, material, distHidrante_inc, distBomberos_inc, pararrayos_inc, red_electrica_inc,
        uso_inc, restaurantes_inc, act_incendio_inc, g_amen_pre_inc, politicas_incendio]

    Fila2 = [RCON_inc, NPIS_inc, material, distHidrante_inc, distBomberos_inc,
        g_amen_pre_inc, politicas_incendio]

    riesgosCon = []

    fila = Fila
    fila2 = Fila2

    a = 0
    riesgoIncendioPeso = 0

    if (pararrayos_inc == "Sin Información") and (red_electrica_inc == "Sin Información") and (uso_inc == "Sin Información") and (restaurantes_inc == "Sin Información") and (act_incendio_inc == "Sin Información"):
        for i in range(0, len(ModeloSinManz)):
            for j in range(0, len(fila2)):
                if ModeloSinManz.iloc[i][1] == fila2[j]:
                    print(ModeloSinManz.iloc[i][1]+ " = " + str(ModeloSinManz.iloc[i][3]))
                    a = a + 1
                    riesgoIncendioPeso =  riesgoIncendioPeso + ModeloSinManz.iloc[i][3] * ModeloSinManz.iloc[i][4]
        riesgosCon.append(round(riesgoIncendioPeso, 2))
        print("Ponderacion =", riesgosCon[0])

    else:
        for i in range(0, len(ModeloCompleto)):
            for j in range(0, len(fila)):
                if ModeloCompleto.iloc[i][1] == fila[j]:
                    print(ModeloCompleto.iloc[i][1]+ " = " + str(ModeloCompleto.iloc[i][3]))
                    a = a + 1
                    riesgoIncendioPeso =  riesgoIncendioPeso + ModeloCompleto.iloc[i][3] * ModeloCompleto.iloc[i][4]
        riesgosCon.append(round(riesgoIncendioPeso, 2))
    
        print(f"El peso del riesgo de incendio es: {riesgoIncendioPeso}")
    
    conceptoIncendio = "Sin info"
    nivelIncendio = "Sin info"

    if riesgosCon[0] <= 3.13:
        conceptoIncendio = "Asegurable"
        nivelIncendio = "Bajo"
    if 3.13 < riesgosCon[0] <= 3.30:
        conceptoIncendio = "Asegurable"
        nivelIncendio = "Medio Bajo"
    if 3.31 < riesgosCon[0] <= 3.46:
        conceptoIncendio = "Asegurable"
        nivelIncendio = "Medio"
    if 3.47 < riesgosCon[0] <= 3.62:
        conceptoIncendio = "Asegurable"
        nivelIncendio = "Medio Alto"
    if 3.63 < riesgosCon[0]:
        conceptoIncendio = "No asegurable"
        nivelIncendio = "Alto"
        
    print(f"El concepto de asegurabilidad es: {conceptoIncendio}")
    print(f"El nivel de incendio es: {nivelIncendio}")

    #Modelo DXAEN
    from geopy.distance import geodesic
    estaciones_df = pd.read_excel('Archivos/EstacionesFinalDXA.xlsx')
    
    AmenazaEncharcamiento = ValoreS[0][32],
    INUNDACION = ValoreS[0][33]

    def NRIESGOCUBIERTA(CatastrO):
        if CatastrO[0][3] == 'eternit o teja de barro (cubierta sencilla)':
            return 5
        elif CatastrO[0][3] == 'azotea, aluminio, placa sencilla con eternit, o teja de barro':
            return 4
        elif CatastrO[0][3] == 'entrepiso (cubierta provisional) prefabricado':
            return 3
        elif CatastrO[0][3] == 'zinc, teja de barro, eternit rústico':
            return 2
        elif CatastrO[0][3] == 'placa impermeabilizada, cubierta lujosa u ornamental':
            return 1
        else:
            return 3  # Si no hay información, asignamos un riesgo de 3
    def NRIESGOEDAD(RCON):
        if RCON < 1985:
            return '5'
        elif 1985 <= RCON <= 1997:
            return '4'
        elif 1998 <= RCON <= 2010:
            return '3'
        elif 2011 <= RCON <= 2022:
            return '2'
        elif RCON > 2022:
            return '1'
        else:
             
            return 'Sin Información'
        
    def encontrar_estacion_y_NPA_mas_cercana(LATITUD, LONGITUD):
        estacion_mas_cercana = None
        distancia_minima = float('inf')
        NPA_estacion = None
        nombre_estacion = None

        for index, estacion in estaciones_df.iterrows():
            estacion_latitud = estacion['Latitud']
            estacion_longitud = estacion['Longitud']

            distancia = geodesic((LATITUD, LONGITUD), (estacion_latitud, estacion_longitud)).meters

            if distancia < distancia_minima:
                distancia_minima = distancia
                estacion_mas_cercana = estacion['Estacion']
                NPA_estacion = estacion['NPA']
                nombre_estacion = estacion['Estacion']
        if estacion_mas_cercana is not None:
            return estacion_mas_cercana, distancia_minima, NPA_estacion, nombre_estacion
        else:
            # Manejar el caso en el que no se encontró ninguna estación
            return None, None, None, None
    def NRIESGONPA(LATITUD, LONGITUD):
        # Llamada a la función para obtener la estación más cercana y su NPA
        _, _, NPA_estacion, _ = encontrar_estacion_y_NPA_mas_cercana(LATITUD, LONGITUD)

        if NPA_estacion is not None:
            if NPA_estacion >= 120:
                return '5'
            elif NPA_estacion >= 100:
                return '4'
            elif NPA_estacion >= 80:
                return '3'
            elif NPA_estacion >= 60:
                return '2'
            else:
                return '1'
        else:
             
            return 'Sin Información'

    def NRIESGOAENCHAR(AmenazaEncharcamiento):
        if AmenazaEncharcamiento == 'rojo':
            return 5
        elif AmenazaEncharcamiento == 'amarilla':
            return 4
        elif AmenazaEncharcamiento == 'oliva':
            return 2
        elif AmenazaEncharcamiento == 'verde':
            return 1
        else:
            return 3  # Sin información
    if info_catastro == True:  
        nivel_cubierta = NRIESGOCUBIERTA(CatastrO)
        nivel_año = int(NRIESGOEDAD(RCON))
    else:
        nivel_cubierta = 3
        nivel_año = 3
        
    nivel_amenaza = NRIESGOAENCHAR(AmenazaEncharcamiento)
    nivel_riesgo_estacion = int(NRIESGONPA(LATITUD, LONGITUD))

    peso_edad = 0.2375
    peso_cubierta = 0.2575
    peso_amenaza_encharcamiento = 0.2075
    peso_npa = 0.2875

    NivelRiesgoPonderado = (
    peso_edad * nivel_año +
    peso_cubierta * nivel_cubierta +
    peso_amenaza_encharcamiento * nivel_amenaza +
    peso_npa * nivel_riesgo_estacion) / (peso_edad + peso_cubierta + peso_amenaza_encharcamiento + peso_npa)
     
    if NivelRiesgoPonderado <= 3.51:
        conceptoDXAEN = "Asegurable"
        nivelDXAEN = "Bajo"
    elif 3.51 < NivelRiesgoPonderado <= 3.77:
        conceptoDXAEN = "Asegurable"
        nivelDXAEN = "Medio Bajo"
    elif 3.77 < NivelRiesgoPonderado <= 4.03:
        conceptoDXAEN = "Asegurable"
        nivelDXAEN = "Medio"
    elif 4.03 < NivelRiesgoPonderado <= 4.29:
        conceptoDXAEN = "No Asegurable"
        nivelDXAEN = "Medio Alto"
    elif 4.29 < NivelRiesgoPonderado:
        conceptoDXAEN = "No Asegurable"
        nivelDXAEN = "Alto"   

    #CREACIÓN DEL PDF
    
    #FUNCIÓN HEADER
    def header():
        pdf.set_font('Arial','B',15.0)
        pdf.set_y(0.05)
        pdf.set_x(0)
        pdf.set_fill_color(0, 108, 41)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(6, 1, 'INFORME DE EVALUACIÓN DE RIESGOS PROPIEDAD', -2, 1, "C", 1)
        pdf.image(r'Archivos/Logo.jpg', x = 7, y = 0.1, w = 1, h = 1)
        pdf.ln(0.3)
        pdf.set_text_color(0, 0, 0)
    
    def footer():
        pdf.set_y(10.2)
        pdf.set_x(0.73)
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(9,0, str(pdf.page_no()))
        
    def celda_verde(ancho, altura, titulo):
        pdf.set_font('Times','B',12.0)
        pdf.set_fill_color(0, 108, 41)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(ancho, altura, titulo, align="C", border = True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Times','',10.0) 
    
    def celda_roja(ancho, altura, titulo):
        pdf.set_font('Times','B',12.0)
        pdf.set_fill_color(213, 36, 36)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(ancho, altura, titulo, align="C", border = True, fill=True)
        pdf.set_text_color(0, 0, 0)
        
    def imagen_random():
        numeros = [1,2,3]
        numero_aleatorio = random.choice(numeros)   
        if numero_aleatorio == 1:
            path_imagen = 'Archivos/Imagen_Inicio.png'
        elif numero_aleatorio == 2:
            path_imagen = 'Archivos/Imagen_Inicio_2.png'
        else:
            path_imagen = 'Archivos/Imagen_Inicio_3.png'
        return path_imagen   

    pdf=FPDF(format='letter', unit='in')
    pdf.add_page()
    pdf.set_font('Arial','B',15.0) 
    th = pdf.font_size
    ac = 0.25
    epw = pdf.w - 2 * pdf.l_margin
    
    #PAGINA INTRODUCCIÓN
    pdf.set_fill_color(0, 108, 41)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(6, 1, 'INFORME DE EVALUACIÓN DE RIESGOS PROPIEDAD', 0, 1, "C", 1)
    pdf.image(r'Archivos/Logo.jpg', x = 7, y = 0.4, w = 1, h = 1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial','B', 10.0) 
    pdf.set_y(2)
    pdf.cell(9,0, f"NÚMERO DE SOLICITUD: {consecutivo_CIRO}")
    imagen_random()
    path_imagen = imagen_random()
    if path_imagen == 'Archivos/Imagen_Inicio_3.png':
        pdf.image(path_imagen, x = 0.72, y = 2.9, w = 7, h = 4.3)
    else:
        pdf.image(path_imagen, x = 0.72, y = 2.5, w = 7, h = 5)
    pdf.set_fill_color(255, 224, 53)
    pdf.set_y(8.5)
    pdf.set_x(0.73)
    pdf.cell(5, 0.03, '', 0, 1, "C", 1)
    pdf.set_y(8.8)
    pdf.set_x(0.73)
    pdf.cell(9,0, "SEGUROS BOLÍVAR S.A.")
    pdf.set_y(9)
    pdf.set_x(0.73)
    pdf.cell(9,0, "CREADO POR: ")
    pdf.set_y(9)
    pdf.set_x(1.75)
    pdf.set_font('Arial','', 10.0)
    pdf.cell(9,0, "INGENIERO DÍGITAL")
    pdf.set_y(9.2)
    pdf.set_x(0.73)
    pdf.set_font('Arial','B', 10.0) 
    pdf.cell(9,0, f"FECHA DE SOLICITUD: {fecha_actual}")
    footer()
    
    # 1 - INFORMACIÓN PERSONAL
    pdf.add_page()
    header()
    pdf.set_font('Times','B', 14.0)
    pdf.set_text_color(0, 0, 0)
    
    if is_cc == True:
        informacionGeneral = [['Nombre Tomador / Asegurado', "Persona Natural"],
            ['Documento de identidad', "C.C"],
            ['Actividad Económica', "No aplica"],
            ['Valor a asegurar', valor_a_asegurar],
            ['Dirección', direccion],
            ['Ciudad', 'Bogota'], 
            ['Teléfono', "No aplica"],
            ['Número de solicitud', consecutivo_CIRO]]
    else:
        informacionGeneral = [['Nombre Tomador / Asegurado', tomador],
            ['NIT', nit],
            ['Actividad Económica', str(ciiu_numero).replace("'", "")],
            ['Valor a asegurar', valor_a_asegurar],
            ['Dirección', direccion],
            ['Ciudad', 'Bogota'], 
            ['Teléfono', telefono_principal],
            ['Número de solicitud', consecutivo_CIRO]]
        
    pdf.set_fill_color(225, 225, 225)
    pdf.cell(epw, 0.5, '1 - INFORMACIÓN GENERAL', 0, 1, "C", 1)
    pdf.set_fill_color(0, 0, 0)
    pdf.set_font('Times','',10.0) 
    pdf.ln(0.3)


    for row in informacionGeneral:
        for i in row:
            pdf.cell(epw/2, ac, str(i), border=0, align = 'C') 
        pdf.ln(ac)


    pdf.ln(0.2)


    # 2 - ENTORNO
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, '2 - ENTORNO', align='C')
    pdf.ln(0.25) 
    if info_catastro == True:
        pdf.cell(epw, 3.9, '', align='C', border = 1)
        try:
            open(r'Archivos/PNG/ID/' + str(DireccioN[0])  + ".png")
            pdf.image(r'Archivos/PNG/ID/' + str(DireccioN[0])  + ".png", x = 0.4, y = 4.65, w = 4.2, h = 3.7) 
            pdf.image(r'Archivos/Mapas/ID/'+str(DIRECCION)+'ENTORNO.png',x = 4.3, y = 5, w = 3.7, h = 3.2)
        except IOError:
            pass
        pdf.ln(3.7)
        pdf.set_font('Times','I',9.0) 
        pdf.cell(epw, 0.2, "La gráfica representa el polígono (silueta) del predio. Los vectores índican el número de pisos en el predio.")
        pdf.ln()
        celda_verde(epw, ac, 'COORDENADAS') 
        pdf.ln(ac)
        
        coordenadas = [['Localidad', SectoR[0][2]],
        ['UPZ', SectoR[0][0]],
        ['Barrio', SectoR[0][1]],
        ['Latitud', LatloN[0][0]],
        ['Longitud', LatloN[0][1]]]
        for row in coordenadas:
            for i in row:
                pdf.cell(epw/2, ac, str(i), border=1, align = 'C') 
            pdf.ln(ac)
         
        
    else:
        pdf.add_page()
        header()
        pdf.set_font('Times','B',12.0)
        celda_verde(epw, ac, 'COORDENADAS')
        pdf.set_font('Times','',10.0) 
        pdf.ln(ac)
        
        coordenadas = [['Localidad', 'Sin información'],
        ['UPZ', 'Sin información'],
        ['Barrio', 'Sin información'],
        ['Latitud', LATITUD],
        ['Longitud', LONGITUD]]
        
        for row in coordenadas:
            for i in row:
                pdf.cell(epw/2, ac, str(i), border=1, align = 'C') 
            pdf.ln(ac)

        pdf.ln(5) 
        
    footer()
    
    os.remove(r'Archivos/PNG/ID/' + str(DireccioN[0])  + ".png")
    os.remove(r'Archivos/Mapas/ID/'+str(DIRECCION)+'ENTORNO.png')
    
    # MAPA - NEARBY SEARCH
    
    pdf.add_page()
    header()
    
    distancias = []
    img, locales_clasif, coordenadas = nearby_search_maps(LATITUD, LONGITUD)
    
    for coordenada in coordenadas:
        latitud = coordenada[0]
        longitud = coordenada[1]
        
        distancia_m = haversine(LATITUD, LONGITUD, latitud, longitud)
        distancias.append(distancia_m)
    
    datos_ordenados = sorted(zip(locales_clasif, distancias, coordenadas), key=lambda x: x[1])
    
    pdf.set_x((pdf.w/2)-3.5)
    celda_verde(7, ac, 'ESTABLECIMIENTOS EN LA ZONA')
    pdf.ln(ac)
    pdf.image(r"Archivos/mapa.png", x =(pdf.w/2)-3.5, y = 1.6, w = 7, h = 5)
    pdf.set_x((pdf.w/2)-3.5)
    pdf.cell(7, 5, '', align='C', border = 1)
    
    pdf.ln(5.1)
    
    pdf.set_font('Times','B',9.0) 
    pdf.set_fill_color(0, 108, 41)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(epw/3.0, ac, "NOMBRE", align='C', border = 1, fill=True)
    pdf.cell(epw/4.0, ac, "CALIFICACIÓN SEGÚN MAPS", align='C', border = 1, fill=True)
    pdf.cell(epw/4.5, ac, "CALIFICACIÓN INCENDIO", align='C', border = 1, fill=True)
    pdf.cell(1.5, ac, "DISTANCIA AL PREDIO", align='C', border = 1, fill=True)
    pdf.ln(ac)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Times','',9.0)  
    for local, distancia, coordenada in datos_ordenados:
        text_lines = textwrap.wrap(str(local[0]), width=25)
        pdf.cell(epw/3.0, ac, ' '.join(text_lines), align='C', border = 1)
        pdf.cell(epw/4.0, ac, str(local[1]), align='C', border = 1)
        if local[2] == "Bajo":        
            pdf.set_fill_color(0, 255, 0)
        elif local[2] == "Medio - Bajo":        
            pdf.set_fill_color(0, 180, 100)
        elif local[2] == "Medio":        
            pdf.set_fill_color(255, 255, 0)
        elif local[2] == "Medio - Alto":        
            pdf.set_fill_color(255, 128, 0)
        elif local[2] == "Alto":        
            pdf.set_fill_color(255, 0, 0)
        else:
            pdf.set_fill_color(192,192,192)

        pdf.cell(epw/4.5, ac, str(local[2]), align='C', border = 1, fill=True)
        pdf.cell(1.5, ac, str(distancia) + " m", align='C', border = 1)
        pdf.ln() 

    os.remove("Archivos/mapa.png")

    footer()

    # 3 - RIESGOS CATASTROFICOS
    pdf.add_page()
    header()
    pdf.ln(ac)
    pdf.set_font('Times','B',14.0)
    celda_verde(epw, ac, '3 - CUADRO DE AMENAZAS (Visor mapas - Manzaneo)') 
    pdf.ln(ac)
    pdf.cell(epw/2, 2.77, '', align='C', border = 1)
    pdf.cell(epw/2, 2.77, '', align='C', border = 1)
    pdf.image(r'Archivos/PNG/ID/' + str(DireccioN[0])  + "_tabla" + ".png", x =0.5, y = 1.9, w = 3.5, h = 2.7)
    pdf.image(r'Archivos/PNG/ID/' + str(DireccioN[0])  + "_tablaM" + ".png", x =4.5, y = 1.9, w = 3.5, h = 2.7)

    os.remove('Archivos/PNG/ID/' + str(DireccioN[0])  + "_tabla" + ".png")
    os.remove('Archivos/PNG/ID/' + str(DireccioN[0])  + "_tablaM" + ".png")
    
    pdf.ln(2.85)
    pdf.set_font('Times','B',14.0) 
    celda_verde(epw,ac,'4 - CONSTRUCCIÓN')
    pdf.ln(ac)
    pdf.set_font('Times','',10.0) 
    # 4 - CONSTRUCCIÓN
    if info_catastro == True:
        
        numero_pisos = str(numero_pisos)
        numero_semi_sotanos = str(numero_semi_sotanos)
        numero_sotanos = str(numero_sotanos)

        #OBTENER SOLO LOS NUMEROS Y SACAR SOLO LOS QUE SE NECESITAN
        numeroPisos = [int(temp)for temp in numero_pisos.split() if temp.isdigit()]
        numeroPisos = numeroPisos[1::2]

        numeroSemiSotanos = [int(temp)for temp in numero_semi_sotanos.split() if temp.isdigit()]
        numeroSemiSotanos = numeroSemiSotanos[1::2]

        numeroSotanos = [int(temp)for temp in numero_sotanos.split() if temp.isdigit()]
        numeroSotanos = numeroSotanos[1::2]
        npi = 0
        ns = 0 
        nss = 0
        if len(numeroPisos) > 0 :
            npi = max(numeroPisos)
        else:
            npi = "No aplica"
            
        
        if len(numeroSotanos) > 0 :
            ns = max(numeroSotanos)
        else:
            ns = "No aplica"
            

        if len(numeroSemiSotanos) > 0 :
            nss = max(numeroSemiSotanos)
        else:
            nss = "No aplica"
            
        if CatastrO[0][7] is not None:
            tip = CatastrO[0][7]
        else:
            tip = "Comercial"
        print("Este es el tipo = "+tip)
        construccion = [['Tipo de propiedad', tip],
        ['Número de pisos (Mayor)', npi],
        ['Número de sótanos', ns],
        ['Número de semisótanos', nss],
        ['Año de construcción', CatastrO[0][0][2]],
        ['Área del lote', CatastrO[0][0][0] + " m²"],
        ['Área construida', CatastrO[0][0][1] + " m²"],
        ['Área en uso', CatastrO[0][0][3]],
        ['Topografía', CatastrO[0][8]],
        ['Material', CatastrO[0][1]],
        ['Sistema estructural', sis],
        ['Muros', CatastrO[0][2]],
        ['Cubierta', CatastrO[0][3]],
        ['Concepto de la estructura', CatastrO[0][4]],
        ['Fachada', CatastrO[0][5]],
        ['Estado de acabados', CatastrO[0][6]],
        ['Zona de alto riesgo no mitigable', CatastrO[0][10]],
        ['Cerchas', CatastrO[0][9]],
        ['Clase suelo urbano', CatastrO[0][11]],
        ['Acabado de pisos', CatastrO[0][16]],
        ['Cubrimiento de muros', CatastrO[0][15]]]
        
        antiguedad_previa_2010 = False
        año_construccion = int(CatastrO[0][0][2])
        año_referencia = 2010
        
        
        if año_construccion < año_referencia:
            antiguedad_previa_2010 = True
        else:
            antiguedad_previa_2010 = False
        
        print(f"El predio fue construido previo a 2010 {antiguedad_previa_2010}")

        for row in construccion:
            for i in row:
                pdf.cell(epw/2, 0.238, str(i), border=1, align = 'C') 
            pdf.ln(0.238)

        
        footer()

        #CONSTRUCCIÓN EN EL LOTE, PISOS, SEMISOTANOS Y SOTANOS
        pdf.add_page()
        header()
        celda_verde(epw, ac, "CONSTRUCCIÓN EN EL LOTE")
        pdf.set_font('Times','',10.0) 
        pdf.ln()

        tituloPisos = [["Número de pisos"],["Número de semisótanos"],["Número sótanos"]]
        for row in tituloPisos:
            for i in row:
                pdf.cell(epw/3, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)
        for i in numeroPisos:
            pdf.multi_cell(epw/3 , ac, str(i), border = 1, align = 'C')
        pdf.ln()
        y = 5.83
        for i in numeroSemiSotanos:
            pdf.set_xy(epw/3+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/3 , ac, str(i), border = 1, align = 'C')
            y = y+1
        pdf.ln()
        y = 5.83
        for i in numeroSotanos:
            pdf.set_xy((epw/3)*2+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/3 , ac, str(i), border = 1, align = 'C')
            y = y+1

        pdf.ln(ac)

        #APARTADO DE LAS VIAS

        celda_verde(epw, ac, "ESTADO DE LAS VÍAS")      
        pdf.ln(ac)
        pdf.set_font('Times','',10.0) 

        vias = [['Tipo de vías', CatastrO[0][12]],
        ['Estado de las vías', CatastrO[0][13]],
        ['Influencia de las vías', CatastrO[0][14]]]

        for row in vias:
            for i in row:
                pdf.cell(epw/2, ac, str(i), border=1, align = 'C') 
            pdf.ln(ac)
        
        pdf.ln(ac)
        print("Información estructural completa")
    else:
        pdf.set_font('Times','B',14.0) 
        pdf.cell(epw, ac, '4 - CONSTRUCCIÓN', align='C')
        pdf.ln(ac)
        
        pdf.set_font('Times','',10.0) 
        pdf.cell(epw, ac, "No hay información de la construcción del predio en las bases de datos del catastro.", border=1, align = 'C')
        pdf.ln(ac)
        
    # DESCRIPCION ACTIVIDAD ECONOMICA
    try:
        pdf.ln(ac)
        celda_verde(epw, ac, "DESCRIPCIÓN ACTIVIDAD ECONÓMICA") 
        pdf.set_font('Times', '', 10.0)
        if len(ciiu_numero)>0:
            pdf.ln(ac)
            pdf.cell(epw, ac*(len(ciiu_numero)+1), "", border = 1, align='C')
            for i in range(0,len(ciiu_dado)):
                pdf.ln(ac)
                pdf.cell(epw, ac, str(ciiu_numero[i])+ ": " + str(ciiu_dado[i]), border=0, align='C')
        pdf.ln(ac)
    except:
        pass
     
    pdf.ln(ac)
    celda_verde(epw, ac, "RIESGOS POR ACTIVIDAD ECONÓMICA") 
    
    if is_cc == False:

        headers = ["CIIU", "Incendio", "All Risk", "Sustracción","R.M", "E.E", "Manejo", "RC"]

        data = riesgos_politicas[headers].astype(str).values.tolist()
    
        pdf.ln()
        pdf.set_font('Times', 'B', 9.5)
        for header1 in headers:
            pdf.cell(epw / 8, ac, header1, border=1, align='C')
        pdf.ln()

        pdf.set_font('Times', '', 9.5)

        for row in data:
            for item in row:
                if item.lower() == 'nan' or item.lower() == 'sin información':
                    print("No hay información del riesgo para ciiu")
                    item = 'Sin Información'
                    pdf.set_fill_color(192,192,192)
                elif item == '5.0':
                    pdf.set_fill_color(255, 0, 0)
                elif item == '4.0':
                    pdf.set_fill_color(255, 128, 0)
                elif item == '3.0':
                    pdf.set_fill_color(255, 255, 0)
                elif item == '2.0':
                    pdf.set_fill_color(0, 180, 100)
                elif item == '1.0':
                    pdf.set_fill_color(0, 255, 0)
                else:
                    pdf.set_fill_color(255, 255, 255)

                int_item = "{:g}".format(float(item)) if item.lower() != 'sin información' else item
                pdf.cell(epw / 8, ac, str(int_item), border=1, align='C', fill=True)

            pdf.ln()
        if IsAseg == False and IsAlerta == False:
            riesgosAE = f"El predio posee altos niveles de riesgo asociados con el desarrollo de su actividad económica principal ({ciiu_numero[0]})"
            var = 1
            text_lines = textwrap.wrap(riesgosAE, width=140)
            var = len(text_lines)
            pdf.cell(epw, ac*var, '', align='C', border=1)
            pdf.ln(ac/8)
            for line in text_lines:
                pdf.cell(epw, ac, line, border=0, align='L')
                pdf.ln(ac)
        elif IsAseg == False and IsAlerta == True:
            riesgosAE = f"El predio posee altos niveles de riesgo asociados con el desarrollo de su actividad económica principal ({ciiu_numero[0]}) y de sus actividades económicas secundarias."
            var = 1
            text_lines = textwrap.wrap(riesgosAE, width=140)
            var = len(text_lines)
            pdf.cell(epw, ac*var, '', align='C', border=1)
            pdf.ln(ac/8)
            for line in text_lines:
                pdf.cell(epw, ac, line, border=0, align='L')
                pdf.ln(ac)
        else:
            riesgosAE = f"El predio cumple con las políticas de asegurabilidad de la compañía."
            var = 1
            text_lines = textwrap.wrap(riesgosAE, width=127)
            var = len(text_lines)
            pdf.cell(epw, ac*var, '', align='C', border=1)
            pdf.ln(ac/8)
            for line in text_lines:
                pdf.cell(epw, ac, line, border=0, align='L')
                pdf.ln(ac)
        
        footer()
        
    else:
        headers = ["CIIU", "Incendio", "All Risk", "Sustracción","R.M", "E.E", "Manejo", "RC"]
        
        pdf.set_font('Times', 'B', 9.5)  
        pdf.ln()
        for header1 in headers:
            pdf.cell(epw / 8, ac, header1, border=1, align='C')
        pdf.ln() 
        data = [["No aplica",3,3,3,3,3,3,3]]
        for row in data:
            for i, cell in enumerate(row):
                pdf.set_fill_color(255, 255, 0)
                pdf.cell(epw / 8, ac, str(cell), border=1, align = "C", fill=True)
            pdf.ln()
    
    
    pdf.add_page()
    header()
    pdf.set_font('Times','B',14.0) 
    celda_verde(epw, ac, "REPORTE EMIS") 
    pdf.set_font('Times','',10.0)    
    #EMIS
    if is_cc == False:
        locale.setlocale( locale.LC_ALL, '' )
        if len(emis != 0):
            empleados = int(emis['num_empleados'].values[0])
            ingresos = float(emis['ingresos_totales_ult_ano_usd'].values[0])
            print(emis)

            vEmis = [['Fecha de Actualización', str(emis['fecha_actualizacion'].values[0]).replace("00:00:00 UTC", " ")],
            ['Estatus de la compañía', emis['estatus'].values[0]],
            ['Número de empleados', emis['num_empleados'].values[0]],
            ['Tipo de compañía', emis['tipo_compania'].values[0]],
            ['Ingresos totales del último año (USD)', emis['ingresos_totales_ult_ano_usd'].values[0]],
            ['Moneda capital del mercado', emis['moneda_capital_mercado'].values[0]],
            ['Año de ingresos totales', emis['ano_ingresos_totales'].values[0]]]
            
            for row in vEmis:
                pdf.ln(ac)
                for i in row:
                    pdf.cell(epw/2, ac, str(i), border=1, align = 'C') 
            pdf.ln()
            celda_verde(epw, ac, "DESCRIPCIÓN SEGÚN EMIS")
            pdf.set_font('Times','',10.0) 
            pdf.ln(ac)
            var = 1
            if len(emis['descripcion'].values[0]) > 120:
                var = round(len(emis['descripcion'].values[0]) / 120) + 1
                pdf.cell(epw, ac*var , '', align='C', border = 1)
                pdf.ln(ac/8)
                a = 0
                b = 120
                for i in range(var):
                    text = emis['descripcion'].values[0][a:b]
                    a = a + 120
                    b = b + 120
                    text_encoded = text.encode('latin-1', 'replace').decode('latin-1')  # Codificar en Latin-1
                    pdf.cell(epw, ac, text_encoded, border=0, align='C')
                    pdf.ln(ac)
                pdf.ln(ac)
        else:
            empleados = None
            ingresos = None
            pdf.ln(ac)
            pdf.cell(epw, ac, "SIN INFORMACIÓN", border=1, align = 'C')
            pdf.ln(ac)



        def reemplazar(cadena, dic):
            for k,v in dic.items():
                cadena=cadena.replace(k, v)
            return cadena
        
        pdf.ln()
        
        #ACTIVIDAD SEGUN CATASTRO
        if info_catastro == True:
            pdf.set_font('Times','B',12.0) 
            celda_verde(epw, ac, "DESCRIPCIÓN SEGÚN CATASTRO")
            pdf.set_font('Times','',10.0) 
            pdf.ln(ac)
            dUso = []
            var =1  
            
            PrecusO = ["Sin información" if x is None else x for x in PrecusO]
            
            print(PrecusO)
            
            if PrecusO[0] is not None:
                for i in range(len(PrecusO)):
                    a = 0
                    b = 120
                    if len(PrecusO[i]) > 120:
                        var = round(len(PrecusO[i]) / 120) + 1
                        pdf.cell(epw, ac*var , '', align='C', border = 1)
                        pdf.ln(0.0001)
                        dUso.append(reemplazar(PrecusO[i],{"Etiqueta: " : "", "\n" :"", "  " : "", "Definición: " : "= "}))
                    for j in range(var):
                        try:
                            text = dUso[i][a:b]
                            a = a + 120
                            b = b + 120
                            text_encoded = text.encode('latin-1', 'replace').decode('latin-1')  # Codificar en Latin-1
                            pdf.cell(epw, ac, text_encoded, border=0, align='C')
                            pdf.ln(ac)
                        except:
                            pass
            else:
                PrecusO[0] = "Sin información"
                
                pdf.ln(ac-ac/8)
                pdf.cell(epw, ac, "SIN INFORMACIÓN", border=1, align='C')
        else:
            pdf.ln()
            pdf.set_font('Times','B',12.0) 
            pdf.cell(epw, ac, "DESCRIPCIÓN SEGÚN CATASTRO", border=1, align = 'C') 
            pdf.set_font('Times','',10.0) 
            pdf.ln(ac)
            pdf.cell(epw, ac, "SIN INFORMACIÓN", border=1, align = 'C') 
    else:
        pass
    
    footer()

    #PUNTOS IMPORTANTES
    pdf.add_page()
    header()
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, "5 - PUNTOS DE INTERES", border=0, align = 'C') 
    pdf.ln(ac*2)
    celda_verde(epw/2, ac, "BOMBEROS") 
    pdf.ln(ac)
    pdf.set_font('Times','',10.0)

    if len(ValoreS) > 0:
        distHidrante = int(round(ValoreS[0][0], 2))
        distBomberos = int(round(ValoreS[0][6], 2))

        bomberos = [['Estación más cercana', ValoreS[0][4]],
        ['Dirección de la estación',ValoreS[0][7]],
        ['Distancia a hidrante en m', round(ValoreS[0][0], 2)],
        ['Distancia a estación en m ', round(ValoreS[0][6], 2)],
        ['Número de contacto', ValoreS[0][8]]]

        for row in bomberos:
            for i in row:
                pdf.cell(epw/4, ac, str(i), border=1, align = 'C') 
            pdf.ln(ac)
    else:
        contador_sin += 5
        distHidrante = None
        distBomberos = None

        bomberos = [['Estación más cercana', 'Sin información'],
        ['Dirección de la estación', 'Sin información'],
        ['Distancia a hidrante en m', 'Sin información'],
        ['Distancia a estación en m ', 'Sin información'],
        ['Número de contacto', 'Sin información']]
        
        for row in bomberos:
            for i in row:
                pdf.cell(epw/4, ac, str(i), border=1, align = 'C')
            pdf.ln(ac) 

    pdf.ln(ac)
    celda_verde(epw/2, ac, "POLICÍA") 
    pdf.ln(ac)
    pdf.set_font('Times','',10.0)  

    if len(ValoreS) > 0:
        distCai = int(round(ValoreS[0][9], 2))
        distPolicia = int(round(ValoreS[0][15], 2))

        poli = [['CAI más cercano', ValoreS[0][10]],
        ['Dirección', ValoreS[0][12]],
        ['Distancia en m', round(ValoreS[0][9], 2)],
        ['Tipo de atención', ValoreS[0][11]],
        ['Número de contacto ', ValoreS[0][13]],
        ['Estación más cercana', ValoreS[0][16]],
        ['Dirección de estación', ValoreS[0][17]],
        ['Distancia en m', round(ValoreS[0][15], 2) ],
        ['Número de Contacto', ValoreS[0][18]]]

        for row in poli:
            for i in row:
                pdf.cell(epw/4, ac, str(i), border=1, align = 'C') 
            pdf.ln(ac)
    
    else:
        contador_sin += 9
        distCai = None
        distPolicia = None

        poli = [['CAI más cercano', 'Sin información'],
        ['Dirección', 'Sin información'],
        ['Distancia en m', 'Sin información'],
        ['Tipo de atención', 'Sin información'],
        ['Número de contacto ', 'Sin información'],
        ['Estación más cercana', 'Sin información'],
        ['Dirección de estación', 'Sin información'],
        ['Distancia en m', 'Sin información' ],
        ['Número de Contacto', 'Sin información']]

        for row in poli:
            for i in row:
                pdf.cell(epw/4, ac, str(i), border=1, align = 'C')
            pdf.ln(ac) 
            
    
    
    # try:
    #     if contador_sin >= 10:
    #         return HTTPException(status_code=104, detail="Se encontraron muchos items sin información")
    # except HTTPException as e:
    #     raise e
    
    pdf.ln(ac)
    pdf.image(r'Archivos/Policia.jpeg', x = epw/1.35, y = 3.64375 +ac*2 , w = ac*6, h = ac*6)
    pdf.image(r'Archivos/Bomberos.jpeg', x = epw/1.35, y = 1.89375 , w = ac*6, h = ac*6)
    
    #SINIESTROS
    
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, "6 - SINIESTROS", border=0, align = 'C') 
    pdf.ln(ac*2)
    
    if incurrido.empty:
        celda_verde(epw, ac, "NO HA PRESENTADO SINIESTROS")
        pdf.ln(ac)
        pdf.set_font('Times','B',10.0) 
        pdf.cell(epw, ac, "Usuario " +vigencia+ " dentro de la compañia." , border=1, align = 'C')
        pdf.ln(ac)
    else:
        celda_verde(epw, ac, "HISTÓRICO DE SINIESTROS") 
        pdf.set_font('Times','',8.0) 
        pdf.ln(ac)
        pdf.set_font('Times','B',10.0) 
        pdf.cell(epw/4, ac, "NOMBRE COBERTURA", align='C', border = 1)
        pdf.cell(epw/4, ac, "CÓDIGO PRODUCTO", align='C', border = 1)
        pdf.cell(epw/4, ac, "CÓDIGO COBERTURA", align='C', border = 1)
        pdf.cell(epw/4, ac, "# SINIESTROS HISTÓRICOS", align='C', border = 1)
        pdf.ln(ac)
        pdf.set_font('Times','',10.0)
        row_count = 0
        codigo_por_cobertura = {}
        for i, row in incurrido.iterrows():
            nombre_cobertura = row["NOMBRE_COBERTURA"]
            codigo_producto = row["CODIGO_PRODUCTO"]
            codigo_cobertura = row["CODIGO_COBERTURA"]
            
            if nombre_cobertura not in codigo_por_cobertura:
                codigo_por_cobertura[nombre_cobertura] = {
                    "codigo_producto": codigo_producto,
                    "codigo_cobertura": codigo_cobertura,
                    "cantidad": 1
                }
            else:
                codigo_por_cobertura[nombre_cobertura]["cantidad"] += 1
        for i, (nombre, info) in enumerate(codigo_por_cobertura.items()):
            pdf.cell(epw/4, ac, str(nombre), align='C', border=1)
            pdf.cell(epw/4, ac, str(info["codigo_producto"]), align='C', border=1)
            pdf.cell(epw/4, ac, str(info["codigo_cobertura"]), align='C', border=1)
            pdf.cell(epw/4, ac, str(info["cantidad"]), align='C', border=1)
            pdf.ln()
            row_count += 1
            
        pdf.set_font('Times','B',10.0)
        pdf.cell(epw, ac, "LA FECHA DEL ÚLTIMO SINIESTRO FUE EL "+ str(incurrido_ordenado.iloc[-1]["FECHA_SINIESTRO"]), border=1, align='C')
        pdf.ln(ac) 
        
        pdf.ln()
        pdf.set_font('Times','B',12.0) 
        pdf.ln()
        celda_verde(epw, ac, "RESUMEN DE INCURRIDOS POR AÑO")
        pdf.set_font('Times','B',10.0) 
        pdf.ln(ac)
        pdf.cell(epw/3, ac, "AÑO SINIESTRO", align='C', border=1)
        pdf.cell(epw/3, ac, "NÚMERO DE SINIESTROS", align='C', border=1)
        pdf.cell(epw/3, ac, "INCURRIDO", align='C', border=1)
        pdf.ln()

        pdf.set_font('Times','',10.0) 

        resumen_por_año = incurrido.groupby(["CODIGO_PRODUCTO", "AÑO"]).agg({"NUMERO_SINIESTRO": "count", "INCURRIDO": "sum"}).reset_index()

        for i, row in resumen_por_año.iterrows():
            pdf.cell(epw/3, ac, str(row["AÑO"]), align='C', border=1)
            pdf.cell(epw/3, ac, str(row["NUMERO_SINIESTRO"]), align='C', border=1)
            pdf.cell(epw/3, ac, "{:,.2f}".format(row["INCURRIDO"]), align='C', border=1)
            pdf.ln()
        
        pdf.set_font('Times','B',10.0) 
        pdf.cell(epw, ac, "EL TOTAL EN INCURRIDOS ES "+ str(total_incurrido_formateado) +" pesos", border=1, align = 'C')
        pdf.ln()
        
        pdf.cell(epw, ac, "EL PROMEDIO ANUAL EN INCURRIDOS ES "+ str(promedio_incurrido_formateado) +" pesos", border=1, align = 'C')
        pdf.ln()
                    
    if anti == True:
        pdf.ln()
        pdf.set_font('Times','B',10.0) 
        pdf.cell(epw, ac, "La primera vinculación de este cliente se genero el " + antiguedad, border=1, align = 'C')
        pdf.ln(ac)
    else:
        pdf.set_font('Times','B',10.0) 
        pdf.cell(epw, ac, "SE TRATA DE UN CLIENTE NUEVO DENTRO DE LA COMPAÑIA ", border=1, align = 'C')
        pdf.ln(ac) 
        
    footer()
    
    #ANALISIS DE RIESGO 
    pdf.add_page()
    header()
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, "7 - ANÁLISIS DE RIESGO", border=0, align = 'C') 
    pdf.ln(ac*2)
    pdf.set_font('Times','B',12.0)
    if ConceptoManzaneo[0] == "N":
        celda_verde(epw, ac, "CONCEPTO DE MANZANEO") 
    else:
        celda_roja(epw, ac, "CONCEPTO DE MANZANEO")
    pdf.ln(ac)
    pdf.set_font('Times','',10.0) 
    if ConceptoManzaneo[0] == "N":
        pdf.cell(epw, ac, "Concepto Favorable", border=1, align = 'C') 
    elif ConceptoManzaneo[0] == "S":
        pdf.cell(epw, ac, "Concepto desfavorable", border=1, align = 'C') 
    else:
        pdf.cell(epw, ac, "Sin información", border=1, align = 'C') 
    pdf.ln(ac*2)
    
    tituloSire = [["#"],["FECHA DE REPORTE"],["TIPO DE AFECTACIÓN"]]
    pdf.set_font('Times','B',12.0) 
    celda_verde(epw, ac, "REGISTROS SIRE")
    pdf.set_font('Times','',10.0) 
    pdf.ln(ac)
        
    if len(sire) > 0:
        for row in tituloSire:
            for i in row:
                pdf.set_font('Times','B',10.0) 
                pdf.cell(epw/3, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)
    
        for i in range (len(sire)):
            pdf.multi_cell(epw/3 , ac, str(i), border = 1, align = 'C')

        y = 10.82
        for i in sire['Fecha reporte']:
            pdf.set_font('Times', '',10.0) 
            pdf.set_xy((epw/3)+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/3 , ac, str(i), border = 1, align = 'C')
            y = y+1

        y = 10.82
        for i in sire['Tipo de afectación']:
            pdf.set_xy((epw/3)*2+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/3 , ac, str(i), border = 1, align = 'C')
            y = y+1
    else:
        pdf.cell(epw, ac, "NO EXISTE REGISTRO EN SIRE", border=1, align = 'C')
        pdf.ln(ac)
    print("Información interna completa")
    
    footer()
    
    #MODELO DE RIESGO TERREMOTO
    pdf.add_page()
    header()
    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(epw, ac, "8 - MODELOS DE RIESGO", border=0, align='C')
    pdf.ln(ac*2)
    celda_verde(epw/2, ac, "TERREMOTO")
    pdf.ln(ac)
    pdf.set_font('Times', '', 10.0)


    if type(riesgoSismo) is not str:
        rTerre = [['Porcentaje de daño esperado', "{:.2f}".format(riesgoSismo)],
        ['Nivel de riesgo', escala],
        ['Concepto', concepto]]
    else:
        rTerre = [['Porcentaje de daño esperado', riesgoSismo],
        ['Nivel de riesgo', escala],
        ['Concepto', concepto]]

    x = pdf.get_x()
    for row in rTerre:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align='C')
        pdf.ln(ac)
    if concepto == "Asegurable":
        pdf.image(r'Archivos/Check.png', x = 5, y = 1.8, w = 1, h = 1)
    if concepto == "No asegurable":
        pdf.image(r'Archivos/Error.png', x = 5, y = 1.8, w = 1, h = 1)

    pdf.ln(ac)
    pdf.set_font('Times', 'B', 12.0)
    if concepto == "Asegurable":
        celda_verde(epw, ac, "Justificación Terremoto")
    else:
        celda_roja(epw, ac, "Justificación Terremoto")
    pdf.ln(ac)
    pdf.set_font('Times', '', 10.0)
    try:
        justificacion_positiva_terre = str("Se trata de un predio con una altura máxima de "+str(npi)+" pisos, una edad de construcción de "+str(2022- int(CatastrO[0][0][2]))+ " años y un sistema estructural de " + str(CatastrO[0][1])+ " " +sis + ". Dadas esas características la propiedad tiene una probabilidad "+ str(escala)+ " de tener afectaciones considerables ante eventos sísmicos. Adicionalmente, en la zona se estima una posibilidad " +str(MatrizAmenazas[0]) + " de presentar eventos catastróficos. Teniendo en cuenta lo anterior, el nivel de riesgo es aceptable, por lo tanto, la empresa se considera ASEGURABLE.")
        
        justificacion_negativa_terre = str("Se trata de un predio con una altura máxima de "+str(npi)+", una edad de construcción de "+str(2022- int(CatastrO[0][0][2]))+ " años y un sistema estructural de " + str(CatastrO[0][1])+ " " +sis
        + ". Dadas esas características, la propiedad tiene una probabilidad "+ str(escala)+ " de tener afectaciones considerables ante eventos sísmicos. Adicionalmente, en la zona se estima una posibilidad "
        +str(terremoto_riesgo) + " de que se presenten eventos catastróficos. Teniendo en cuenta lo anterior, el nivel de riesgo NO es aceptable, por lo tanto, la empresa se considera NO ASEGURABLE.")
        
        '''
        
        justificacion_positiva = str("Se trata de una propiedad dedicada al "+ tip+ " cuya sede objetivo de la presente evaluación se encuentra ubicada en el barrio "+ cat.SectoR[0][1]+ " de la localidad "+ cat.SectoR[0][2]+ ", dicho predio tiene una altura maxima de "+ str(npi) 
        +" pisos, con una edad de construcción de "+ str(2021 - int(cat.CatastrO[0][0][2]))
        +" años, cuenta ademas con un sistema estructural en "+ cat.CatastrO[0][1]+ " " +terremoto.sis+ ". "+ terremoto.norma+ ". Teniendo en cuenta que en el sector de la ubicacion se registra una amenza para terremeto " +amenaza.MatrizAmenazas[0]
        +", ademas las otras variables de amenaza no presentan altos niveles. Asimismo por medio de la simulacion de escenarios catastroficos se determino que el riesgo de daño seria de un "+ str(terremoto.riesgoSismo)+"% aproximadamente. Se considera que la propiedad es "+terremoto.concepto)
        justificacion_negativa = str("Se trata de una propiedad dedicada al "+ tip+ " cuya sede objetivo de la presente evaluación se encuentra ubicada en el barrio " 
        + cat.SectoR[0][1]+ " de la localidad "+ cat.SectoR[0][2]+ ", dicho predio tiene una altura maxima de "+ str(npi) 
        +" pisos, con una edad de construcción de "+ str(2021 - int(cat.CatastrO[0][0][2]))
        +" años, cuenta ademas con un sistema estructural en "+ (cat.CatastrO[0][1])+ " " +(terremoto.sis)+ ". "+ terremoto.norma+ ". Teniendo en cuenta que en el sector de la ubicacion se registra una amenza para terremeto " +amenaza.MatrizAmenazas[0]
        +", para remocion " + amenaza.MatrizAmenazas[2]+ " e inundación "+ amenaza.MatrizAmenazas[6]+". Asimismo por medio de la simulacion de escenarios catastroficos se determino que el riesgo de daño seria de un "+ str(terremoto.riesgoSismo)+"% aproximadamente. Se considera que la propiedad es NO ASEGURABLE")
        '''
        
        if concepto == "Asegurable":
            var = 1
            text_lines = textwrap.wrap(justificacion_positiva_terre, width=127)
            var = len(text_lines)
            pdf.cell(epw, ac*var, '', align='C', border=1)
            pdf.ln(ac/8)
            for line in text_lines:
                pdf.cell(epw, ac, line, border=0, align='L')
                pdf.ln(ac)
        else: 
            var = 1
            text_lines = textwrap.wrap(justificacion_negativa_terre, width=127)
            var = len(text_lines)
            pdf.cell(epw, ac*var, '', align='C', border=1)
            pdf.ln(ac/8)
            for line in text_lines:
                pdf.cell(epw, ac, line, border=0, align='L')
                pdf.ln(ac)
    except: 
        justificación_sin_info = ("Por falta de información no es posible generar un concepto de asegurabilidad completo para esta propiedad")
        pdf.cell(epw, ac, justificación_sin_info, border=1, align='C')
    pdf.ln(ac)

    print("Modelo de terremoto completo")

    #MODELO DE RIESGO SUSTRACCION 
    celda_verde(epw/2, ac, "SUSTRACCIÓN")
    pdf.ln(ac)
    rSustra= [['Probabilidad de robo', proRobo],
    ['Calificación del entorno', ento],
    ['Concepto', conceptoSus]]

    x = pdf.get_x()
    for row in rSustra:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align='C')
        pdf.ln(ac)
    if conceptoSus == "Asegurable":
        pdf.image(r'Archivos/Check.png', x = 5, y = 4.8, w = 1, h = 1)
    if conceptoSus == "No asegurable":
        pdf.image(r'Archivos/Error.png', x = 5, y = 4.8, w = 1, h = 1)

    pdf.ln(ac)
    pdf.set_font('Times', 'B', 12.0)
    if conceptoSus == "Asegurable":
        celda_verde(epw, ac, "Justificación Sustracción")
    else:
        celda_roja(epw, ac, "Justificación Sustracción")
    pdf.ln(ac)
    pdf.set_font('Times', '', 10.0)
    try:
        justificacion_positiva_sustra = str("El predio se encuentra en una zona con una probabilidad estimada de hurto "+ str(proRobo)+ ". Adicionalmente, se analizó el entorno y sus posibles afectaciones, generando como resultado una apreciación "
        +str(apre)+", teniendo en cuenta la distancia que se presenta entre la propiedad y aquellos puntos de interés* que inciden en la frecuencia de siniestralidad para sustracción. Teniendo en cuenta lo anterior, el nivel de riesgo es "
        +str(riesgoSus)+", por lo tanto, la empresa se considera ASEGURABLE.")

        justificacion_negativa_sustra = str("El predio se encuentra en una zona con una probabilidad estimada de hurto "+ str(proRobo)+ ". Adicionalmente se analizó el entorno y sus posibles afectaciones, generando como resultado una apreciación "
        +str(apre)+", teniendo en cuenta la distancia que se presenta entre la propiedad y aquellos puntos de interés* que inciden en la frecuencia de siniestralidad para sustracción.  Teniendo en cuenta lo anterior, el nivel de riesgo es "
        +str(riesgoSus)+", por lo tanto la empresa se considera NO ASEGURABLE")
        
        justificacion_ZI_sustra = str("El predio se encuentra en una zona atribuible como zona de interés ya que se encuentra dentro de un " 
        + str(ValoreS[0][34]) + ", específicamente al " + str(ValoreS[0][35]) + ", por esto el predio está amparado por los protocolos de seguridad del " + str(ValoreS[0][34]) + ", por lo tanto la empresa se considera ASEGURABLE")

        if conceptoSus == "No asegurable" and FueraSus == True:
            var = 1
            text_lines = textwrap.wrap("El predio no es asegurable, ya que la actividad económica principal tiene calificación 5 en la amenaza de sustracción según las políticas de la compañía.", width=127)
            var = len(text_lines)
            pdf.cell(epw, ac*var, '', align='C', border=1)
            pdf.ln(ac/8)
            for line in text_lines:
                pdf.cell(epw, ac, line, border=0, align='L')
                pdf.ln(ac)
        if conceptoSus == "No asegurable" and FueraSus == False: 
            var = 1
            text_lines = textwrap.wrap(justificacion_negativa_sustra, width=127)
            var = len(text_lines)
            pdf.cell(epw, ac*var, '', align='C', border=1)
            pdf.ln(ac/8)
            for line in text_lines:
                pdf.cell(epw, ac, line, border=0, align='L')
                pdf.ln(ac)
        if conceptoSus == "Asegurable" and ValoreS[0][34] is not None and FueraSus == False:
            var = 1
            text_lines = textwrap.wrap(justificacion_ZI_sustra, width=127)
            var = len(text_lines)
            pdf.cell(epw, ac*var, '', align='C', border=1)
            pdf.ln(ac/8)
            for line in text_lines:
                pdf.cell(epw, ac, line, border=0, align='L')
                pdf.ln(ac)
        elif conceptoSus == "Asegurable" and FueraSus == False:
            var = 1
            text_lines = textwrap.wrap(justificacion_positiva_sustra, width=127)
            var = len(text_lines)
            pdf.cell(epw, ac*var, '', align='C', border=1)
            pdf.ln(ac/8)
            for line in text_lines:
                pdf.cell(epw, ac, line, border=0, align='L')
                pdf.ln(ac)
    except: 
        justificación_sin_info = ("Por falta de información no es posible generar un concepto de asegurabilidad completo para esta propiedad")
        pdf.cell(epw, ac, justificación_sin_info, border=1, align='C')
    
    print("Modelo de sustracción completo")   
    
    if concepto == "Asegurable":
        #GARANTIAS
        garantia = ("DURANTE LA VIGENCIA DE LA PÓLIZA, EL ASEGURADO DEBE MANTENER INSTALADO Y ACTIVO, UN SISTEMA DE ALARMA QUE PROTEJA LAS INSTALACIONES Y POSIBLES ACCESOS CON SENSORES DE MOVIMIENTO, SENSORES MAGNÉTICOS DE APERTURA, SENSORES DE PÁNICO INALAMBRICOS Y/O FIJOS. EL SISTEMA DEBE ESTAR MONITOREADO VÍA RADIO, GPRS Y/O CELULAR CON EMPRESA ESPECIALIZADA INSCRITA EN LA SUPERINTENDENCIA DE VIGILANCIA; LA CUAL CUENTE CON SERVICIO DE REACCIÓN. LA ALARMA DEBE CONTAR CON UNA BATERÍA DE RESERVA QUE SOPORTE EL SISTEMA COMO MÍNIMO CUATRO (4) HORAS. ")
        try:
            if a[3] >= 2:
                print("ENTRO")
                pdf.set_font('Times', 'B', 14.0)
                pdf.cell(epw, ac, "9 - GARANTIAS", border=0, align='C')
                pdf.ln(ac*2)
                pdf.set_font('Times', '', 8.0)
                var = 1

                if len(garantia) > 120:
                    var = round(len(garantia) / 120) + 1
                pdf.cell(epw, ac*var, '', align='C', border=1)
                pdf.ln(ac/8)
                a = 0
                b = 120
                for i in range(var):
                    text = garantia[a:b]
                    a = a + 120
                    b = b + 120
                    pdf.cell(epw, ac, text, border=0, align='C')
                    pdf.ln(ac)
                pdf.ln(ac)
        except:
            pass

    pdf.ln(ac)
    footer()
    
    #MODELO DE RIESGO INCENDIO 
    pdf.add_page()
    header()
    celda_verde(epw/2, ac, "INCENDIO")
    pdf.ln(ac)
    rIncendio= [['Amenaza del sector', g_amen_pre_inc],
    ['Calificación Politicas', f'Riesgo Tipo {politicas_incendio}'],
    ['Riesgo Incendio Total', nivelIncendio],
    ['Concepto',conceptoIncendio]]

    x = pdf.get_x()
    for row in rIncendio:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align='C')
        pdf.ln(ac)
    if conceptoIncendio == "Asegurable":
        pdf.image(r'Archivos/Check.png', x = 5, y = 1.4, w = 1, h = 1)
    if conceptoIncendio == "No asegurable":
        pdf.image(r'Archivos/Error.png', x = 5, y = 1.4, w = 1, h = 1)

    pdf.ln(ac)
    pdf.set_font('Times', 'B', 12.0)
    if conceptoIncendio == "Asegurable":
        celda_verde(epw, ac, "Justificación Incendio")
    else:
        celda_roja(epw, ac, "Justificación Incendio")
    pdf.ln(ac)
    pdf.set_font('Times', '', 10.0)
    
    if len(ciiu_dado) > 0:
        justificacion_positiva_incendio = str("El predio se encuentra ubicado en una zona con amenaza "+ str(g_amen_pre_inc)+ " para incendio, teniendo en cuenta los reportes generados por el cuerpo de bomberos. La empresa "
        +str(tomador)+" tiene como actividad económica principal " +str(ciiu_dado[0])+ ", la cual se considera como "
        +str(politicas_incendio)+ " de acuerdo con las políticas de Ingeniería. Adicional a esto se evaluaron temas como distancia a estación de bomberos, presencia de hidrantes cercanos, redes eléctricas, entre otras. Teniendo todo esto en cuenta se considera un riesgo "+(str(nivelIncendio))+ ", por lo que se considera ASEGURABLE")

        
        justificacion_negativa_incendio = str("El predio se encuentra ubicado en una zona con amenaza "+ str(g_amen_pre_inc)+ " para incendio, teniendo en cuenta los reportes generados por el cuerpo de bomberos. La empresa "
        +str(tomador)+" tiene como actividad económica principal " +str(ciiu_dado[0])+ ", la cual se considera como "
        +str(politicas_incendio)+ " de acuerdo con las políticas de Ingeniería. Adicional a esto se evaluaron temas como distancia a estación de bomberos, presencia de hidrantes cercanos, redes eléctricas, entre otras. Teniendo todo esto en cuenta se considera un riesgo "+(str(nivelIncendio))+ ", por lo que se considera NO ASEGURABLE")
    else:
        justificacion_positiva_incendio = str("El predio se encuentra ubicado en una zona con amenaza "+ str(g_amen_pre_inc)+ " para incendio, teniendo en cuenta los reportes generados por el cuerpo de bomberos. Adicional a esto se evaluaron temas como distancia a estación de bomberos, presencia de hidrantes cercanos, redes eléctricas, entre otras. Teniendo todo esto en cuenta se considera un riesgo "+(str(nivelIncendio))+ ", por lo que se considera ASEGURABLE")
        justificacion_negativa_incendio = str("El predio se encuentra ubicado en una zona con amenaza "+ str(g_amen_pre_inc)+ " para incendio, teniendo en cuenta los reportes generados por el cuerpo de bomberos. Adicional a esto se evaluaron temas como distancia a estación de bomberos, presencia de hidrantes cercanos, redes eléctricas, entre otras. Teniendo todo esto en cuenta se considera un riesgo "+(str(nivelIncendio))+ ", por lo que se considera NO ASEGURABLE")

    
    if conceptoIncendio == "Asegurable":
        var = 1
        text_lines = textwrap.wrap(justificacion_positiva_incendio, width=127)
        var = len(text_lines)
        pdf.cell(epw, ac*var, '', align='C', border=1)
        pdf.ln(ac/8)
        for line in text_lines:
            pdf.cell(epw, ac, line, border=0, align='L')
            pdf.ln(ac)
    else: 
        var = 1
        text_lines = textwrap.wrap(justificacion_negativa_incendio, width=127)
        var = len(text_lines)
        pdf.cell(epw, ac*var, '', align='C', border=1)
        pdf.ln(ac/8)
        for line in text_lines:
            pdf.cell(epw, ac, line, border=0, align='L')
            pdf.ln(ac)
            
    print("Modelo de INCENDIO completo")

    ##MODELO DXAEN#
    pdf.ln(ac)
    celda_verde(epw/2, ac, "DAÑOS POR AGUA EV. DE LA NATURALEZA")
    pdf.ln(ac)
    rDXAEN= [['Nivel de riesgo', nivelDXAEN],
    ['Concepto', conceptoDXAEN]] 
    print (conceptoDXAEN)
    x = pdf.get_x()
    for row in rDXAEN:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align='C')
        pdf.ln(ac)
        
    if conceptoDXAEN == "Asegurable":
        pdf.image(r'Archivos/Check.png', x = 5, y = 4.5, w = 1, h = 1)
    if conceptoDXAEN == "No Asegurable":
        pdf.image(r'Archivos/Error.png', x = 5, y = 4.5, w = 1, h = 1)

    pdf.ln(ac)
    pdf.set_font('Times', 'B', 12.0)
    if conceptoDXAEN == "Asegurable":
        celda_verde(epw, ac, "Justificación Daños por Agua Ev. Naturaleza")
    else:
        celda_roja(epw, ac, "Justificación Daños por Agua Ev. Naturaleza")
    pdf.ln(ac)
    pdf.set_font('Times', '', 10.0)
    if info_catastro == True:
        justificacion_positiva_DXAEN = ("El predio se considera asegurable en términos de daños por agua evento de la naturaleza debido a la combinación de una cubierta " +str(CatastrO[0][3])+ ", construido en " +str(RCON)+ ", nivel de riesgo de precipitación " +str(nivel_riesgo_estacion)+ " y una amenaza de encharcamiento " +str(AmenazaEncharcamiento)+ ". Estos factores reducen el riesgo de daños por agua eventos de la naturaleza, ubicando el predio en un nivel de riesgo de " +str(nivelDXAEN)+ " que considera el predio ASEGURABLE.")
        justificacion_Negativa_DXAEN = ("El predio se considera no asegurable en términos de daños por agua eventos de la naturaleza debido a una combinación de factores desfavorables. La cubierta existente no es adecuada para prevenir filtraciones de agua " +str(CatastrO[0][3])+ ", el año de construcción es antiguo (" +str(RCON)+ "), los niveles de precipitaciones son altos y existe una alta amenaza de encharcamiento " +str(AmenazaEncharcamiento)+ ". Estos factores aumentan significativamente el riesgo de daños por agua " +str(nivelDXAEN)+ ", lo que hace que el predio NO SEA ASEGURABLE en estas condiciones.")
    else:
        justificacion_positiva_DXAEN = ("El predio posee un nivel de riesgo de precipitación " +str(nivel_riesgo_estacion)+ " y una amenaza de encharcamiento " +str(AmenazaEncharcamiento)+ ". Estos factores reducen el riesgo de daños por agua eventos de la naturaleza, ubicando el predio en un nivel de riesgo de " +str(nivelDXAEN)+ " que considera el predio ASEGURABLE.")
        justificacion_Negativa_DXAEN = ("El predio posee niveles de precipitaciones altos y existe una alta amenaza de encharcamiento " +str(AmenazaEncharcamiento)+ ". Estos factores aumentan significativamente el riesgo de daños por agua " +str(nivelDXAEN)+ ", lo que hace que el predio NO SEA ASEGURABLE en estas condiciones.")
    if conceptoDXAEN == "Asegurable":
        var = 1
        text_lines = textwrap.wrap(justificacion_positiva_DXAEN, width=127)
        var = len(text_lines)
        pdf.cell(epw, ac*var, '', align='C', border=1)
        pdf.ln(ac/8)
        for line in text_lines:
            pdf.cell(epw, ac, line, border=0, align='L')
            pdf.ln(ac)
    else: 
        var = 1
        text_lines = textwrap.wrap(justificacion_Negativa_DXAEN, width=127)
        var = len(text_lines)
        pdf.cell(epw, ac*var, '', align='C', border=1)
        pdf.ln(ac/8)
        for line in text_lines:
            pdf.cell(epw, ac, line, border=0, align='L')
            pdf.ln(ac)
    print("Modelo de DXAEN completo")    
    
    footer()
    

    #Garantías
    texto = '''Durante la vigencia de la póliza, se realizará la suspensión del suministro de energía eléctrica durante las horas y días no laborables a los circuitos de distribución eléctrica. Esta suspensión se aplicará a los equipos o áreas que no son indispensables para el desarrollo de las actividades del asegurado. Se entiende como indispensables aquellos circuitos que suministran energía a equipos o áreas que, debido al funcionamiento de la empresa, no pueden quedarse sin energía. La implementación de esta suspensión debe documentarse mediante un procedimiento que incluya responsables definidos y registros suficientes.''' 
    texto1= '''Durante la vigencia de la póliza, el asegurado debe mantener un sistema de puesta a tierra de capacidad suficiente para proteger los equipos electrónicos existentes en las instalaciones y realizar mantenimiento preventivo anual al sistema. Evidenciar las actividades de mantenimiento por medio de un registro documentado. Para la instalación de un sistema apropiado de puesta a tierra, tomar en consideración el Reglamento Técnico de Instalaciones Eléctricas (RETIE).'''
    texto2= '''Durante la vigencia de la póliza, el asegurado debe realizar mantenimiento por lo menos cada tres (3) meses a los canales y bajantes de aguas lluvias, cajas de inspección, entre otros. Este mantenimiento debe incluir la limpieza y la revisión de los desagües de aguas lluvias que protegen el predio de inundaciones. Además, se debe respaldar el desagüe con un sistema de bombeo con motobombas sumergibles para evacuar cualquier fluido en caso de inundación.'''
    texto3='''Durante la vigencia de la póliza, el asegurado debe realizar mantenimiento, por lo menos cada seis (6) meses, a la impermeabilización, canales y bajantes, el cual incluya su limpieza y la revisión del manto que protege la cubierta. Evidenciar las actividades de mantenimiento por medio de un registro documentado o bitácora.'''
    if info_catastro == True:
        numero_sotanos
        CatastrO[0][3]
    
    pdf.add_page()
    header()
    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(epw, ac, "9 - GARANTÍAS", border=0, align='C')
    pdf.ln(ac*2)
    
    pdf.set_font('Times', '', 12.0)

    # GARANTÍA CORTE DE ENERGÍA
    pdf.set_fill_color(0, 108, 41)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(w = 0, h = 0.25, txt = 'CORTE DE ENERGÍA 405-5', border = 1, ln=1, align = 'C', fill = 1)
    pdf.set_text_color(0, 0, 0)
    var = 1
    text_lines = textwrap.wrap(texto, width=105)
    var = len(text_lines)
    pdf.cell(epw, ac*var, '', align='C', border=1)
    pdf.ln(ac/8)
    for line in text_lines:
        pdf.cell(epw, ac, line, border=0, align='L')
        pdf.ln(ac)
    pdf.ln(ac)
    
     # GARANTÍA SISTEMA DE PUESTA A TIERRA
    if info_catastro == True:
        if antiguedad_previa_2010 == True:
            pdf.set_fill_color(0, 108, 41)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(w = 0, h = 0.25, txt = 'SISTEMA DE PUESTA A TIERRA 421-3', border = 1, ln=1, align = 'C', fill = 1)
            pdf.set_text_color(0, 0, 0)
            var = 1
            text_lines = textwrap.wrap(texto1, width=105)
            var = len(text_lines)
            pdf.cell(epw, ac*var, '', align='C', border=1)
            pdf.ln(ac/8)
            for line in text_lines:
                pdf.cell(epw, ac, line, border=0, align='L')
                pdf.ln(ac)
            pdf.ln(ac)
        # GARANTÍA INUNDACIÓN EN SÓTANO
        if str(ns).isdigit():
            if ns > 0 or nss > 0:
                pdf.set_fill_color(0, 108, 41)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(w = 0, h = 0.25, txt = 'INUNDACIÓN EN SÓTANO 415-5', border = 1, ln=1, align = 'C', fill = 1)
                pdf.set_text_color(0, 0, 0)
                var = 1
                text_lines = textwrap.wrap(texto2, width=105)
                var = len(text_lines)
                pdf.cell(epw, ac * var, '', align='C', border=1)
                pdf.ln(ac / 8)
                for line in text_lines:
                    pdf.cell(epw, ac, line, border=0, align='L')
                    pdf.ln(ac)
                pdf.ln(ac)
        else:
            pass
    else:
        pdf.set_fill_color(0, 108, 41)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(w = 0, h = 0.25, txt = 'SISTEMA DE PUESTA A TIERRA 421-3', border = 1, ln=1, align = 'C', fill = 1)
        pdf.set_text_color(0, 0, 0)
        var = 1
        text_lines = textwrap.wrap(texto1, width=105)
        var = len(text_lines)
        pdf.cell(epw, ac*var, '', align='C', border=1)
        pdf.ln(ac/8)
        for line in text_lines:
            pdf.cell(epw, ac, line, border=0, align='L')
            pdf.ln(ac)
        pdf.ln(ac)

        pdf.set_fill_color(0, 108, 41)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(w = 0, h = 0.25, txt = 'INUNDACIÓN EN SÓTANO 415-5', border = 1, ln=1, align = 'C', fill = 1)
        pdf.set_text_color(0, 0, 0)
        var = 1
        text_lines = textwrap.wrap(texto2, width=105)
        var = len(text_lines)
        pdf.cell(epw, ac * var, '', align='C', border=1)
        pdf.ln(ac / 8)
        for line in text_lines:
            pdf.cell(epw, ac, line, border=0, align='L')
            pdf.ln(ac)
        pdf.ln(ac)
    
    

    # GARANTÍA MANTENIMIENTO A IMPERMEABILIZACIÓN
    pdf.set_fill_color(0, 108, 41)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(w = 0, h = 0.25, txt = 'MANTENIMIENTO A IMPERMEABILIZACIÓN 414-5', border = 1, ln=1, align = 'C', fill = 1)
    pdf.set_text_color(0, 0, 0)
    var = 1
    text_lines = textwrap.wrap(texto3, width=105)
    var = len(text_lines)
    pdf.cell(epw, ac*var, '', align='C', border=1)
    pdf.ln(ac/8)
    for line in text_lines:
        pdf.cell(epw, ac, line, border=0, align='L')
        pdf.ln(ac)
    
    footer()
    
    print("garantiascompleto")
    
    
    ################## CONCEPTO ID ###############################
    
    pdf.add_page()
    header()
    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(epw, ac, "10 - CONCEPTO INGENIERO DIGITAL", border=0, align='C')
    pdf.ln(ac*2)

    pdf.set_font('Times', '', 12.0)
    
    def agregar_concepto(pdf, titulo, mensaje):
        pdf.set_font('Times', 'B', 14.0)
        celda_verde(epw, ac, titulo)
        pdf.ln() 
        
        pdf.set_font('Times', '', 10.0)
        var = 1
        text_lines = textwrap.wrap(mensaje, width=120)
        var = len(text_lines)
        pdf.cell(epw, ac*var, '', align='C', border=1)
        pdf.ln(ac/8)    
        for line in text_lines:
            pdf.cell(epw, ac, line, border=0, align='L')
            pdf.ln(ac)
        pdf.ln()
    
    if is_cc == False:    
        #CONDICIÓN 1
        if IsAseg == False:
            condicion1 = "No asegurable"
        else:
            condicion1 = "Asegurable"
        #CONDICIÓN 2
        if info_catastro == True:
            if MatrizAmenazas[0] in ["Medio-alto", "alta"] and año_construccion < 1985:
                condicion2 = "No asegurable"
            else:
                condicion2 = "Asegurable"
        else:
            condicion2 = "Sin información"
        #CONDICIÓN 3
        if concepto == "No asegurable":
            condicion3 = "No asegurable"
        else:
            condicion3 = "Asegurable"
        #CONDICIÓN 4
    
        if MatrizAmenazasManzaneo[0] == "Sin información":
            condicion4 = "Sin información"
        elif (ConceptoManzaneo[0] == "S" and MatrizAmenazasManzaneo[0].lower() == "alto"):
            condicion4 = "No asegurable"
        else:
            condicion4 = "Asegurable"
        #CONDICIÓN 5
        if info_catastro == True:
            if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta") and año_construccion < 1985:
                condicion5 = "No asegurable"
            else:
                condicion5 = "Asegurable"
        else:
            condicion5 = "Sin información"
    else:
        condicion1 = "No aplica"
        if MatrizAmenazas[0] in ["Medio-alto", "alta"] and año_construccion < 1985:
            condicion2 = "No asegurable"
        else:
            condicion2 = "Asegurable"
        if concepto == "No asegurable":
            condicion3 = "No asegurable"
        else:
            condicion3 = "Asegurable"
        if MatrizAmenazasManzaneo[0] == "Sin información" or (ConceptoManzaneo[0] == "S" and MatrizAmenazasManzaneo[0].lower() == "alto"):
            condicion4 = "No asegurable"
        else:
            condicion4 = "Asegurable"
        if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta") and año_construccion < 1985:
            condicion5 = "No asegurable"
        else:
            condicion5 = "Asegurable"

    celda_verde(5.5, ac, "Concepto del ID")
    pdf.ln(ac)

    rID = [
        ['Actividad económica', condicion1],
        # ['Concepto por incurrido en siniestros', "En desarrollo"],
        ['Año de constr. - Amenaza del VM Terremoto', condicion2],
        ['Modelo de Terremoto', condicion3],
        ['Manzaneo - Amenaza Incendio Manz.', condicion4],
        ['Año de constr. - Amenaza del VM Remoción', condicion5],
    ]
    x = pdf.get_x()
    for row in rID:
        for item in row:
            pdf.cell(5.5/2, ac, str(item), border=1, align='C')  # Ajustar el tamaño de la celda según sea necesario
        pdf.ln(ac)
    pdf.set_x(x)  
    pdf.ln(ac)
    
    if is_cc == False and info_catastro == True:
        justificacionID = "Se trata de la empresa " +str(tomador)+" ubicada en la "+str(direccion)+" de la ciudad de Bogotá. El predio fue construído en el año de " +str(año_construccion)+ "."
    elif is_cc == False and info_catastro == False:
        justificacionID = "Se trata de la empresa " +str(tomador)+" ubicada en la "+str(direccion)+" de la ciudad de Bogotá. No hay información del año de construcción del predio."
    else:
        justificacionID = "La dirección de la persona natural es " +str(direccion)+ " de la ciudad de Bogotá. El predio fue construído en el año de " +str(año_construccion)+ "."
    
    if is_cc == False and info_catastro == True:
        if condicion1 == "No asegurable" or condicion2 == "No asegurable" or condicion3 == "No asegurable" or condicion4 == "No asegurable" or condicion5 == "No asegurable":
            conceptoID = "No asegurable"
            #Condición 1
            if (IsAseg == False):
                justificacionID += " La empresa " +str(tomador)+ " tiene como actividad económica principal " +str(ciiu_dado[0])+ ", la cual se considera como fuera de políticas de acuerdo con las políticas establecidas por la compañía."
            elif (IsAseg == True):
                justificacionID += " La empresa " +str(tomador)+ " tiene como actividad económica principal " +str(ciiu_dado[0])+ ", la cual se encuentra amparada por las políticas establecidas por la empresa."
            #Condición 2
            if MatrizAmenazas[0] in ["Medio-alto", "alta"] and año_construccion < 1985:
                justificacionID += " El predio cuenta con un riesgo Medio - Alto o Alto para la amenaza de terremoto según el visor de mapas y el año de construcción del predio es previo a 1985."
            if not(MatrizAmenazas[0] in ["Medio-alto", "alta"]) and año_construccion < 1985:
                justificacionID += " El predio cuenta con un riesgo aceptable para la amenaza de terremoto según el visor de mapas, sin embargo el año de construcción del predio es previo a 1985."
            if MatrizAmenazas[0] in ["Medio-alto", "alta"] and not(año_construccion < 1985):
                justificacionID += " El predio cuenta con un riesgo Medio - Alto o Alto para la amenaza de terremoto según el visor de mapas, sin embargo el año de construcción del predio es posterior a 1985."
            if not(MatrizAmenazas[0] in ["Medio-alto", "alta"]) and not(año_construccion < 1985):
                justificacionID += " El predio cuenta con un riesgo aceptable para la amenaza de terremoto según el visor de mapas y el año de construcción del predio es posterior a 1985."
            #Condición 3
            if concepto == "Sin información suficiente":
                justificacionID += " Por otro lado, no hay información suficiente para generar un concepto para el modelo de riesgo de Terremoto."
            if concepto == "No asegurable":
                justificacionID += " Por otro lado, el predio no es asegurable bajo el concepto del modelo de riesgo de Terremoto."
            elif not(concepto == "No asegurable"):
                justificacionID += " Por otro lado, el predio si es asegurable bajo el concepto del modelo de riesgo de Terremoto."
            #Condición 4
            if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "S":
                justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es desfavorable."
            if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "N":
                justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es favorable."    
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable igual que la amenaza de incendio de la capa de manzaneo."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (not(ConceptoManzaneo[0] == "S") and MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable pero la amenaza de incendio de la capa de manzaneo es Alta."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and not(MatrizAmenazasManzaneo[0].lower() == "alto")):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable pero la amenaza de incendio de la capa de manzaneo es aceptable."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and not(ConceptoManzaneo[0] == "S") and not (MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable igual que la amenaza de incendio de la capa de manzaneo."
            #Condición 5
            if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta") and año_construccion < 1985:
                justificacionID += " También, la amenaza de remoción en masa es desfavorable según el visor de mapas."
            if (not(MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta")) and año_construccion < 1985:
                justificacionID += " También, la amenaza de remoción en masa es aceptable según el visor de mapas."
            if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta") and not(año_construccion < 1985):
                justificacionID += " También, la amenaza de remoción en masa es desfavorable según el visor de mapas."
            elif not((MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta")) and not (año_construccion < 1985):
                justificacionID += " También, la amenaza de remoción en masa es favorable según el visor de mapas."
        
            justificacionID += " El concepto final de asegurabilidad del ID dada toda la justificación anterior es NO ASEGURABLE." 
        
        else:
            conceptoID = "Asegurable"
            #Condición 1
            if (IsAseg == False):
                justificacionID += " La empresa " +str(tomador)+ " tiene como actividad económica principal " +str(ciiu_dado[0])+ ", la cual se considera como fuera de políticas de acuerdo con las políticas de la compañía."
            elif (IsAseg == True):
                justificacionID += " La empresa " +str(tomador)+ " tiene como actividad económica principal " +str(ciiu_dado[0])+ ", la cual se encuentra amparada por las políticas establecidas por la empresa."
            #Condición 2
            if MatrizAmenazas[0] in ["Medio-alto", "alta"] and año_construccion < 1985:
                justificacionID += " El predio cuenta con un riesgo Medio - Alto o Alto para la amenaza de terremoto según el visor de mapas y el año de construcción del predio es previo a 1985."
            if not(MatrizAmenazas[0] in ["Medio-alto", "alta"]) and año_construccion < 1985:
                justificacionID += " El predio cuenta con un riesgo aceptable para la amenaza de terremoto según el visor de mapas, sin embargo el año de construcción del predio es previo a 1985."
            if MatrizAmenazas[0] in ["Medio-alto", "alta"] and not(año_construccion < 1985):
                justificacionID += " El predio cuenta con un riesgo Medio - Alto o Alto para la amenaza de terremoto según el visor de mapas, sin embargo el año de construcción del predio es posterior a 1985."
            if not(MatrizAmenazas[0] in ["Medio-alto", "alta"]) and not(año_construccion < 1985):
                justificacionID += " El predio cuenta con un riesgo aceptable para la amenaza de terremoto según el visor de mapas y el año de construcción del predio es posterior a 1985."
            #Condición 3
            if concepto == "Sin información suficiente":
                justificacionID += " Por otro lado, no hay información suficiente para generar un concepto para el modelo de riesgo de Terremoto."
            if concepto == "No asegurable":
                justificacionID += " Por otro lado, el predio no es asegurable bajo el concepto del modelo de riesgo de Terremoto."
            elif not(concepto == "No asegurable"):
                justificacionID += " Por otro lado, el predio si es asegurable bajo el concepto del modelo de riesgo de Terremoto."
            #Condición 4
            if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "S":
                justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es desfavorable."
            if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "N":
                justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es favorable."    
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable igual que la amenaza de incendio de la capa de manzaneo."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (not(ConceptoManzaneo[0] == "S") and MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable pero la amenaza de incendio de la capa de manzaneo es Alta."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and not(MatrizAmenazasManzaneo[0].lower() == "alto")):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable pero la amenaza de incendio de la capa de manzaneo es aceptable."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and not(ConceptoManzaneo[0] == "S") and not (MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable igual que la amenaza de incendio de la capa de manzaneo."
            #Condición 5
            if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta") and año_construccion < 1985:
                justificacionID += " También, la amenaza de remoción en masa es desfavorable según el visor de mapas."
            if (not(MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta")) and año_construccion < 1985:
                justificacionID += " También, la amenaza de remoción en masa es aceptable según el visor de mapas."
            if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta") and not(año_construccion < 1985):
                justificacionID += " También, la amenaza de remoción en masa es desfavorable según el visor de mapas."
            elif not((MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta")) and not (año_construccion < 1985):
                justificacionID += " También, la amenaza de remoción en masa es favorable según el visor de mapas."
            
            justificacionID += " El concepto final de asegurabilidad del ID dada toda la justificación anterior es ASEGURABLE."
    if is_cc == False and info_catastro == False:
        if condicion1 == "No asegurable" or condicion2 == "No asegurable" or condicion3 == "No asegurable" or condicion4 == "No asegurable" or condicion5 == "No asegurable":
            conceptoID = "No asegurable"
            #Condición 1
            if (IsAseg == False):
                justificacionID += " La empresa " +str(tomador)+ " tiene como actividad económica principal " +str(ciiu_dado[0])+ ", la cual se considera como fuera de políticas de acuerdo con las políticas establecidas por la compañía."
            elif (IsAseg == True):
                justificacionID += " La empresa " +str(tomador)+ " tiene como actividad económica principal " +str(ciiu_dado[0])+ ", la cual se encuentra amparada por las políticas establecidas por la empresa."
            #Condición 2
            if MatrizAmenazas[0] in ["Medio-alto", "alta"]:
                justificacionID += " El predio cuenta con un riesgo Medio - Alto o Alto para la amenaza de terremoto según el visor de mapas."
            if not(MatrizAmenazas[0] in ["Medio-alto", "alta"]):
                justificacionID += " El predio cuenta con un riesgo aceptable para la amenaza de terremoto según el visor de mapas."
            #Condición 3
            if concepto == "Sin información suficiente":
                justificacionID += " Por otro lado, no hay información suficiente para generar un concepto para el modelo de riesgo de Terremoto."
            if concepto == "No asegurable":
                justificacionID += " Por otro lado, el predio no es asegurable bajo el concepto del modelo de riesgo de Terremoto."
            elif not(concepto == "No asegurable"):
                justificacionID += " Por otro lado, el predio si es asegurable bajo el concepto del modelo de riesgo de Terremoto."
            #Condición 4
            if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "S":
                justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es desfavorable."
            if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "N":
                justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es favorable."    
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable igual que la amenaza de incendio de la capa de manzaneo."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (not(ConceptoManzaneo[0] == "S") and MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable pero la amenaza de incendio de la capa de manzaneo es Alta."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and not(MatrizAmenazasManzaneo[0].lower() == "alto")):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable pero la amenaza de incendio de la capa de manzaneo es aceptable."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and not(ConceptoManzaneo[0] == "S") and not (MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable igual que la amenaza de incendio de la capa de manzaneo."
            #Condición 5
            if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta"):
                justificacionID += " También, la amenaza de remoción en masa es desfavorable según el visor de mapas."
            if (not(MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta")):
                justificacionID += " También, la amenaza de remoción en masa es aceptable según el visor de mapas."
                
            justificacionID += " El concepto final de asegurabilidad del ID dada toda la justificación anterior es NO ASEGURABLE." 
        
        else:
            conceptoID = "Asegurable"
            #Condición 1
            if (IsAseg == False):
                justificacionID += " La empresa " +str(tomador)+ " tiene como actividad económica principal " +str(ciiu_dado[0])+ ", la cual se considera como fuera de políticas de acuerdo con las políticas de la compañía."
            elif (IsAseg == True):
                justificacionID += " La empresa " +str(tomador)+ " tiene como actividad económica principal " +str(ciiu_dado[0])+ ", la cual se encuentra amparada por las políticas establecidas por la empresa."
            #Condición 2
            if MatrizAmenazas[0] in ["Medio-alto", "alta"]:
                justificacionID += " El predio cuenta con un riesgo Medio - Alto o Alto para la amenaza de terremoto según el visor de mapas."
            if not(MatrizAmenazas[0] in ["Medio-alto", "alta"]):
                justificacionID += " El predio cuenta con un riesgo aceptable para la amenaza de terremoto según el visor de mapas."
            #Condición 3
            if concepto == "Sin información suficiente":
                justificacionID += " Por otro lado, no hay información suficiente para generar un concepto para el modelo de riesgo de Terremoto."
            if concepto == "No asegurable":
                justificacionID += " Por otro lado, el predio no es asegurable bajo el concepto del modelo de riesgo de Terremoto."
            elif not(concepto == "No asegurable"):
                justificacionID += " Por otro lado, el predio si es asegurable bajo el concepto del modelo de riesgo de Terremoto."
            #Condición 4
            if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "S":
                justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es desfavorable."
            if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "N":
                justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es favorable."    
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable igual que la amenaza de incendio de la capa de manzaneo."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (not(ConceptoManzaneo[0] == "S") and MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable pero la amenaza de incendio de la capa de manzaneo es Alta."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and not(MatrizAmenazasManzaneo[0].lower() == "alto")):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable pero la amenaza de incendio de la capa de manzaneo es aceptable."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and not(ConceptoManzaneo[0] == "S") and not (MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable igual que la amenaza de incendio de la capa de manzaneo."
            #Condición 5
            if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta"):
                justificacionID += " También, la amenaza de remoción en masa es desfavorable según el visor de mapas."
            if (not(MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta")):
                justificacionID += " También, la amenaza de remoción en masa es aceptable según el visor de mapas."
      
            justificacionID += " El concepto final de asegurabilidad del ID dada toda la justificación anterior es ASEGURABLE."
    elif is_cc == True and info_catastro == True:
        if condicion1 == "No asegurable" or condicion2 == "No asegurable" or condicion3 == "No asegurable" or condicion4 == "No asegurable" or condicion5 == "No asegurable":
            conceptoID = "No asegurable"
           #Condición 2
            if MatrizAmenazas[0] in ["Medio-alto", "alta"] and año_construccion < 1985:
                justificacionID += " El predio cuenta con un riesgo Medio - Alto o Alto para la amenaza de terremoto según el visor de mapas y el año de construcción del predio es previo a 1985."
            if not(MatrizAmenazas[0] in ["Medio-alto", "alta"]) and año_construccion < 1985:
                justificacionID += " El predio cuenta con un riesgo aceptable para la amenaza de terremoto según el visor de mapas, sin embargo el año de construcción del predio es previo a 1985."
            if MatrizAmenazas[0] in ["Medio-alto", "alta"] and not(año_construccion < 1985):
                justificacionID += " El predio cuenta con un riesgo Medio - Alto o Alto para la amenaza de terremoto según el visor de mapas, sin embargo el año de construcción del predio es posterior a 1985."
            if not(MatrizAmenazas[0] in ["Medio-alto", "alta"]) and not(año_construccion < 1985):
                justificacionID += " El predio cuenta con un riesgo aceptable para la amenaza de terremoto según el visor de mapas y el año de construcción del predio es posterior a 1985."
            #Condición 3
            if concepto == "Sin información suficiente":
                justificacionID += " Por otro lado, no hay información suficiente para generar un concepto para el modelo de riesgo de Terremoto."
            if concepto == "No asegurable":
                justificacionID += " Por otro lado, el predio no es asegurable bajo el concepto del modelo de riesgo de Terremoto."
            elif not(concepto == "No asegurable"):
                justificacionID += " Por otro lado, el predio si es asegurable bajo el concepto del modelo de riesgo de Terremoto."
            #Condición 4
            if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "S":
                justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es desfavorable."
            if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "N":
                justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es favorable."    
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable igual que la amenaza de incendio de la capa de manzaneo."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (not(ConceptoManzaneo[0] == "S") and MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable pero la amenaza de incendio de la capa de manzaneo es Alta."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and not(MatrizAmenazasManzaneo[0].lower() == "alto")):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable pero la amenaza de incendio de la capa de manzaneo es aceptable."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and not(ConceptoManzaneo[0] == "S") and not (MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable igual que la amenaza de incendio de la capa de manzaneo."
            #Condición 5
            if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta") and año_construccion < 1985:
                justificacionID += " También, la amenaza de remoción en masa es desfavorable según el visor de mapas."
            if (not(MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta")) and año_construccion < 1985:
                justificacionID += " También, la amenaza de remoción en masa es aceptable según el visor de mapas."
            if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta") and not(año_construccion < 1985):
                justificacionID += " También, la amenaza de remoción en masa es desfavorable según el visor de mapas."
            elif not((MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta")) and not (año_construccion < 1985):
                justificacionID += " También, la amenaza de remoción en masa es favorable según el visor de mapas."
            
            justificacionID += " El concepto final de asegurabilidad del ID dada toda la justificación anterior es NO ASEGURABLE." 
        
        else:
            conceptoID = "Asegurable"
             #Condición 2
            if MatrizAmenazas[0] in ["Medio-alto", "alta"] and año_construccion < 1985:
                justificacionID += " El predio cuenta con un riesgo Medio - Alto o Alto para la amenaza de terremoto según el visor de mapas y el año de construcción del predio es previo a 1985."
            if not(MatrizAmenazas[0] in ["Medio-alto", "alta"]) and año_construccion < 1985:
                justificacionID += " El predio cuenta con un riesgo aceptable para la amenaza de terremoto según el visor de mapas, sin embargo el año de construcción del predio es previo a 1985."
            if MatrizAmenazas[0] in ["Medio-alto", "alta"] and not(año_construccion < 1985):
                justificacionID += " El predio cuenta con un riesgo Medio - Alto o Alto para la amenaza de terremoto según el visor de mapas, sin embargo el año de construcción del predio es posterior a 1985."
            if not(MatrizAmenazas[0] in ["Medio-alto", "alta"]) and not(año_construccion < 1985):
                justificacionID += " El predio cuenta con un riesgo aceptable para la amenaza de terremoto según el visor de mapas y el año de construcción del predio es posterior a 1985."
            #Condición 3
            if concepto == "Sin información suficiente":
                justificacionID += " Por otro lado, no hay información suficiente para generar un concepto para el modelo de riesgo de Terremoto."
            if concepto == "No asegurable":
                justificacionID += " Por otro lado, el predio no es asegurable bajo el concepto del modelo de riesgo de Terremoto."
            elif not(concepto == "No asegurable"):
                justificacionID += " Por otro lado, el predio si es asegurable bajo el concepto del modelo de riesgo de Terremoto."
            #Condición 4
            if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "S":
                justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es desfavorable."
            if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "N":
                justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es favorable."    
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable igual que la amenaza de incendio de la capa de manzaneo."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (not(ConceptoManzaneo[0] == "S") and MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable pero la amenaza de incendio de la capa de manzaneo es Alta."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and not(MatrizAmenazasManzaneo[0].lower() == "alto")):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable pero la amenaza de incendio de la capa de manzaneo es aceptable."
            if not(MatrizAmenazasManzaneo[0] == "Sin información") and not(ConceptoManzaneo[0] == "S") and not (MatrizAmenazasManzaneo[0].lower() == "alto"):
                justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable igual que la amenaza de incendio de la capa de manzaneo."
            #Condición 5
            if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta") and año_construccion < 1985:
                justificacionID += " También, la amenaza de remoción en masa es desfavorable según el visor de mapas."
            if (not(MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta")) and año_construccion < 1985:
                justificacionID += " También, la amenaza de remoción en masa es aceptable según el visor de mapas."
            if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta") and not(año_construccion < 1985):
                justificacionID += " También, la amenaza de remoción en masa es desfavorable según el visor de mapas."
            elif not((MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alta")) and not (año_construccion < 1985):
                justificacionID += " También, la amenaza de remoción en masa es favorable según el visor de mapas."
            
            justificacionID += " El concepto final de asegurabilidad del ID dada toda la justificación anterior es ASEGURABLE."

        
     
    agregar_concepto(pdf,"Justificación del ID", justificacionID)
    

    if conceptoID == "Asegurable":
        pdf.image(r'Archivos/Check.png', x = 6.2, y = 1.8, w = 1, h = 1)
    if conceptoID == "No asegurable":
        pdf.image(r'Archivos/Error.png', x = 6.2, y = 1.8, w = 1, h = 1)
    
    footer()
    # ANEXOS
    pdf.add_page()
    header()
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, "11 - ANEXOS", border=0, align = 'C') 
    pdf.ln(ac*2)
    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "1- MAPA DE LA ZONA", border=0, align = 'L') 
    pdf.image(r'Archivos/Mapas/ID/'+str(DIRECCION)+'.png', x = 1.5, y = ac*9 , w = ac*20, h = ac*16)
    pdf.image(r'Archivos/Mapas/ID/'+str(DIRECCION)+'S.png', x = 1.5, y = ac*25 , w = ac*20, h = ac*16)
    pdf.ln(ac*22)
    footer()

    pdf.add_page()
    header()
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, "2 - CAPTURAS DE STREETVIEW", border=0, align = 'L') 
    pdf.image(r'Archivos/Mapas/ID/'+str(DIRECCION)+'C0.jpeg', x = 0.75, y = ac*8 , w = ac*14, h = ac*14)
    pdf.image(r'Archivos/Mapas/ID/'+str(DIRECCION)+'C90.jpeg', x = 1+(ac*13), y = ac*8 , w = ac*14, h = ac*14)
    pdf.image(r'Archivos/Mapas/ID/'+str(DIRECCION)+'C180.jpeg', x = 0.75, y = ac*25 , w = ac*14, h = ac*14)
    pdf.image(r'Archivos/Mapas/ID/'+str(DIRECCION)+'C270.jpeg', x = 1+(ac*13), y = ac*25 , w = ac*14, h = ac*14)
    footer()

    pdf.add_page()
    header()
    pdf.set_font('Times','B',14.0) 
    if incurrido.empty:
        pdf.cell(epw, ac, "3 - CUADRO SINIESTROS", border=0, align = 'L')
        pdf.ln()
        pdf.set_font('Times','B',12.0) 
        pdf.ln()
        celda_verde(epw, ac, "NO HA INCURRIDO EN SINIESTROS")
        pass
    else:
        pdf.cell(epw, ac, "3 - CUADRO SINIESTROS", border=0, align = 'L')
        pdf.ln()
        pdf.set_font('Times','B',12.0) 
        pdf.ln()
        celda_verde(epw, ac,"INCURRIDO EN SINIESTROS")
        pdf.set_font('Times','B',8.0) 
        pdf.ln(ac)
        pdf.cell(1.218, ac, "CÓDIGO PRODUCTO", align='C', border = 1)
        pdf.cell(epw/6.3, ac, "NÚMERO DE PÓLIZA", align='C', border = 1)
        pdf.cell(epw/5.5, ac, "NÚMERO DE SINIESTRO", align='C', border = 1)
        pdf.cell(epw/6, ac, "FECHA DE SINIESTRO", align='C', border = 1)
        pdf.cell(epw/7, ac, "INCURRIDO", align='C', border = 1)
        pdf.cell(epw/5.2, ac, "ESTADO SINIESTRO", align='C', border = 1)

        pdf.set_font('Times','',8.0) 

        codigo_producto = incurrido["CODIGO_PRODUCTO"].tolist()
        numero_poliza = incurrido["NUMERO_POLIZA"].tolist()
        numero_siniestro = incurrido["NUMERO_SINIESTRO"].tolist()
        fecha_siniestro = incurrido["FECHA_SINIESTRO"].tolist()
        monto_incurrido = incurrido["INCURRIDO"].tolist()
        descripcion_causa = incurrido["ESTADO_SINIESTRO_CALCULADO"].tolist()

        num_filas = len(codigo_producto)
        pdf.ln()
        for i, row in incurrido_ordenado.iterrows():
            pdf.cell(1.218, ac, str(codigo_producto[i]), align='C', border=1)
            pdf.cell(epw/6.3, ac, str(numero_poliza[i]), align='C', border=1)
            pdf.cell(epw/5.5, ac, str(numero_siniestro[i]), align='C', border=1)
            pdf.cell(epw/6, ac, str(fecha_siniestro[i]), align='C', border=1)
            monto_incurrido_formato = "{:,.2f}".format(monto_incurrido[i])
            pdf.cell(epw/7, ac, str(monto_incurrido_formato), align='C', border=1)
            pdf.cell(epw/5.2, ac, str(descripcion_causa[i]), align='C', border=1)
            pdf.ln()
    footer()
    
    os.remove('Archivos/Mapas/ID/'+str(DIRECCION)+'.png')
    os.remove('Archivos/Mapas/ID/'+str(DIRECCION)+'S.png')
    os.remove('Archivos/Mapas/ID/'+str(DIRECCION)+'C0.jpeg')
    os.remove('Archivos/Mapas/ID/'+str(DIRECCION)+'C90.jpeg')
    os.remove('Archivos/Mapas/ID/'+str(DIRECCION)+'C180.jpeg')
    os.remove('Archivos/Mapas/ID/'+str(DIRECCION)+'C270.jpeg')
    
    print("Anexos completo")
    pdf.output('Archivos/PDF/ID/' + DireccioN[0] + 'NI.pdf', 'F')
    print(DireccioN[0])
    
    print("PDF GENERADO")
    
    #Cargar PDF CIRO integración
    def cargarPdf(nombre):

        import os 

        #Drive 

        ruta_destino = '/Proyectos/Ingeniero Digital/ReportesCiro/'
        ruta_origen = 'Archivos/PDF/ID/'
        filename_out= nombre

        print(os.system(f"rclone copy '{ruta_origen}{filename_out}' IyCUnidad:'{ruta_destino}'"))

    cargarPdf(DireccioN[0] + 'NI.pdf')
    
    ubicacionPDF = str('Archivos/PDF/ID/' + DireccioN[0] + 'NI.pdf')

    os.remove('Archivos/PDF/ID/' + DireccioN[0] + 'NI.pdf')

    mapas = ""
    
    try: 
        Terremoto = MatrizAmenazas[0]
        Vientos = MatrizAmenazas[1]
        Remocion = MatrizAmenazas[2]
        Sustraccion = MatrizAmenazas[3]
        Orden = MatrizAmenazas[4]
        Rayos = MatrizAmenazas[5]
        Inundacion = MatrizAmenazas[6]
        AMIT = MatrizAmenazas[7]    
    except:
        Terremoto = "Sin info"
        Vientos = "Sin info"
        Remocion = "Sin info"
        Sustraccion = "Sin info"
        Orden = "Sin info"
        Rayos = "Sin info"
        Inundacion = "Sin info"
        AMIT = "Sin info"  
        mapas = True

    fin = time.time()
    tiempo = fin - inicio
    print("Llego a guardar info")
    try:
            
        reg = ["API_pruebas", str(DIRECCION), datetime.now(), str(nit), str(tomador), str(ValoR), str(concepto), str(CatastrO[0][1]), str(sis), str(tip), str(ConceptoManzaneo[0]), str(Terremoto),
            str(Vientos), str(Remocion), str(Sustraccion), str(Orden), str(Rayos), str(Inundacion), str(AMIT), str(ciiu_numero).replace("'", ""), str(direccion), 
            str(SectoR[0][1]), str(SectoR[0][0]), str(SectoR[0][2]), str(LatloN[0][0]), str(LatloN[0][1]), str(npi), str(ns), str(nss), str(CatastrO[0][0][1]), 
            str(CatastrO[0][0][1]), str(CatastrO[0][0][2]), str(CatastrO[0][0][3]), str(CatastrO[0][2]), str(CatastrO[0][3]),
            str(CatastrO[0][4]), str(CatastrO[0][5]), str(CatastrO[0][6]), str(tip), str(CatastrO[0][8]), str(CatastrO[0][10]), str(CatastrO[0][9]),
            str(CatastrO[0][11]), str(CatastrO[0][12]), str(CatastrO[0][13]), str(CatastrO[0][14]), str(CatastrO[0][15]), str(CatastrO[0][16]),
            str(PrecusO), str(estrato), str(sire[["Fecha reporte", "Tipo de afectación"]]), tiempo, 
            empleados, 
            ingresos,
            distHidrante,
            distBomberos,
            distCai,
            distPolicia,
            "Exitoso",
            str(conceptoSus),
            str(proRobo),
            str(ento),
            str(riesgoSismo),
            str(escala),
            str(g_amen_pre_inc),
            str(politicas_incendio),
            str(nivelIncendio),
            str(conceptoIncendio),         
            str(conceptoID),
            str(justificacionID),
            str(IsAseg),
            ]

        con2 = psycopg2.connect(database="ingDigitalCA", user="postgres", password="Bolivar2021",
            host="35.153.192.47", port=8081)

        cur = con2.cursor()
        cur.execute("""INSERT INTO first_consultas("usuario", "direccionEstand", "fechaConsulta",  "nit", "razonSocial",
        "valorAsegurar", "conceptoTerre", "material", "sistema", "tipo", 
        "manzaneo","terremoto","vientos","remocion", "sustraccion",
        "orden", "rayos", "inundacion", "amit", "ciuu",
        "direccion", "barrio", "upz", "localidad", "latitud",
        "longitud", "numeroPisos","numeroSotanos", "numeroSemiSotanos", "areaTerreno",
        "areaConstruida", "anoConstruccion", "areaUso", "muros", "cubierta",
        "estadoEstructura", "fachada", "estadoAcabados", "clasificacionPropiedad", "topografia", 
        "zonaMitigable", "cerchas", "tipoSuelo", "vias", "estadoVias", 
        "influenciaVias", "cubrimientoMuros", "acabadoPisos", "usoPredios", "estrato", 
        "sire", "tiempoRespuesta", "emisEmpleados", "emisIngresos", "distHidrante", 
        "distEstacionBomb", "distCai", "distEstacionPoli" , "respuesta" , "conceptoSustraccion", 
        "proRobo", "calEntorno", "danoEsperado", "nivelRiesgoTerre", "sectorIncendio", 
        "politicasIncendio", "nivelIncendio", "conceptoIncendio", "conceptoFinal", "justificacion", "politicasAE") VALUES (
                                                                                    %s, %s, %s, %s, %s,
                                                                                    %s, %s, %s, %s, %s, 
                                                                                    %s, %s, %s, %s, %s,
                                                                                    %s, %s, %s, %s, %s, 
                                                                                    %s, %s, %s, %s, %s, 
                                                                                    %s, %s, %s, %s, %s,
                                                                                    %s, %s, %s, %s, %s, 
                                                                                    %s, %s, %s, %s, %s, 
                                                                                    %s, %s, %s, %s, %s,
                                                                                    %s, %s, %s, %s, %s, 
                                                                                    %s, %s, %s, %s, %s,
                                                                                    %s, %s, %s, %s, %s,
                                                                                    %s, %s, %s, %s, %s,
                                                                                    %s, %s, %s, %s, %s, %s);""", reg)
        con2.commit()
        cur.close()
        con2.close()
        print("Guardo info")
    except:
            
        con2 = psycopg2.connect(database="ingDigitalCA", user="postgres", password="Bolivar2021",
            host="35.153.192.47", port=8081)
        
        reg = ["API_pruebas", direccion, datetime.now(), str(nit), "ERROR"]

        cur = con2.cursor()
        cur.execute("""INSERT INTO first_consultas("usuario", "direccion", "fechaConsulta",  "nit", "respuesta") VALUES (%s, %s, %s, %s, %s);""", reg)
        con2.commit()
        cur.close()
        con2.close()
        print("No logro guardar")

    if is_cc == False and info_catastro == True:
        #JSON    
        mjs = {
            "Nombre tomador": f'{tomador}',
            "NIT":f'{nit}',
            "Direccion": f'{direccion}',
            "Direccion Estandarizada": f'{DireccioN[0]}',
            "Valor a asegurar:": f'{valor_a_asegurar}',
            "Número de teléfono:": f'{telefono_principal}',
            "Fecha calificación predio": f'{predios["PreFCalif"].iloc[U]}',
            "Localidad": f'{SectoR[0][2]}',
            "Upz": f'{SectoR[0][1]}',
            "Barrio": f'{SectoR[0][0]}',
            "Latitud": f'{LatloN[0][0]}',
            "Longitud": f'{LatloN[0][1]}',
            "Terremoto VM":f'{Terremoto}',
            "Vientos VM":f'{Vientos}',
            "Remocion VM":f'{Remocion}',
            "Sustraccion VM":f'{Sustraccion}',
            "Orden VM":f'{Orden}',
            "Rayos VM":f'{Rayos}',   
            "Inundacion VM":f'{Inundacion}',
            "AMIT VM":f'{AMIT}',
            "Mapas": f'{mapas}',
            "Tipo": f'{tip}',
            "Número pisos": f'{npi}',
            "Número semi_sotanos": f'{ns}',
            "Número_sotanos": f'{nss}',
            "año construcción": f'{CatastrO[0][0][2]}',
            "Área terreno": f'{CatastrO[0][0][0]}',
            "Área construida": f'{CatastrO[0][0][1]}',
            "Área uso": f'{CatastrO[0][0][3]}',
            "Topografia": f'{CatastrO[0][8]}',
            "Material": f'{mat}',
            "Sistema estructural": f'{sis}',
            "Muros": f'{CatastrO[0][2]}', 
            "Armazón": f'{CatastrO[0][1]}',
            "Cubierta": f'{CatastrO[0][3]}',
            "Estado_estructura": f'{CatastrO[0][4]}',
            "Fachada": f'{CatastrO[0][5]}',
            "Estado acabados": f'{CatastrO[0][6]}',
            "Zona alto riesgo no mitigable": f'{CatastrO[0][10]}',
            "Cerchas": f'{CatastrO[0][9]}',
            "Clase suelo urbano": f'{CatastrO[0][11]}',
            "Acabado pisos": f'{CatastrO[0][16]}',
            "Cubrimiento muros": f'{CatastrO[0][15]}',
            "Vías": f'{CatastrO[0][12]}',
            "Estado vias": f'{CatastrO[0][13]}',
            "Influencia vias": f'{CatastrO[0][14]}',
            "Información CIIU": f'{ciiu_dado, ciiu_numero}',
            "Clasificacion tipo propiedad": f'{CatastrO[0][7]}',
            "Riesgos por AE": f'{IsAseg}',
            "Usos predios": f'{PrecusO}',
            "Estrato socioeconomico": f'{estrato[["ESoChip", "ESoEstrato"]]}',
            "Valor metro terreno": f'{valor_metro[["V_REF", "ANO"]].sort_values(by=["ANO"],axis=0)}',
            "Avaluos": f'{avaluos[["AVALUO_COM", "AVALUO_CAT"]]}',
            "SIRE": f'{sire[["Fecha reporte", "Tipo de afectación"]]}',
            "Empleados": f'{emis["num_empleados"]}',
            "Concepto Manzaneo": f'{ConceptoManzaneo[0]}',
            "Concepto Terremoto": f'{concepto}',
            "Porcentaje de daño esperado": f'{riesgoSismo}',
            "Nivel de riesgo": f'{escala}',
            "Concepto Sustracción": f'{conceptoSus}',
            "Porcentaje de robo": f'{proRobo}',
            "Calificación entorno": f'{ento}',
            "Concepto Incendio": f'{conceptoIncendio}',
            "Amenaza del sector": f'{g_amen_pre_inc}',
            "Politicas incendio": f'{politicas_incendio}',
            "Riesgo incendio total": f'{nivelIncendio}',
            "Concepto DXAEN": f'{conceptoDXAEN}',
            "Nivel de riesgo": f'{nivelDXAEN}',
            "Concepto ID": f'{conceptoID}',
            "Justificación ID": f'{justificacionID}',
            "Condición 1": f'{condicion1}',
            "Condición 2": f'{condicion2}',
            "Condición 3": f'{condicion3}',
            "Condición 4": f'{condicion4}',
            "Condición 5": f'{condicion5}',
            "Ruta": f'{ubicacionPDF}', 
        } 
    elif is_cc == False and info_catastro == False:
        #JSON    
        mjs = {
            "Nombre tomador": f'{tomador}',
            "NIT":f'{nit}',
            "Direccion": f'{direccion}',
            "Direccion Estandarizada": f'{DireccioN[0]}',
            "Valor a asegurar:": f'{valor_a_asegurar}',
            "Número de teléfono:": f'{telefono_principal}',
            "Fecha calificación predio": f'{"Sin información"}',
            "Localidad": f'{"Sin información"}',
            "Upz": f'{"Sin información"}',
            "Barrio": f'{"Sin información"}',
            "Latitud": f'{LatloN[0][0]}',
            "Longitud": f'{LatloN[0][1]}',
            "Terremoto VM":f'{Terremoto}',
            "Vientos VM":f'{Vientos}',
            "Remocion VM":f'{Remocion}',
            "Sustraccion VM":f'{Sustraccion}',
            "Orden VM":f'{Orden}',
            "Rayos VM":f'{Rayos}',   
            "Inundacion VM":f'{Inundacion}',
            "AMIT VM":f'{AMIT}',
            "Mapas": f'{mapas}',
            "Tipo": f'{"Sin información"}',
            "Número pisos": f'{"Sin información"}',
            "Número semi_sotanos": f'{"Sin información"}',
            "Número_sotanos": f'{"Sin información"}',
            "año construcción": f'{"Sin información"}',
            "Área terreno": f'{"Sin información"}',
            "Área construida": f'{"Sin información"}',
            "Área uso": f'{"Sin información"}',
            "Topografia": f'{"Sin información"}',
            "Material": f'{"Sin información"}',
            "Sistema estructural": f'{"Sin información"}',
            "Muros": f'{"Sin información"}', 
            "Armazón": f'{"Sin información"}',
            "Cubierta": f'{"Sin información"}',
            "Estado_estructura": f'{"Sin información"}',
            "Fachada": f'{"Sin información"}',
            "Estado acabados": f'{"Sin información"}',
            "Zona alto riesgo no mitigable": f'{"Sin información"}',
            "Cerchas": f'{"Sin información"}',
            "Clase suelo urbano": f'{"Sin información"}',
            "Acabado pisos": f'{"Sin información"}',
            "Cubrimiento muros": f'{"Sin información"}',
            "Vías": f'{"Sin información"}',
            "Estado vias": f'{"Sin información"}',
            "Influencia vias": f'{"Sin información"}',
            "Información CIIU": f'{ciiu_dado, ciiu_numero}',
            "Clasificacion tipo propiedad": f'{"Sin información"}',
            "Riesgos por AE": f'{IsAseg}',
            "Usos predios": f'{"Sin información"}',
            "Estrato socioeconomico": f'{"Sin información"}',
            "Valor metro terreno": f'{"Sin información"}',
            "Avaluos": f'{"Sin información"}',
            "SIRE": f'{sire[["Fecha reporte", "Tipo de afectación"]]}',
            "Empleados": f'{emis["num_empleados"]}',
            "Concepto Manzaneo": f'{ConceptoManzaneo[0]}',
            "Concepto Terremoto": f'{concepto}',
            "Porcentaje de daño esperado": f'{riesgoSismo}',
            "Nivel de riesgo": f'{escala}',
            "Concepto Sustracción": f'{conceptoSus}',
            "Porcentaje de robo": f'{proRobo}',
            "Calificación entorno": f'{ento}',
            "Concepto Incendio": f'{conceptoIncendio}',
            "Amenaza del sector": f'{g_amen_pre_inc}',
            "Politicas incendio": f'{politicas_incendio}',
            "Riesgo incendio total": f'{nivelIncendio}',
            "Concepto DXAEN": f'{conceptoDXAEN}',
            "Nivel de riesgo": f'{nivelDXAEN}',
            "Concepto ID": f'{conceptoID}',
            "Justificación ID": f'{justificacionID}',
            "Condición 1": f'{condicion1}',
            "Condición 2": f'{condicion2}',
            "Condición 3": f'{condicion3}',
            "Condición 4": f'{condicion4}',
            "Condición 5": f'{condicion5}',
            "Ruta": f'{ubicacionPDF}', 
        } 
    else:
        mjs = {"Nombre tomador": f'{tomador}',
        "NIT":f'No aplica',
        "Direccion": f'{direccion}',
        "Direccion Estandarizada": f'{DireccioN[0]}',
        "Valor a asegurar:": f'{valor_a_asegurar}',
        "Número de teléfono:": f'{telefono_principal}',
        "Fecha calificación predio": f'{predios["PreFCalif"].iloc[U]}',
        "Localidad": f'{SectoR[0][2]}',
        "Upz": f'{SectoR[0][1]}',
        "Barrio": f'{SectoR[0][0]}',
        "Latitud": f'{LatloN[0][0]}',
        "Longitud": f'{LatloN[0][1]}',
        "Terremoto VM":f'{Terremoto}',
        "Vientos VM":f'{Vientos}',
        "Remocion VM":f'{Remocion}',
        "Sustraccion VM":f'{Sustraccion}',
        "Orden VM":f'{Orden}',
        "Rayos VM":f'{Rayos}',   
        "Inundacion VM":f'{Inundacion}',
        "AMIT VM":f'{AMIT}',
        "Mapas": f'{mapas}',
        "Tipo": f'{tip}',
        "Número pisos": f'{npi}',
        "Número semi_sotanos": f'{ns}',
        "Número_sotanos": f'{nss}',
        "año construcción": f'{CatastrO[0][0][2]}',
        "Área terreno": f'{CatastrO[0][0][0]}',
        "Área construida": f'{CatastrO[0][0][1]}',
        "Área uso": f'{CatastrO[0][0][3]}',
        "Topografia": f'{CatastrO[0][8]}',
        "Material": f'{mat}',
        "Sistema estructural": f'{sis}',
        "Muros": f'{CatastrO[0][2]}', 
        "Armazón": f'{CatastrO[0][1]}',
        "Cubierta": f'{CatastrO[0][3]}',
        "Estado_estructura": f'{CatastrO[0][4]}',
        "Fachada": f'{CatastrO[0][5]}',
        "Estado acabados": f'{CatastrO[0][6]}',
        "Zona alto riesgo no mitigable": f'{CatastrO[0][10]}',
        "Cerchas": f'{CatastrO[0][9]}',
        "Clase suelo urbano": f'{CatastrO[0][11]}',
        "Acabado pisos": f'{CatastrO[0][16]}',
        "Cubrimiento muros": f'{CatastrO[0][15]}',
        "Vías": f'{CatastrO[0][12]}',
        "Estado vias": f'{CatastrO[0][13]}',
        "Influencia vias": f'{CatastrO[0][14]}',
        "Información CIIU": f'{ciiu_dado, ciiu_numero}',
        "Clasificacion tipo propiedad": f'{CatastrO[0][7]}',
        "Riesgos por AE": f'{IsAseg}',
        "Usos predios": f'{PrecusO}',
        "Estrato socioeconomico": f'{estrato[["ESoChip", "ESoEstrato"]]}',
        "Valor metro terreno": f'{valor_metro[["V_REF", "ANO"]].sort_values(by=["ANO"],axis=0)}',
        "Avaluos": f'{avaluos[["AVALUO_COM", "AVALUO_CAT"]]}',
        "SIRE": f'{sire[["Fecha reporte", "Tipo de afectación"]]}',
        "Empleados": f'{"No aplica"}',
        "Concepto Manzaneo": f'{ConceptoManzaneo[0]}',
        "Concepto Terremoto": f'{concepto}',
        "Porcentaje de daño esperado": f'{riesgoSismo}',
        "Nivel de riesgo": f'{escala}',
        "Concepto Sustracción": f'{conceptoSus}',
        "Porcentaje de robo": f'{proRobo}',
        "Calificación entorno": f'{ento}',
        "Concepto Incendio": f'{conceptoIncendio}',
        "Amenaza del sector": f'{g_amen_pre_inc}',
        "Politicas incendio": f'{politicas_incendio}',
        "Riesgo incendio total": f'{nivelIncendio}',
        "Concepto DXAEN": f'{conceptoDXAEN}',
        "Nivel de riesgo": f'{nivelDXAEN}',
        "Concepto ID": f'{conceptoID}',
        "Justificación ID": f'{justificacionID}',
        "Condición 1": f'{condicion1}',
        "Condición 2": f'{condicion2}',
        "Condición 3": f'{condicion3}',
        "Condición 4": f'{condicion4}',
        "Condición 5": f'{condicion5}',
        "Ruta": f'{ubicacionPDF}',
        } 
    return JSONResponse(status_code=200, content=mjs)

    
@app.get('/API/AR_COMPLEJOS_INDUSTRIALES')
async def StandAlone(latitud:str = None, longitud:str = None, nit: str = None, direccion:str = None, ciudad:str = None, departamento:str = None):
    print("Inicia proceso: "+nit)
    #Conexión bases de datos
    con = psycopg2.connect(database="ingdigital", user="postgres", password="Bolivar2021", host="35.153.192.47", port=8081)
    ciiu = pd.read_excel(r"Archivos/Estructura-detallada-CIIU-4AC-2020-.xls")

    #LIMPIAR NIT
        
    for i in range(0, len(nit)):
        if not (type(nit) == type(None) or str(nit) == 'nan'):
            nit = int(str(nit).replace('.', ''))
            nit = int(str(nit).replace(',', ''))
    try:
        for i in range(0, len(latitud)):
            if not (str(latitud) == 'nan' or type(latitud) == type(None)):
                latitud = float(str(latitud).replace(',', '.'))

        for i in range(0, len(longitud)):
            if not (str(longitud) == 'nan' or type(longitud) == type(None)):
                longitud = float(str(longitud).replace(',', '.'))
    except:
        print("Ingreso Dirección")
        pass    
    #ELIMINAR TILDES DE DIRECCIÓN Y MUNICIPIO
    if direccion is not None:
        for i in range(0, len(direccion)):
            if not str(direccion) == 'nan':
                direccion = direccion.upper()
                direccion = direccion.replace("Á", "A")
                direccion = direccion.replace("É", "E")
                direccion = direccion.replace("Í", "I")
                direccion = direccion.replace("Ó", "O")
                direccion = direccion.replace("Ú", "U")
            else:
                direccion = None


    if ciudad is not None:
        for i in range(0, len(ciudad)):
            if not (str(ciudad) == 'nan' or type(ciudad) == None):
                ciudad = ciudad.upper()
                ciudad = ciudad.replace("Á", "A")
                ciudad = ciudad.replace("É", "E")
                ciudad = ciudad.replace("Í", "I")
                ciudad = ciudad.replace("Ó", "O")
                ciudad = ciudad.replace("Ú", "U")
        
    if direccion is not None:

        #ESTANDARIZADOR
        direccion = direccion.upper()
        Carrera = ["CARRERA", "CRA", "K", "KRA", "K.", "CRA.", "KRA.", "KR.", "CR"]
        Calle = ["CLL", "CALLE", "CL.", "CLL.", "C.", "KALLE"]
        Diagonal = ["DIAGONAL", "DG.", "DIAG.", "DIAG", "D.", "DGL", "DGL."]
        Transversal = ["TRANSVERSAL", "TV.", "TR.", "T.", "TRANS.", "TRR", "T", "TRANS", "TR"]
        Avenida = ["AVENIDA", "AV.", "A.", "AVD", "AVDA"]
        AvenidaCalle = ["AV CL", "AC."]
        AvenidaCarrera = ["AK.", "AV KR"]
        Bodega = ["BODEGA", "BG.", "BOD", "BOD.", "BODEGAS", "BOEGAS", "BODG2", "BOEGA", "BD", "PLANTA"]
        Local = ["LOCAL", "LC.", "LOC", "LOCALES", "LOC."]
        Interior = ["INTERIOR", "INT", "INT.", "IN."]
        Apartamento = ["APT.", "AP.", "APARTAMENTO", "APT", "APTO", "APTO."]
        Oficina = ["OFICINA", "OF.", "OFICINAS", "CONSULTORIO", "CONSULT.", "CONSULT", "0FIC", "OFOF", "0F", "OFC", "OFC."]
        Torre = ["TORRE", "TO."]
        Lote = ["LOTE", "LOT", "LOT."]

        for i in range(0,len(direccion)):
            for j in range(0, len(Carrera)):
                if Carrera[j] in direccion.split():
                    direccion = direccion.replace(Carrera[j] + " ", "KR ")
                    break
            for j in range(0, len(Calle)):
                if Calle[j] in direccion.split():
                    direccion = direccion.replace(Calle[j] + " ", "CL ")
                    break
            if not " BIS" in direccion:
                if "BIS" in direccion:
                    direccion = direccion.replace("BIS", " BIS")
            if "ª" in direccion:
                direccion = direccion.replace("ª", "")
            if "#" in direccion.split():
                direccion = direccion.replace(" #", " ")
            elif "#" in direccion:
                direccion = direccion.replace("#", "")
            elif "NO." in direccion.split():
                direccion = direccion.replace(" NO. ", " ")
            elif "N°" in direccion.split():
                direccion = direccion.replace(" N° ", " ")
            elif "Nº" in direccion.split():
                direccion = direccion.replace(" Nº ", " ")
            elif "NO" in direccion.split():
                direccion = direccion.replace(" NO ", " ")
            elif "NO." in direccion:
                direccion = direccion.replace("NO.", "")
            elif "N°" in direccion:
                direccion = direccion.replace("N°", "")
            elif "Nº" in direccion:
                direccion = direccion.replace("Nº", "")
            if "-" in direccion.split():
                direccion = direccion.replace(" - ", " ")
            elif "-" in direccion:
                direccion = direccion.replace("-", " ")
            if "—" in direccion.split():
                direccion = direccion.replace(" — ", " ")
            elif "—" in direccion:
                direccion = direccion.replace("—", " ")
            if "−" in direccion.split():
                direccion = direccion.replace(" − ", " ")
            elif "−" in direccion:
                direccion = direccion.replace("−", " ")
            if "–" in direccion.split():
                direccion = direccion.replace(" – ", " ")
            elif "–" in direccion:
                direccion = direccion.replace("–", " ")
            for j in range(0, len(Diagonal)):
                if Diagonal[j] in direccion.split():
                    direccion = direccion.replace(Diagonal[j] + " ", "DG ")
                    break
            for j in range(0, len(Transversal)):
                if Transversal[j] in direccion.split():
                    direccion = direccion.replace(Transversal[j] + " ", "TV ")
                    break
            for j in range(0, len(Avenida)):
                if Avenida[j] in direccion.split():
                    direccion = direccion.replace(Avenida[j] + " ", "AV ")
                    break
            for j in range(0, len(Bodega)):
                if Bodega[j] in direccion.split():
                    direccion = direccion.replace(Bodega[j] + " ", "BG ")
            for j in range(0, len(Local)):
                if Local[j] in direccion.split():
                    direccion = direccion.replace(Local[j] + " ", "LC ")
            for j in range(0, len(Apartamento)):
                if Apartamento[j] in direccion.split():
                    direccion = direccion.replace(Apartamento[j] + " ", "AP ")
            for j in range(0, len(Oficina)):
                if Oficina[j] in direccion.split():
                    direccion = direccion.replace(Oficina[j] + " ", "OF ")
                elif Oficina[j] in direccion:
                    direccion = direccion.replace(Oficina[j], "OF ")
            for j in range(0, len(Torre)):
                if Torre[j] in direccion.split():
                    direccion = direccion.replace(Torre[j] + " ", "TO ")
            for j in range(0, len(Lote)):
                if Lote[j] in direccion.split():
                    direccion = direccion.replace(Lote[j] + " ", "LT ")
            for j in range(0, len(Interior)):
                if Interior[j] in direccion.split():
                    direccion = direccion.replace(Interior[j] + " ", "IN ")
                    break
            for j in range(0, len(AvenidaCalle)):
                if AvenidaCalle[j] in direccion:
                    direccion = direccion.replace(AvenidaCalle[j] + " ", "AC ")
                    break
            for j in range(0, len(AvenidaCarrera)):
                if AvenidaCarrera[j] in direccion:
                    direccion = direccion.replace(AvenidaCarrera[j] + " ", "AK ")
                    break
            if "   " in direccion:
                direccion = direccion.replace("   ", " ")
            if "  " in direccion:
                direccion = direccion.replace("  ", " ")
            if "   " in direccion:
                direccion = direccion.replace("   ", " ")
            if "  " in direccion:
                direccion = direccion.replace("  ", " ")
            if "  " in direccion:
                direccion = direccion.replace("  ", " ")
        
        #GEOLOCALIZAR DIRECCIÓN PARA OBTENER COORDENADAS

        geolocalizador_entrada = {'direccion': direccion,'ciudad': ciudad, 'f': 'json'}
        geolocalizador = 'https://www.segurosbolivar.com/arcgis/rest/services/Servicios_SB/geoEsri/GPServer/geoEsri/execute'
        geolocalizador_salida = requests.get(url=geolocalizador, headers={'content-type': 'application/json'}, params=geolocalizador_entrada)
    
        if not len(geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')) == 1:
            try:
                latitud = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[0]
                longitud = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[1]
            except:
                urlGeocode = 'http://api.lupap.co/v2/co/'
                temp = requests.get(urlGeocode + 'bogota' + '?a=' + direccion+'&key=3bee5f0a19bf31eb0fa8a70376a4c61eb34d9ba8')
                latitud = temp.json()['response']['geometry']['coordinates'][0]
                longitud = temp.json()['response']['geometry']['coordinates'][1]
    print("Coordenadas: "+str(latitud) + ", " +str(longitud))
    #BUSQUEDA Y ALMACENAMIENTO INFORMACIÓN DEL DANE
    if str(nit) == None:
        nit = 0

    sql_dane = f"""SELECT * FROM dane_2020 WHERE "NIT" = '{int(nit)}'"""
    dane = pd.read_sql(sql_dane, con) 

    sql_emis = f"""SELECT * FROM emis_0521 WHERE "n_id" = '{int(nit)}'"""
    emis = pd.read_sql(sql_emis, con) 

    razon_social = 'None'
    ciiu_dado = []
    ciiu_numero = []
    departamento_principal = 'None'
    direccion_principal = 'None'
    municipio_principal = 'None'
    telefono_principal = 'None'
    telefono2_principal = 'None'
    nombre_comercial = 'None'

    if not len(dane) == 0: 
        razon_social = dane['RAZON_SOCIAL'].iloc[0]
        nombre_comercial = None
        for i in range(0,len(dane)):
            if not str(dane['NOMBRE_COMERCIAL'].iloc[i]) == 'nan':
                nombre_comercial = dane['NOMBRE_COMERCIAL'].iloc[i]
        direccion_principal = dane['DIRECCION'].iloc[0]
        departamento_principal = dane['NOMBRE_DPTO'].iloc[0]
        municipio_principal = dane['NOMBRE_MPIO'].iloc[0]
        telefono_principal = str(int(dane['TELEFONO1'].iloc[0]))
        telefono2_principal = str(int(dane['TELEFONO1'].iloc[0]))

    def match_ciiu(self):
        for index, s in enumerate(ciiu['Unnamed: 2']):
            if str(s) == str(self) or str(s) == '0' + str(self):
                return index, s
                break
            elif str(self)[:3] == str(ciiu['Unnamed: 3'].iloc[index]) or str(self) == '0' + str(ciiu['Unnamed: 3'].iloc[index]):
                return index, ciiu['Unnamed: 1'].iloc[index]

    for i in range(0, len(dane)):
            ciiu_dado.append(ciiu['Unnamed: 3'].iloc[match_ciiu(int(dane['CIIU_ID_CIIU_4'].iloc[i]))[0]])
    for i in range(0, len(dane)):
        ciiu_numero.append(str(int(dane['CIIU_ID_CIIU_4'].iloc[i])))

    #CONSULTA SERVICIO DE MAPAS
    EntradaApiMapas = {'latitud': str(latitud), 'longitud': str(longitud), 'f': 'json'}
    ApiMapas = 'https://www.segurosbolivar.com/arcgis/rest/services/Servicios_SB/ingDigVerDos/GPServer/ingDig/execute'
    resultado_api_mapas = requests.get(url=ApiMapas, headers={'content-type': 'application/json'}, params=EntradaApiMapas)

    if resultado_api_mapas.status_code == 200:
        print('Éxitoso')
    else:
        print('Hay un error')

    #ALMACENA INFO DE MAPAS
    alpha = resultado_api_mapas.json() #alpha es el que debe variar para múltiples solicitudes
    matrizAmenazas = []
    valores = []
    try:

        if not alpha['results'][0]['value']['features'] == []:
            matrizAmenazas = [alpha['results'][0]['value']['features'][0]['attributes']['TERREMO'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['VIENTO'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['REMOCI'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['SUSTRA'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['ORDENPU'].capitalize(),
            alpha['results'][0]['value']['features'][0]['attributes']['RAYO'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['INUNDA'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['AMIT_1'].capitalize()]
    except:
        print("Error encontrando info completa mapas")
        pass

    valores.append((
        alpha['results'][0]['value']['features'][0]['attributes']['DIS_HIDRA'],
        alpha['results'][0]['value']['features'][0]['attributes']['Tipo_Espac'],
        alpha['results'][0]['value']['features'][0]['attributes']['Tipo_Mater'],
        alpha['results'][0]['value']['features'][0]['attributes']['Material'],
        alpha['results'][0]['value']['features'][0]['attributes']['Nombre_1'],
        alpha['results'][0]['value']['features'][0]['attributes']['Estación'],
        alpha['results'][0]['value']['features'][0]['attributes']['DIS_BOMBERO'],
        alpha['results'][0]['value']['features'][0]['attributes']['Dirección'],
        alpha['results'][0]['value']['features'][0]['attributes']['Teléfonos'],
        alpha['results'][0]['value']['features'][0]['attributes']['DIS_CAI'],
        alpha['results'][0]['value']['features'][0]['attributes']['Descripción'],
        alpha['results'][0]['value']['features'][0]['attributes']['Horario'],
        alpha['results'][0]['value']['features'][0]['attributes']['Direccion_Sitio'],
        alpha['results'][0]['value']['features'][0]['attributes']['Telefono'],
        alpha['results'][0]['value']['features'][0]['attributes']['Correo_Electronico'],
        alpha['results'][0]['value']['features'][0]['attributes']['DIS_POLI'],
        alpha['results'][0]['value']['features'][0]['attributes']['Descripción_1'],
        alpha['results'][0]['value']['features'][0]['attributes']['Dirección_Sitio'],
        alpha['results'][0]['value']['features'][0]['attributes']['Telefono_1'],
        alpha['results'][0]['value']['features'][0]['attributes']['Correo_Electronico_1'],                        
        alpha['results'][0]['value']['features'][0]['attributes']['Presion'],
        alpha['results'][0]['value']['features'][0]['attributes']['DIS_TRANSMI'],
        alpha['results'][0]['value']['features'][0]['attributes']['DIS_HOSPI'],
        alpha['results'][0]['value']['features'][0]['attributes']['DIS_IPS'],
        alpha['results'][0]['value']['features'][0]['attributes']['DIS_SERVI'],
        alpha['results'][0]['value']['features'][0]['attributes']['TIPO_ZI'],
        alpha['results'][0]['value']['features'][0]['attributes']['NOMBRE_ZI'],
        alpha['results'][0]['value']['features'][0]['attributes']['INUNDA'],
        alpha['results'][0]['value']['features'][0]['attributes']['amenazaEncharca']
        ))
    ConceptoManzaneo = [None]
    if not alpha["results"][0]["value"]["features"] == []:
        ConceptoManzaneo = []
        ConceptoManzaneo.append(alpha["results"][0]["value"]["features"][0]["attributes"]['PROHIB'])

    #CONSTRUYE TABLA DE AMENAZAS

    colors = ['rgb(51.0, 128.0, 0.0)', 'rgb(102.0, 128.0, 0.0)', 'rgb(128.0, 102.0, 0.0)', 'rgb(128.0, 51.0, 0.0)', 'rgb(128.0, 0.0, 0.0)']
    colors2 = n_colors('rgb(249, 249, 249)', 'rgb(179, 179, 179)', 5, colortype='rgb')
    ame = []
    for i in range(0, len(matrizAmenazas)):
        if (matrizAmenazas[i].lower() == "bajo" or matrizAmenazas[i].lower() == "baja" or matrizAmenazas[i].lower() == "baja o muy baja"):
            ame.append(0)
        elif (matrizAmenazas[i].lower() == "media baja" or matrizAmenazas[i].lower() == "medio bajo" or matrizAmenazas[i].lower() == "medio-bajo"):
            ame.append(1)
        elif (matrizAmenazas[i].lower() == "media" or matrizAmenazas[i].lower() == "medio"):
            ame.append(2)
        elif (matrizAmenazas[i].lower() == "media alta" or matrizAmenazas[i].lower() == "medio alto" or matrizAmenazas[i].lower() == "medio-alto"):
            ame.append(3)
        elif (matrizAmenazas[i].lower() == "alto" or matrizAmenazas[i].lower() == "alta"):
            ame.append(4)
        elif (matrizAmenazas[i].lower() == "sin información" or matrizAmenazas[i].lower() == "sin informacion"):
            ame.append(0)
    

    goldbach = pd.concat([pd.Series(["Terremoto", "Vientos", "Remoción en masa", "Sustracción", "Orden público", "Rayos", "Inundación", "AMIT"]), pd.Series(ame), pd.Series(matrizAmenazas)], axis=1).sort_values(by=[1],axis=0)
    goldbach = goldbach.fillna(value={1:"0"})
    goldbach[1] = goldbach[1].astype(int)

    fig = go.Figure(data=[go.Table(header=dict(align=['right','center'],values=['AMENAZA', 'NIVEL'],
                    line_color='rgb(249,249,249)', fill_color='rgb(249,249,249)',font=dict(color='black', size=10)),
                    cells=dict(align=['right','center'],values=[goldbach[0], goldbach[2]],
                    line_color=[np.array(colors2)[goldbach[1]],np.array(colors)[goldbach[1]]],
    fill_color=[np.array(colors2)[goldbach[1]],np.array(colors)[goldbach[1]]], font=dict(color=["black", "white"], size=10)))
                ])

    fig.update_layout(autosize=True, width=360.6, height=206.4, margin=dict(l=0, r=0, b=0, t=6.4, pad=4),paper_bgcolor="rgb(249,249,249)",)
    fig.write_image("/home/ingeniero_digital/principal/PLATAFORMA/plataforma_proyecto/first/static/PNG/" + str(direccion)+" "+str(ciudad) + "_tabla" + ".png", scale=2) # scale=4

    print("Consultando información interna")
    #CONSULTA INFO SINIESTROS

    siniestros = pd.read_sql(f"""SELECT * FROM siniestros_nit_0621 WHERE "NIT" = {nit}""", con) 
    if len(siniestros) == 0:
        siniestros = "No presenta."
    
    #CONSULTA ESTADO DEL CLIENTE

    ant = pd.read_excel("Archivos/ANTIGUEDADES.xlsx")
    ult = pd.read_excel("Archivos/Siniestros_Reportados.xlsx")
    vig = pd.read_excel("Archivos/vigentes.xlsx")
    for i in range (len(vig)):
        if vig.iloc[i][0] == nit:
            vigencia = "Activo"
            break
        else:
            vigencia = "Inactivo"


    for i in range (len(ant)):
        if ant.iloc[i][0] == nit:
            antiguedad = ant.iloc[i][1]
            break
    for i in range (len(ult)):
        if ult.iloc[i][0] == nit:
            ultSiniestro = ult.iloc[i][1]
            break
    try:
        ultSiniestro = str(ultSiniestro).replace("'", "").replace(" 00:00:00", "") 
    except:
        pass
    try:
        antiguedad = str(antiguedad).replace("'", "").replace(" 00:00:00", "") 
        anti = True
    except:
        anti = False
        pass
    
    try:
        variablesManzaneo =[
        alpha['results'][0]['value']['features'][0]['attributes']['SIST_EST'],
        alpha['results'][0]['value']['features'][0]['attributes']['EDAD'],
        alpha['results'][0]['value']['features'][0]['attributes']['PISOS'],
        alpha['results'][0]['value']['features'][0]['attributes']['SOTANOS'],
        alpha['results'][0]['value']['features'][0]['attributes']['PENDIENTE'],
        alpha['results'][0]['value']['features'][0]['attributes']['NIVEL_VIA_TERR'],
        alpha['results'][0]['value']['features'][0]['attributes']['VIAS'],
        alpha['results'][0]['value']['features'][0]['attributes']['ALCANTARILLADO'],
        alpha['results'][0]['value']['features'][0]['attributes']['RESIDUOS'],
        alpha['results'][0]['value']['features'][0]['attributes']['CANALES_RIOS'],
        str(alpha['results'][0]['value']['features'][0]['attributes']['NIVEL_RIO_TERR']),
        str(alpha['results'][0]['value']['features'][0]['attributes']['EST_PROTEC_INUND']),
        alpha['results'][0]['value']['features'][0]['attributes']['RED_ELECTRICA'],
        alpha['results'][0]['value']['features'][0]['attributes']['PARARRAYOS'],
        alpha['results'][0]['value']['features'][0]['attributes']['ACT_INCENDIO'],
        alpha['results'][0]['value']['features'][0]['attributes']['HIDRANTES'],
        alpha['results'][0]['value']['features'][0]['attributes']['COMERCIO_VIA_PUB'],
        alpha['results'][0]['value']['features'][0]['attributes']['ZONA_ESPARCIMIENTO'],
        alpha['results'][0]['value']['features'][0]['attributes']['COMERCIO_INFORMAL'],
        alpha['results'][0]['value']['features'][0]['attributes']['RECICLADORES'],
        alpha['results'][0]['value']['features'][0]['attributes']['HABITANTE_CALLE'],
        alpha['results'][0]['value']['features'][0]['attributes']['PREDIO_DESHAB'], 
        alpha['results'][0]['value']['features'][0]['attributes']['VIGILANCIA'], 
        alpha['results'][0]['value']['features'][0]['attributes']['ALARMAS'], 
        alpha['results'][0]['value']['features'][0]['attributes']['CAMARAS'],
        alpha['results'][0]['value']['features'][0]['attributes']['ALUMBRADO'],
        alpha['results'][0]['value']['features'][0]['attributes']['ILUMINACION'],
        alpha['results'][0]['value']['features'][0]['attributes']['NOMBRE_ZI'],
        alpha['results'][0]['value']['features'][0]['attributes']['TIPO_ZI'],
        ]
    except:
        variablesManzaneo =[
        alpha['results'][0]['value']['features'][0]['attributes']['SIST_EST'],
        alpha['results'][0]['value']['features'][0]['attributes']['EDAD'],
        alpha['results'][0]['value']['features'][0]['attributes']['PISOS'],
        alpha['results'][0]['value']['features'][0]['attributes']['SOTANOS'],
        alpha['results'][0]['value']['features'][0]['attributes']['PENDIENTE'],
        alpha['results'][0]['value']['features'][0]['attributes']['NIVEL_VIA_TERR'],
        alpha['results'][0]['value']['features'][0]['attributes']['VIAS'],
        alpha['results'][0]['value']['features'][0]['attributes']['ALCANTARILLADO'],
        alpha['results'][0]['value']['features'][0]['attributes']['RESIDUOS'],
        alpha['results'][0]['value']['features'][0]['attributes']['CANALES_RIOS'],
        str(alpha['results'][0]['value']['features'][0]['attributes']['NIVEL_RIO_TERR']),
        str(alpha['results'][0]['value']['features'][0]['attributes']['EST_PROTEC_INUND']),
        alpha['results'][0]['value']['features'][0]['attributes']['RED_ELECTRICA'],
        alpha['results'][0]['value']['features'][0]['attributes']['PARARRAYOS'],
        alpha['results'][0]['value']['features'][0]['attributes']['ACT_INCENDIO'],
        alpha['results'][0]['value']['features'][0]['attributes']['HIDRANTES'],
        alpha['results'][0]['value']['features'][0]['attributes']['COMERCIO_VIA_PUB'],
        alpha['results'][0]['value']['features'][0]['attributes']['ZONA_ESPARCIMIENTO'],
        alpha['results'][0]['value']['features'][0]['attributes']['COMERCIO_INFORMAL'],
        alpha['results'][0]['value']['features'][0]['attributes']['RECICLADORES'],
        alpha['results'][0]['value']['features'][0]['attributes']['HABITANTE_CALLE'],
        alpha['results'][0]['value']['features'][0]['attributes']['PREDIO_DESHAB'], 
        alpha['results'][0]['value']['features'][0]['attributes']['VIGILANCIA'], 
        alpha['results'][0]['value']['features'][0]['attributes']['ALARMAS'], 
        alpha['results'][0]['value']['features'][0]['attributes']['CAMARAS'],
        alpha['results'][0]['value']['features'][0]['attributes']['ALUMBRADO'],
        alpha['results'][0]['value']['features'][0]['attributes']['ILUMINACION']
        ]
    for i in range(0, len(variablesManzaneo)):
        if variablesManzaneo[i] == "None":
            variablesManzaneo[i] = "NO APLICA"
    print("Las variables almacenadas de manzaneo fueron: " +str(len(variablesManzaneo)))
    
    #CALCULA NIVELES DE RIESGO
    calPro = pd.read_excel("Archivos/Calificacion propiedad.xlsx")
    eval = pd.read_excel("Archivos/Evaluacion variables.xlsx")
    print("Calculando niveles de riesgo")
    nombreManzaneo = ["SIST_EST", "EDAD", "PISOS", "SOTANOS", "PENDIENTE", "NIVEL_VIA_TERR", "VIAS", "ALCANTARILLADO", "RESIDUOS", "CANALES_RIOS", "NIVEL_RIO_TERR","EST_PROTEC_INUND", "RED_ELECTRICA", "PARARRAYOS", "ACT_INCENDIO", "HIDRANTES", "COMERCIO_VIA_PUB", "ZONA_ESPARCIMIENTO", "COMERCIO_INFORMAL", "RECICLADORES","HABITANTE_CALLE", "PREDIO_DESHAB", "VIGILANCIA", "ALARMAS", "CAMARAS", "ALUMBRADO", "ILUMINACION"]
    RCON1 = ["<1985", "MENOR A 1985"]
    RCON2 = ["1985 A 1997", "1985 Y 1997"]
    RCON3 = ["1998 A 2010", "1998 Y 2010"]
    RCON4 = [">2010", "MAYOR A 2010"]

    for j in range(0, len(RCON1)):
        if RCON1[j] == variablesManzaneo[1]:
            variablesManzaneo[1] = variablesManzaneo[1].replace(RCON1[j], "PREVIO A 1985")
            break
    for j in range(0, len(RCON2)):
        if RCON2[j] == variablesManzaneo[1]:
            variablesManzaneo[1] = variablesManzaneo[1].replace(RCON2[j], "ENTRE 1985 Y 1997")
            break    
    for j in range(0, len(RCON3)):
        if RCON3[j] == variablesManzaneo[1]:
            variablesManzaneo[1] = variablesManzaneo[1].replace(RCON3[j], "ENTRE 1998 Y 2010")
            break
    for j in range(0, len(RCON4)):
        if RCON4[j] == variablesManzaneo[1]:
            variablesManzaneo[1] = variablesManzaneo[1].replace(RCON4[j], "POSTERIOR A 2010")
            break
        
    for i in range(0, len(variablesManzaneo)):
        variablesManzaneo[i] = variablesManzaneo[i].upper()
        variablesManzaneo[i] = variablesManzaneo[i].replace("Á", "A")
        variablesManzaneo[i] = variablesManzaneo[i].replace("É", "E")
        variablesManzaneo[i] = variablesManzaneo[i].replace("Í", "I")
        variablesManzaneo[i] = variablesManzaneo[i].replace("Ó", "O")
        variablesManzaneo[i] = variablesManzaneo[i].replace("Ú", "U")

    amenazaTerr = 0
    amenazaAgua = 0
    amenazaRM = 0
    amenazaInc = 0
    amenazaSust = 0
    vulneTerr = 0
    vulneAgua = 0
    vulneRM = 0
    vulneInc = 0
    vulneSust = 0
    puntajesManzaneo = []
    a = 0
    for i in range(0, len(eval)):
        for j in range(0, len(nombreManzaneo)):
            if eval.iloc[i][0] == nombreManzaneo[j] and eval.iloc[i][1] == variablesManzaneo[j]:
                a = a + 1
                puntajesManzaneo.append(eval.iloc[i][2])
                #AMENZAS
                if eval.iloc[i][4] == "TERREMOTO" and eval.iloc[i][3] == "AMENAZA":
                    amenazaTerr = amenazaTerr + eval.iloc[i][2]
                if eval.iloc[i][4] == "DAÑOS POR AGUA" and eval.iloc[i][3] == "AMENAZA":
                    amenazaAgua = amenazaAgua + eval.iloc[i][2]
                if eval.iloc[i][4] == "RM Y EE" and eval.iloc[i][3] == "AMENAZA":
                    amenazaRM = amenazaRM + eval.iloc[i][2]
                if eval.iloc[i][4] == "INCENDIO" and eval.iloc[i][3] == "AMENAZA":
                    amenazaInc = amenazaInc + eval.iloc[i][2]
                if eval.iloc[i][4] == "SUSTRACCION" and eval.iloc[i][3] == "AMENAZA":
                    amenazaSust = amenazaSust + eval.iloc[i][2]
                    
                #VULNERABILIDADES
                if eval.iloc[i][4] == "TERREMOTO" and eval.iloc[i][3] == "VULNERABILIDAD":
                    vulneTerr = vulneTerr + eval.iloc[i][2]
                if eval.iloc[i][4] == "DAÑOS POR AGUA" and eval.iloc[i][3] == "VULNERABILIDAD":
                    vulneAgua = vulneAgua + eval.iloc[i][2]
                if eval.iloc[i][4] == "RM Y EE" and eval.iloc[i][3] == "VULNERABILIDAD":
                    vulneRM = vulneRM + eval.iloc[i][2]
                if eval.iloc[i][4] == "INCENDIO" and eval.iloc[i][3] == "VULNERABILIDAD":
                    vulneInc = vulneInc + eval.iloc[i][2]
                if eval.iloc[i][4] == "SUSTRACCION" and eval.iloc[i][3] == "VULNERABILIDAD":
                    vulneSust = vulneSust + eval.iloc[i][2]
    print("Las variables almacenadas en puntajes manzaneo son= " +str(len(puntajesManzaneo)))

    print(str(puntajesManzaneo))
    ## REVISAR LINEA PARA ACTIVIDADES ECONOMICAS

    evalPro = 0
    for i in range(0, len(calPro)):
        if int(ciiu_numero[0]) == calPro.iloc[i][1]:
            evalPro = calPro.iloc[i][5]
            break
        else: 
            evalPro = 3

    amenazaTerr = amenazaTerr * evalPro
    amenazaAgua = amenazaAgua * evalPro
    amenazaRM = amenazaRM  * evalPro
    amenazaInc = amenazaInc * evalPro
    amenazaSust = amenazaSust * evalPro

    vulneTerr = vulneTerr * evalPro
    vulneAgua = vulneAgua * evalPro
    vulneRM = vulneRM * evalPro
    vulneInc = vulneInc * evalPro
    vulneSust = vulneSust * evalPro

    terremoto = amenazaTerr * vulneTerr
    agua = amenazaAgua * vulneAgua
    Rm = amenazaRM * vulneRM
    incendio = amenazaInc * vulneInc
    sustraccion = amenazaSust * vulneSust 
    cateARCI = pd.read_excel("Archivos/Categorias ARCI.xlsx")
    for i in reversed(range(1,6)):
        if terremoto >= cateARCI.iloc[i][3] and terremoto <= cateARCI.iloc[i][4]:
            Rterremoto = cateARCI.iloc[i][1]
            Nterremoto = cateARCI.iloc[i][0]
    for i in reversed(range(8,13)):
        if sustraccion >= cateARCI.iloc[i][3] and sustraccion <= cateARCI.iloc[i][4]:
            Rsustraccion = cateARCI.iloc[i][1]
            Nsustraccion = cateARCI.iloc[i][0]

    for i in reversed(range(15,20)):
        if Rm >= cateARCI.iloc[i][3] and Rm <= cateARCI.iloc[i][4]:
            RRm = cateARCI.iloc[i][1]
            NRm = cateARCI.iloc[i][0]

    for i in reversed(range(22,27)):
        if incendio >= cateARCI.iloc[i][3] and incendio <= cateARCI.iloc[i][4]:
            Rincendio = cateARCI.iloc[i][1]
            Nincendio = cateARCI.iloc[i][0]

    for i in reversed(range(29,34)):
        if agua >= cateARCI.iloc[i][3] and agua <= cateARCI.iloc[i][4]:
            Ragua = cateARCI.iloc[i][1]
            Nagua = cateARCI.iloc[i][0]


    #EXCLUSIONES PARRA JUSTIFICACIONES
    if variablesManzaneo[16] == "NO APLICA":
        via = ""
    else:
        via = "Se trata de un predio que "+ variablesManzaneo[16] + " tiene acceso en via publica" 
    if variablesManzaneo[17] == "NO APLICA":
        espar = ""
    if variablesManzaneo[17] == "TODAS LAS ANTERIORES":
        espar = "cuenta con bares, discotecas, billares, casinos y/o moteles a sus alrededores"
    else:
        espar = "No cuenta con zonas de esparcimiento a sus alrededores"
    if variablesManzaneo[22] == "NO HAY":
        vigi = "no cuenta con ningun servicio de vigilancia privada"
    else:
        vigi = "cuenta con servicio vigilancia " + variablesManzaneo[22] 
    if variablesManzaneo[25] == "NO TIENE":
        alu = "No existe alumbrado publico en la zona"
    else:
        alu = "Existe alumbrado publico en la zona en " + variablesManzaneo[25]
    if variablesManzaneo[26] == "NO TIENE":
        ilu = "Los predios en la zona no cuentan con iluminación privada"
    else:
        ilu = "Los predios en la zona cuentan con una iluminacion privada "+ variablesManzaneo[26]
    
    if variablesManzaneo[6] == "SIN PAVIMENTO":
        vi =  "las vias no se encuentran pavimentadas"
    else:
        vi = "las vias presentan " + variablesManzaneo[6] 
    if variablesManzaneo[7] == "INEXISTENTE":
        alca = "la zona no cuenta con ningun tipo de alcantarillado"
    else:
        alca = "La zona cuenta con un alcantarillado "+variablesManzaneo[7]
    if variablesManzaneo[10] == "NO APLICA":
        fuh = " no se encuentran fuentes hidircas cercanas"
    else:
        fuh = " encuentra una " + variablesManzaneo[10]+ ", esta fuente hidirca se situa " + variablesManzaneo[11] + "del terreno del predio; asi mismo la fuente cuenta con estructuras de protección "+ variablesManzaneo[12]
        
    if variablesManzaneo[12] == "INEXISTENTES":
        red = "No presenta una red electrica"
    else:
        red = "presenta una red electrica " +variablesManzaneo[12] 
    if variablesManzaneo[13] == "NO HAY":
        para = "no cuenta con pararrayos"
    else:
        para = "cuenta con parrarrayos de tipo " + variablesManzaneo[13]

    if variablesManzaneo[14] == "NO APLICA":
        actI = "no cuenta con presencia de negocios de alta azarosidad que afecten el riesgo de incendio"
        fabr = ""
    if variablesManzaneo[14] == "TODAS O VARIAS":
        actI = "cuenta con presencia de negocios de alta azarosidad que afecten el riesgo de incendio tales como"
        fabr = "fabrica y/o almacenamiento de pintura, espumados, colchones, farmacos y quimicos"
    if variablesManzaneo[14] != "TODAS O VARIAS" and variablesManzaneo[14] != "NO APLICA":
        actI = "cuenta con presencia de negocios de alta azarosidad que afecten el riesgo de incendio tales como"
        fabr = variablesManzaneo[14]

    ## REVISAR EL PROBLEMA DE CALIFICACIÓN DE PROPIEDAD
    if evalPro == 1:
        riesgoActi = "Bajo"
    if evalPro == 2:
        riesgoActi = "Medio Bajo"
    if evalPro == 3:
        riesgoActi = "Medio"
    if evalPro == 4:
        riesgoActi = "Medio Alto"
    if evalPro == 5:
        riesgoActi = "Alto"

    #CADENAS DE TEXTO DE CALIFICACIONES
    jusSustraccion = str(via+ espar + ", se evidencia que " +variablesManzaneo[18]+" tiene comercio informal marcado, " +variablesManzaneo[19]
                + " existe presencia de recilcadores y habitantes de calle en las zonas cercanas, asi mismo "+ variablesManzaneo[21]
                +" se evidencian predios deshabitados cercanos. En cuanto a la evaluación de vulnerabilidad de la zona, se registra que "+ vigi
                + ", "+ variablesManzaneo[23]+ " tiene sistema de alarmas y "+ variablesManzaneo[24]+ " tiene camaras. "+ alu +" " +ilu 
                + ". Se considera que para la cobertura de sustracción el riesgo es "+ Rsustraccion + ".")

    jusTerremoto = str("Se trata de predios con altura maxima de "+ variablesManzaneo[2]+ " pisos, un rango de edad de construcción "+variablesManzaneo[1]
                + " y un sistema estructural de "+variablesManzaneo[0]+ ", ademas  se registra que "+ variablesManzaneo[3]
                + " puede contar con sotanos.  Se considera que para la cobertura de terremoto el riesgo es "+ Rterremoto)               

    jusAgua = str("El predio se encuentra en un terreno con pendiente "+variablesManzaneo[4]+ ", el nivel de las vias contiguas se encuentran " +variablesManzaneo[5]+ ", " +vi
        + ". Ademas "+ alca+ " y "+variablesManzaneo[8]+ " presenta acumulación de residuos. En los alrededores del predio "+ fuh 
        + ". Se considera que para la cobertura de daños por agua el riesgo es "+ Ragua)

    jusRm = str("La zona " +red+ " y " + para+ ". Se considera que para la cobertura de maquinaria y equipo electronica el riesgo es " + RRm)

    justIncendio = str("La zona " +actI+ fabr+ ", ademas esta zona "+ variablesManzaneo[15]+ " cuenta con hidrantes. Se considera que para el riesgo de incendio el riesgo es  "+ Rincendio)

    calActi = str("La actividad principal desarrollada por " +razon_social+ " corresponde a  "+ str(ciiu_dado[0])
            + ". Teniendo en cuenta las politicas de ingenieria, esta actividad representa un riesgo " + riesgoActi
            + " Esta calificación afectara la evaluación de riesgos de cada cobertura.")

    print("Generando anexos")
    #GENERACION ANEXOS (API´S GMP)
    import urllib

    f = open('/home/ingeniero_digital/principal/PLATAFORMA/plataforma_proyecto/biblioteca_modelos/AR Complejos Industriales/Vecinos Fotos/Satelite'+str(nit)+'.png','wb')
    f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/staticmap?center='+str(latitud)+','+str(longitud)+'&zoom=18&size=600x600&markers=color:red%7Clabel:%7C'+str(latitud)+','+str(longitud)+'&maptype=satellite&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
    f.close()
    f = open('/home/ingeniero_digital/principal/PLATAFORMA/plataforma_proyecto/biblioteca_modelos/AR Complejos Industriales/Vecinos Fotos/Roadmap'+str(nit)+'.png','wb')
    f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/staticmap?center='+str(latitud)+','+str(longitud)+'&zoom=18&size=600x600&markers=color:red%7Clabel:%7C'+str(latitud)+','+str(longitud)+'&maptype=roadmap&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
    f.close()
  
    try:
        nearby = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+str(latitud)+','+str(longitud)+'&radius=50&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc')
        near = nearby.json()

        vecinos = []
        for i in range (0, len(near['results'])):
            try:
                vecinos.append([near['results'][i]['name'], " - " , near['results'][i]['vicinity'], " - " , near['results'][i]['types'][0], " - ", near['results'][i]['photos'][0]['photo_reference']])
                pass
            except: 
                vecinos.append([near['results'][i]['name'], " - " , near['results'][i]['vicinity'], " - " , near['results'][i]['types'][0], " - ", " "])

        a= 0
        photos = []
        nombres = []
        tipos = []
        for i in range (0, len(near['results'])):
            try:
                if vecinos[i][6] != " ":
                    photos.append(vecinos[i][6])
                    tipos.append(vecinos[i][4])
                    nombres.append(vecinos[i][0])

            except:
                pass
        
        for i in range(0, len(photos)):
            
            f = open('/home/ingeniero_digital/principal/PLATAFORMA/plataforma_proyecto/biblioteca_modelos/AR Complejos Industriales/Vecinos Fotos/'+str(nit)+str(i)+'.jpeg','wb')
            f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference='+ str(photos[i]) +'&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
            f.close()

    except:
        pass

    print("Creando pdf")
    # GENERACIÓN DEL PDF

    pdf=FPDF(format='letter', unit='in')
    pdf.add_page()
        
    # Estableces fuente del texto
    pdf.set_font('Times','',10.0) 
    # Text height is the same as current font size
    th = pdf.font_size
    ac = 0.25
    # Effective page width
    epw = pdf.w - 2 * pdf.l_margin

    #PAGINA INTRODUCCIÓN
    pdf.image(r'/home/ingeniero_digital/principal/Archivos Informe/Logo.jpg', x =2.8, y = pdf.get_y(), w = 3, h = 3)
    pdf.set_font('Times','B', 18.0) 
    pdf.ln(ac*15)
    pdf.cell(epw, 2, "INFORME DE", align = 'C')
    pdf.ln(ac)
    pdf.cell(epw, 2, "EVALUACIÓN DE RIESGOS", align = 'C')
    pdf.ln(ac*2)
    try:
        pdf.cell(epw, 2, str(variablesManzaneo[28]), align = 'C')
        pdf.ln(ac)
        pdf.cell(epw, 2, str(variablesManzaneo[27]), align = 'C')
        pdf.ln(ac*2)
    except:
        pass
    pdf.cell(epw, 2, razon_social, align = 'C')   
    pdf.ln(ac*7)
    pdf.set_font('Times','', 12.0) 
    pdf.cell(epw, 2, "ADMINISTRACIÓN DE RIESGOS DE COMPLEJOS INDUSTRIALES(ARCI)", align = 'C')
    pdf.ln(ac*2)
    pdf.cell(epw, 2, "Fecha de realización:", align = 'C')
    pdf.ln(ac)
    now = datetime.now()
            
    pdf.cell(epw, 2, str(now.date()), align = 'C')
            
    pdf.add_page()

    # 1 - INFORMACIÓN PERSONAL
    informacionGeneral = [['Nombre Tomador / Asegurado', razon_social],
    ['NIT', nit],
    ['Actividad Económica', str(ciiu_numero).replace("'", "")],
    ['Valor a asegurar', "0"],
    ['Dirección', direccion],
    ['Ciudad', ciudad], 
    ['Telefono', telefono_principal]]

    pdf.set_font('Times','B', 14.0) 
    pdf.cell(epw, 0.0, '1 - INFORMACIÓN GENERAL', align='C')
    pdf.set_font('Times','',10.0) 
    pdf.ln(0.3)
        
    for row in informacionGeneral:
        for i in row:
            pdf.cell(epw/2, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)

    pdf.ln(0.5)

    # 2 - ENTORNO
    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, 'COORDENADAS', align='C', border = 1)
    pdf.ln(ac)
    pdf.set_font('Times','',10.0) 

    coordenadas = [['Departamento', departamento],
    ['Municipio', ciudad],  
    ['Latitud', latitud],
    ['Longitud', longitud]]

    for row in coordenadas:
        for i in row:
            pdf.cell(epw/2, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)

    # 3 - CUADRO DE AMENAZAS
    pdf.ln(ac)

    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, '2 - CUADRO DE AMENAZAS (MAPAS)', align='C')
    pdf.ln(0.3)
    pdf.cell(epw, 4, '', align='C', border = 1)

    pdf.ln(4)
    pdf.image(r'Archivos/PNG/ID_AR/' + str(direccion) +" "+ str(ciudad)+"_tabla" + ".png", x =1.5, y = 5, w = 5.3, h = 3.5)
    pdf.set_font('Times', 'B', 12.0)
    pdf.cell(epw, ac, "CALIFICACIÓN ACTIVIDAD ECONOMICA", border=1, align='C')
    pdf.ln(ac)
    pdf.set_font('Times', '', 10.0)
    var = 1
    var = round(len(calActi) / 120) + 1
    pdf.cell(epw, ac*var, '', align='C', border=1)
    pdf.ln(ac/8)
    a = 0
    b = 120
    for i in range(var):
        text = calActi[a:b]
        a = a + 120
        b = b + 120
        pdf.cell(epw, ac, text, border=0, align='C')
        pdf.ln(ac)


    #MODELOS DE RIEGO
    pdf.add_page()
    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(epw, ac, "3 - MODELOS DE RIESGO", border=0, align='C')
    pdf.ln(ac*2)
    pdf.cell(epw/1.333, ac, "SUSTRACCIÓN", border=1, align='C')
    y = pdf.get_y()
    pdf.ln(ac)
    pdf.set_font('Times', '', 10.0)
    encabezado = [["VARIABLE"],["RESPUESTA"],["PUNTAJE"]]

    for row in encabezado:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align = 'C') 
    pdf.ln(ac)
    print(variablesManzaneo)
    print(variablesManzaneo[24])
    manEE = [['Comercio via', variablesManzaneo[16], puntajesManzaneo[16]],
    ['Zonas de esparcimiento',variablesManzaneo[17], puntajesManzaneo[17]],
    ['Comercio informal',variablesManzaneo[18], puntajesManzaneo[18]],
    ['Recicladores',variablesManzaneo[19], puntajesManzaneo[19]],
    ['Habitantes de calle',variablesManzaneo[20], puntajesManzaneo[20]],
    ['Predios deshabitados',variablesManzaneo[21], puntajesManzaneo[21]],
    ['Vigiliancia',variablesManzaneo[22], puntajesManzaneo[22]],
    ['Alarmas',variablesManzaneo[23], puntajesManzaneo[23]],
    ['Camaras',variablesManzaneo[24], puntajesManzaneo[24]],
    ['Alumbrado',variablesManzaneo[25], puntajesManzaneo[25]],
    ['Iluminación',variablesManzaneo[26], puntajesManzaneo[26]]]

    for row in manEE:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)

    #Imprimir justificacion
    var = 1
    var = round(len(jusSustraccion) / 120) + 1
    pdf.cell(epw, ac*var, '', align='C', border=1)
    pdf.ln(ac/8)
    a = 0
    b = 120
    for i in range(var):
        text = jusSustraccion[a:b]
        a = a + 120
        b = b + 120
        pdf.cell(epw, ac, text, border=0, align='C')
        pdf.ln(ac)

    #
    pdf.ln(ac)
    pdf.set_font('Times', 'B', 12.0)
    pdf.cell(epw/1.333, ac, "DAÑOS POR AGUA", border=1, align='C')
    y = pdf.get_y()
    pdf.ln(ac)
    pdf.set_font('Times', '', 10.0)

    for row in encabezado:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align = 'C') 
    pdf.ln(ac)

    manAgua = [['Pendiente', variablesManzaneo[4], puntajesManzaneo[4]],
    ['Nivel via',variablesManzaneo[5], puntajesManzaneo[5]],
    ['Vias', variablesManzaneo[6], puntajesManzaneo[6]],
    ['Alcantarillado', variablesManzaneo[7], puntajesManzaneo[7]],
    ['Residuos', variablesManzaneo[8], puntajesManzaneo[8]],
    ['Canales de los rios', variablesManzaneo[9], puntajesManzaneo[9]],
    ['Nivel rio', variablesManzaneo[10], puntajesManzaneo[10]],
    ['Estructuras Protección', variablesManzaneo[11], puntajesManzaneo[11]]]
    for row in manAgua:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)

    #Imprimir justificacion
    var = 1
    var = round(len(jusAgua) / 120) + 1
    pdf.cell(epw, ac*var, '', align='C', border=1)
    pdf.ln(ac/8)
    a = 0
    b = 120
    for i in range(var):
        text = jusAgua[a:b]
        a = a + 120
        b = b + 120
        pdf.cell(epw, ac, text, border=0, align='C')
        pdf.ln(ac)

    pdf.image(r'Archivos/'+str(Nsustraccion)+".PNG", x = epw/1.22, y = 1.5 +ac*2 , w = ac*8, h = ac*5)
    pdf.image(r'Archivos/'+str(Nagua)+".PNG", x = epw/1.22, y = 6.5 +ac*2 , w = ac*8, h = ac*5)

    pdf.add_page()
    pdf.set_font('Times', 'B', 12.0)
    pdf.cell(epw/1.333, ac, "TERREMOTO", border=1, align='C')
    y = pdf.get_y()
    pdf.ln(ac)
    pdf.set_font('Times', '', 10.0)


    for row in encabezado:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align = 'C') 
    pdf.ln(ac)

    manTerremoto = [['Sistema estructural', variablesManzaneo[0], puntajesManzaneo[0]],
    ['Edad de construcción',variablesManzaneo[1], puntajesManzaneo[1]],
    ['Numero de pisos', variablesManzaneo[2], puntajesManzaneo[2]],
    ['Sotanos', variablesManzaneo[3], puntajesManzaneo[3]]]

    for row in manTerremoto:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)

    #Imprimir justificacion
    pdf.ln(ac)
    var = 1
    var = round(len(jusTerremoto) / 120) + 1
    pdf.cell(epw, ac*var, '', align='C', border=1)
    pdf.ln(ac/8)
    a = 0
    b = 120
    for i in range(var):
        text = jusTerremoto[a:b]
        a = a + 120
        b = b + 120
        pdf.cell(epw, ac, text, border=0, align='C')
        pdf.ln(ac)

    pdf.ln(ac*2)
    pdf.set_font('Times', 'B', 12.0)
    pdf.cell(epw/1.333, ac, "RM Y EE", border=1, align='C')
    y = pdf.get_y()
    pdf.ln(ac)
    pdf.set_font('Times', '', 10.0)

    for row in encabezado:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align = 'C') 
    pdf.ln(ac)

    manEE = [['Red electica', variablesManzaneo[12], puntajesManzaneo[12]],
    ['Pararrayos',variablesManzaneo[13], puntajesManzaneo[13]]]

    for row in manEE:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)
    #Imprimir justificacion
    pdf.ln(ac)
    var = 1
    var = round(len(jusRm) / 120) + 1
    pdf.cell(epw, ac*var, '', align='C', border=1)
    pdf.ln(ac/8)
    a = 0
    b = 120
    for i in range(var):
        text = jusRm[a:b]
        a = a + 120
        b = b + 120
        pdf.cell(epw, ac, text, border=0, align='C')
        pdf.ln(ac)

    pdf.ln(ac*2)
    pdf.set_font('Times', 'B', 12.0)
    pdf.cell(epw/1.333, ac, "INCENDIO", border=1, align='C')
    y = pdf.get_y()
    pdf.ln(ac)
    pdf.set_font('Times', '', 10.0)

    for row in encabezado:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align = 'C') 
    pdf.ln(ac)

    manIncendio = [['Act incendio', variablesManzaneo[14], puntajesManzaneo[14]],
    ['Hidrantes',variablesManzaneo[15], puntajesManzaneo[15]]]

    for row in manIncendio:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)

    #Imprimir justificacion
    pdf.ln(ac)
    var = 1
    var = round(len(justIncendio) / 120) + 1
    pdf.cell(epw, ac*var, '', align='C', border=1)
    pdf.ln(ac/8)
    a = 0
    b = 120
    for i in range(var):
        text = justIncendio[a:b]
        a = a + 120
        b = b + 120
        pdf.cell(epw, ac, text, border=0, align='C')
        pdf.ln(ac)

    pdf.image(r'Archivos/'+str(Nterremoto)+".PNG", x = epw/1.22, y = 0.1 +ac*2 , w = ac*8, h = ac*5)
    pdf.image(r'Archivos/'+str(NRm)+".PNG", x = epw/1.22, y = 2.8 +ac*2   , w = ac*8, h = ac*5)
    pdf.image(r'Archivos/'+str(Nincendio)+".PNG", x = epw/1.22, y = 5.1 +ac*2 , w = ac*8, h = ac*5)
    # DESCRIPCION ACTIVIDAD ECONOMICA
    pdf.add_page()
    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(epw, ac, "4 - INFORMACIÓN EMPRESARIAL", border=0, align='C')
    pdf.ln(ac*2)
    try:
        pdf.set_font('Times', 'B', 12.0)
        pdf.cell(epw, ac, "DESCRIPCIÓN SEGÚN ACTIVIDAD ECONOMICA (DANE)", border=1, align='C')
        pdf.set_font('Times', '', 10.0)
        if len(ciiu_numero)>0:
            pdf.ln(ac)
            pdf.cell(epw, ac*(len(ciiu_numero)+1), "", border = 1, align='C')
            for i in range(0,len(ciiu_dado)):
                pdf.ln(ac)
                pdf.cell(epw, ac, str(ciiu_numero[i])+ ": " + str(ciiu_dado[i]), border=0, align='C')
        pdf.ln(ac)
    except:
        pass


    #EMIS
    pdf.ln(ac)
    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "EMIS", border=1, align = 'C') 
    pdf.set_font('Times','',10.0) 
    locale.setlocale( locale.LC_ALL, '' )
    if len(emis != 0):
        empleados = int(emis['num_empleados'].values[0])
        ingresos = float(emis['ingresos_totales_ult_ano_usd'].values[0])

        vEmis = [['Fecha de Actualización', str(emis['fecha_actualizacion'].values[0]).replace("00:00:00 UTC", " ")],
        ['Estatus de la compañia', emis['estatus'].values[0]],
        ['Numero de empleados', emis['num_empleados'].values[0]],
        ['Tipo de compañia', emis['tipo_compania'].values[0]],
        ['Ingresos totales del ultimo año (USD)', emis['ingresos_totales_ult_ano_usd'].values[0]],
        ['Moneda capital del mercado', emis['moneda_capital_mercado'].values[0]],
        ['Año de ingresos totales', emis['ano_ingresos_totales'].values[0]]]
                
        for row in vEmis:
            pdf.ln(ac)
            for i in row:
                pdf.cell(epw/2, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)
        pdf.set_font('Times','B',12.0) 
        pdf.cell(epw, ac, "DESCRIPCIÓN SEGUN EMIS", border=1, align = 'C') 
        pdf.set_font('Times','',10.0) 
        pdf.ln(ac)
        var = 1
        if len(emis['descripcion'].values[0]) > 120:
            var = round(len(emis['descripcion'].values[0]) / 120) + 1
        pdf.cell(epw, ac*var , '', align='C', border = 1)
        pdf.ln(ac/8)
        a = 0
        b = 120
        for i in range(var):
            text = emis['descripcion'].values[0][a:b]
            a = a +120
            b = b +120
            pdf.cell(epw, ac, text, border=0, align = 'C')
            pdf.ln(ac) 
        pdf.ln(ac) 

    else:
        empleados = None
        ingresos = None
        pdf.ln(ac)
        pdf.cell(epw, ac, "SIN INFORMACIÓN", border=1, align = 'C')
        pdf.ln(ac)

    #SINIESTROS
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, "5 - SINIESTROS", border=0, align = 'C') 
    pdf.ln(ac*2)

    tituloSiniestros = [["#"],["NOMBRE COBERTURA"],["SINIESTROS HISTORICOS"],["POLIZAS HISTORICAS"]]
    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "HISTORICO DE SINIESTROS", border=1, align = 'C') 
    pdf.set_font('Times','',8.0) 
    pdf.ln(ac)

    if type(siniestros) is not str:
        for row in tituloSiniestros:
            for i in row:
                pdf.set_font('Times','B',8.0) 
                if i == "NOMBRE COBERTURA":
                    pdf.set_xy((epw/5)+pdf.l_margin, pdf.l_margin+(ac*25.13))
                    pdf.cell(epw/2.5, ac, str(i), border=1, align = 'C') 
                else:
                    pdf.cell(epw/5, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)
            
        for i in range (len(siniestros)):
            pdf.multi_cell(epw/5 , ac, str(i+1), border = 1, align = 'C')

        y = 26.13
        for i in siniestros['NOMBRE_COBERTURA']:
            pdf.set_font('Times', '',8.0) 
            pdf.set_xy((epw/5)+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/2.5 , ac, str(i), border = 1, align = 'C')
            y = y+1

        y = 26.13
        for i in siniestros['CANTIDAD_SINIESTROS']:
            pdf.set_xy((epw/5)*3+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/5 , ac, str(i), border = 1, align = 'C')
            y = y+1
            
        y = 26.13
        for i in siniestros['CANTIDAD_POLIZAS']:
            pdf.set_xy((epw/5)*4+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/5 , ac, str(i), border = 1, align = 'C')
            y = y+1
        pdf.cell(epw, ac, "LA FECHA DEL ULTIMO SINIESTRO FUE EL "+ ultSiniestro, border=1, align = 'C')
        pdf.ln(ac)
    else:
        pdf.cell(epw, ac, "NO HA PRESENTADO SINIESTROS", border=1, align = 'C')
        pdf.ln(ac)
    pdf.set_font('Times','B',10.0) 
    pdf.cell(epw, ac, "Usuario " +vigencia+ " dentro de la compañia." , border=1, align = 'C')
    pdf.ln(ac)
    if anti == True:
        pdf.set_font('Times','B',10.0) 
        pdf.cell(epw, ac, "La primera vinculación de este cliente se genero el " + antiguedad, border=1, align = 'C')
        pdf.ln(ac)
    else:
        pdf.set_font('Times','B',10.0) 
        pdf.cell(epw, ac, "SE TRATA DE UN CLIENTE NUEVO DENTRO DE LA COMPAÑIA ", border=1, align = 'C')
        pdf.ln(ac)

    #ANEXOS
    pdf.add_page()
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, "10 - ANEXOS", border=0, align = 'C') 
    pdf.ln(ac*2)
    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "1- MAPA DE LA ZONA", border=0, align = 'L') 


    pdf.image(r'Archivos/PNG/ID_AR/Roadmap'+str(nit)+'.png', x = 1.5, y = ac*5 , w = ac*22, h = ac*20)
    pdf.ln(ac*22)
    pdf.cell(epw, ac, "2 - CAPTURA DE STREETVIEW", border=0, align = 'L') 
    pdf.image(r'Archivos/PNG/ID_AR/Satelite'+str(nit)+'.png', x = 1.9, y = ac*27 , w = ac*20, h = ac*16)


    pdf.add_page()
    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "3 - INFORMACIÓN NEGOCIOS VECINOS", border=0, align = 'L') 
    pdf.ln(ac*2)

    encabezado = [["Nombre"],["Dirección"],["Tipo"]]

    for row in encabezado:
        for i in row:
            pdf.cell(epw/3, ac, str(i), border=1, align = 'C') 
    pdf.ln(ac)
    pdf.set_font('Times','',10.0) 

    for i in range(0, len(vecinos)):
        infovecinos = [[vecinos[i][0], vecinos[i][2], vecinos[i][4]]]
        for row in infovecinos:
            for i in row:
                pdf.cell(epw/3, ac, str(i), border=1, align = 'C') 
            pdf.ln(ac)

    pdf.add_page()
    pdf.set_font('Times','B',10.0) 
    pdf.cell(epw, ac, "4 - FOTOGRAFIAS DE NEGOCIOS VECINOS", border=0, align = 'L')
    pdf.ln(ac)
    try:

        for i in range(0, len(photos), 2):
            try:
                pdf.image(r"Archivos/PNG/ID_AR/"+str(nit)+str(i)+".jpeg", x = 1.9, y = ac*6 , w = ac*20, h = ac*16)
                pdf.cell(epw, ac, str(nombres[i]), border=0, align = 'L')
            except:
                pass
            try:
                pdf.ln(ac*22)
                pdf.image(r"Archivos/PNG/ID_AR/"+str(nit)+str(i+1)+".jpeg", x = 1.9, y = ac*27 , w = ac*20, h = ac*16)
                pdf.cell(epw, ac, str(nombres[i+1]), border=0, align = 'L')
            except:
                pass
            if i == len(photos) or i+1 == len(photos):
                pass
            else:
                pdf.add_page()
    except:
        pass
    pdf.output('Archivos/PDF/ID_AR/'+ str(variablesManzaneo[27])+" - "+razon_social+'.pdf', 'F')
    respuesta = "Ok"    
    
    def cargarPdf(nombre):

        import os 

        #Drive 

        ruta_destino = '/ARCI/Informes API'
        ruta_origen = 'Archivos/PDF/ID_AR/'
        filename_out= nombre

        print(os.system(f"rclone copy '{ruta_origen}{filename_out}' ARCI:'{ruta_destino}'"))
    
    cargarPdf(str(variablesManzaneo[27])+" - "+razon_social+'.pdf')


    '''
    def cargarPdf(nombre):

        import os 

        #Drive 

        ruta_destino = '/Proyectos/Ingeniero Digital/ReportesCiro/'
        ruta_origen = '/home/ingeniero_digital/principal/PLATAFORMA/plataforma_proyecto/first/static/PDF/'
        filename_out= nombre

        print(os.system(f"rclone copy '{ruta_origen}{filename_out}' IyCUnidad:'{ruta_destino}'"))

    cargarPdf(razon_social + '.pdf')
    '''
    mjs = {
        "longitud": f'{str(longitud)}',
        "latitud": f'{str(latitud)}',
        "razonSocial": f'{razon_social}',
        "fechaRealización": f'{now}', 
        "Respuesta": f'{respuesta}',
        
    } 
    
    return JSONResponse(status_code=200, content=mjs)

@app.get('/API/Fotos_Entorno')
async def StandAlone(direccion:str = None, latitud:str = None, longitud:str = None, ciudad:str =  None):
    
    #Tamaño de la imagen
    size = "1200x1200"
    # Campo de vision horizontal (ZOOM)
    fov = "120"
    #Angulo horizontal de la camara
    heading = 0
    #Angulo vertical 
    pitch = "0"

    if not str(ciudad) == None:
        print("Entro")
        #direccion = direccion.replace(",", "")
        ciudad = ciudad.upper()
        ciudad = ciudad.replace("É","E")
        ciudad = ciudad.replace("Í","I")
        ciudad = ciudad.replace("Ó","O")
        ciudad = ciudad.replace("Ú","U")
    
    if not (direccion) == None:
        Apiest = 'http://ec2-35-153-192-47.compute-1.amazonaws.com:8092/API/1a1'
        args = {'Ciudad' : 'Bogota', 'Direccion': direccion}
        response = requests.get(Apiest, params = args)
        direccion = response.json()['DIRECCION_ESTANDAR']['0']

        geolocalizador = 'https://www.segurosbolivar.com/arcgis/rest/services/Servicios_SB/geoEsri/GPServer/geoEsri/execute'
        geolocalizador_entrada = {'direccion': direccion, 'ciudad': ciudad, 'f': 'json'}
        geolocalizador_salida = requests.get(url=geolocalizador, headers={'content-type': 'application/json'}, params=geolocalizador_entrada)

        latitud = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[0]
        longitud = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[1]
    

    for i in range(0, 4):
        try:
            f = open('Archivos/PNG/ENTORNO/'+str(i)+str(direccion + " - " + ciudad)+'.jpeg','wb')
            f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/streetview?size='+size+'&location='+str(latitud)+','+str(longitud)+'&heading='+str(heading)+'&pitch='+pitch+'&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
            f.close()   
            heading = heading + 90
        except:
            f = open('Archivos/PNG/ENTORNO/'+str(i)+str(latitud + " - " + longitud)+'.jpeg','wb')
            f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/streetview?size='+size+'&location='+str(latitud)+','+str(longitud)+'&heading='+str(heading)+'&pitch='+pitch+'&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
            f.close()   
            heading = heading + 90
            
    import base64
    data = []
    for i in range(0, 4):
        try:

            with open("Archivos/PNG/ENTORNO/"+str(i)+str(direccion + " - " + ciudad)+".jpeg", "rb") as image_file:
                
                # Linea original
                # data.append(base64.b64encode(image_file.read()))

                # ! Cambio para poder hacer una correcta decodificación de la img
                _tmp = base64.b64encode(image_file.read())
                data.append(str(_tmp, 'UTF-8'))
        except:
                    
            with open("Archivos/PNG/ENTORNO/"+str(i)+str(latitud + " - " + longitud)+".jpeg", "rb") as image_file:
                
                # Linea original
                # data.append(base64.b64encode(image_file.read()))

                # ! Cambio para poder hacer una correcta decodificación de la img
                _tmp = base64.b64encode(image_file.read())
                data.append(str(_tmp, 'UTF-8'))

    mjs = {
        "Latitud": f'{latitud}',
        "Longitud": f'{longitud}',
        "imagen 1": f'{data[0]}',
        "imagen 2": f'{data[1]}',
        "imagen 3": f'{data[2]}',
        "imagen 4": f'{data[3]}',
    } 

    return JSONResponse(status_code=200, content=mjs)


@app.get('/API/Modelo_sustraccion')
async def StandAlone(direccion:str = None):
    if not (direccion) == None:
        Apiest = 'http://ec2-35-153-192-47.compute-1.amazonaws.com:8092/API/1a1'
        args = {'Ciudad' : 'Bogota', 'Direccion': direccion}
        response = requests.get(Apiest, params = args)
        direccion = response.json()['DIRECCION_ESTANDAR']['0']

        geolocalizador = 'https://www.segurosbolivar.com/arcgis/rest/services/Servicios_SB/geoEsri/GPServer/geoEsri/execute'
        geolocalizador_entrada = {'direccion': direccion, 'ciudad': "Bogota", 'f': 'json'}
        geolocalizador_salida = requests.get(url=geolocalizador, headers={'content-type': 'application/json'}, params=geolocalizador_entrada)

        latitud = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[0]
        longitud = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[1]

    EntradaApiMapas = {'latitud': str(latitud),'longitud': str(longitud), 'f': 'json'}

    ApiMapasNueva = 'https://www.segurosbolivar.com/arcgis/rest/services/Servicios_SB/ingDigVerDos/GPServer/ingDig/execute'

    resultado_api_mapas_nueva = requests.get(url=ApiMapasNueva,
                                    headers={'content-type': 'application/json'},
                                    params=EntradaApiMapas)

    mapas = resultado_api_mapas_nueva.json()

    categorias = pd.read_excel("Archivos/categorias.xlsx")

    #SE ALMACENAN LAS DISTANCIAS DESDE EL SERVICIO DE MAPAS

    distancias = [mapas['results'][0]['value']['features'][0]['attributes']['DIS_BOMBERO'], 
    mapas['results'][0]['value']['features'][0]['attributes']['DIS_CAI'], 
    mapas['results'][0]['value']['features'][0]['attributes']['DIS_HOSPI'], 
    mapas['results'][0]['value']['features'][0]['attributes']['DIS_IPS'], 
    mapas['results'][0]['value']['features'][0]['attributes']['DIS_TRANSMI'], 
    mapas['results'][0]['value']['features'][0]['attributes']['DIS_SERVI']]

    #CALCULO DE LAS CATEGORIAS DE ACUERDO AL ARCHIVO DESIGNADO (CON PROPORCIÓN)
    for i in reversed(range(len(categorias))):
        if distancias[0]< categorias.iloc[i][2] and distancias[0]> categorias.iloc[i-1][2]:
            bomeberosCate = categorias.iloc[i-1][1] * 0.554768241	
        if distancias[1]< categorias.iloc[i][3] and distancias[1]> categorias.iloc[i-1][3]:
            CAICate = categorias.iloc[i-1][1] * 0.489194208
        if distancias[2]< categorias.iloc[i][4] and distancias[2]> categorias.iloc[i-1][4]:
            hospitalesCate = categorias.iloc[i-1][1] * 0.431583783
        if distancias[3]< categorias.iloc[i][5] and distancias[3]> categorias.iloc[i-1][5]:
            IPSCate = categorias.iloc[i-1][1] * 0.401704408	
        if distancias[4]< categorias.iloc[i][6] and distancias[4]> categorias.iloc[i-1][6]:
            transmiCate = categorias.iloc[i-1][1] * 0.406639651
        if distancias[5]< categorias.iloc[i][7] and distancias[5]> categorias.iloc[i-1][7]:
            gasolinaCate = categorias.iloc[i-1][1] * 0.282416613

    
    #CALCULO DE LAS CATEGORIAS DE ACUERDO AL ARCHIVO DESIGNADO (SIN PROPORCIÓN)
    for i in reversed(range(len(categorias))):
        if distancias[0]< categorias.iloc[i][2] and distancias[0]> categorias.iloc[i-1][2]:
            bomeberosCate2 = categorias.iloc[i-1][1]
        if distancias[1]< categorias.iloc[i][3] and distancias[1]> categorias.iloc[i-1][3]:
            CAICate2 = categorias.iloc[i-1][1]
        if distancias[2]< categorias.iloc[i][4] and distancias[2]> categorias.iloc[i-1][4]:
            hospitalesCate2 = categorias.iloc[i-1][1]
        if distancias[3]< categorias.iloc[i][5] and distancias[3]> categorias.iloc[i-1][5]:
            IPSCate2 = categorias.iloc[i-1][1]
        if distancias[4]< categorias.iloc[i][6] and distancias[4]> categorias.iloc[i-1][6]:
            transmiCate2 = categorias.iloc[i-1][1]
        if distancias[5]< categorias.iloc[i][7] and distancias[5]> categorias.iloc[i-1][7]:
            gasolinaCate2 = categorias.iloc[i-1][1]
        
    calEntorno2 = round((bomeberosCate2 + CAICate2 + hospitalesCate2 + IPSCate2 + transmiCate2 + gasolinaCate2) / 6)
    
    calEntorno = round((bomeberosCate + CAICate + hospitalesCate + IPSCate + transmiCate + gasolinaCate) / 6)

    # ESTA ES LA UNICA INFORMACION QUE FALTA, LA QUE VIENE DESDE EL MAPA DE AMENAZA
    amenazaSus = mapas['results'][0]['value']['features'][0]['attributes']['NIVEL_SUST']

    riesgoSusV = round(calEntorno * amenazaSus)
    
    riesgoSusV2 = round(calEntorno2 * amenazaSus)

    try:
        if 0 < riesgoSusV <= 2:
            riesgoSus = "Baja"
            conceptoSus = "Asegurable"
        if 2 < riesgoSusV <= 5:
            riesgoSus = "Media baja"
            conceptoSus = "Asegurable"
        if 5 < riesgoSusV <= 10:
            riesgoSus = "Media"
            conceptoSus = "Asegurable"
        if 10 < riesgoSusV <= 15:
            riesgoSus = "Media Alta"
            conceptoSus = "No asegurable"
        if 15 < riesgoSusV <= 20:
            riesgoSus = "Alta"
            conceptoSus = "No asegurable"
    except:
        riesgoSus = "Media"
        conceptoSus = "Sin información suficiente"

    try:
        if 0 < riesgoSusV2 <= 2:
            riesgoSus2 = "Baja"
            conceptoSus2 = "Asegurable"
        if 2 < riesgoSusV2 <= 5:
            riesgoSus2 = "Media baja"
            conceptoSus2 = "Asegurable"
        if 5 < riesgoSusV2 <= 10:
            riesgoSus2 = "Media"
            conceptoSus2 = "Asegurable"
        if 10 < riesgoSusV2 <= 15:
            riesgoSus2 = "Media Alta"
            conceptoSus2 = "No asegurable"
        if 15 < riesgoSusV2 <= 20:
            riesgoSus2 = "Alta"
            conceptoSus2 = "No asegurable"
    except:
        riesgoSus2 = "Media"
        conceptoSus2 = "Sin información suficiente"

    mjs = {
        "direccion": f'{direccion}',
        "latitud": f'{latitud}',
        "longitud": f'{longitud}',
        "bomeberosCate": f'{bomeberosCate}',
        "CAICate": f'{CAICate}',
        "hospitalesCate": f'{hospitalesCate}',
        "IPSCate": f'{IPSCate}',
        "transmiCate": f'{transmiCate}',
        "gasolinaCate": f'{gasolinaCate}',
        "calEntorno": f'{calEntorno}',
        "amenazaSus": f'{amenazaSus}',
        "riesgoSusV": f'{riesgoSusV}',
        "riesgoSus": f'{riesgoSus}',
        "conceptoSus": f'{conceptoSus}',

        "bomeberosCate2": f'{bomeberosCate2}',
        "CAICate2": f'{CAICate2}',
        "hospitalesCate2": f'{hospitalesCate2}',
        "IPSCate2": f'{IPSCate2}',
        "transmiCate2": f'{transmiCate2}',
        "gasolinaCate2": f'{gasolinaCate2}',
        "calEntorno2": f'{calEntorno2}',
        "riesgoSusV2": f'{riesgoSusV2}',
        "riesgoSus2": f'{riesgoSus2}',
        "conceptoSus2": f'{conceptoSus2}',
        
    } 

    return JSONResponse(status_code=200, content=mjs)
    
# sudo nohup uvicorn app:app --host 0.0.0.0 --port 8085 --reload --workers 4 > /home/ingeniero_digital/principal/LogApiPruebas_08_06_2022.txt 2>&1 &

if __name__ == '__main__':

    uvicorn.run("app:app", host='0.0.0.0',
               port=8093, reload=True, workers=1)  #


##############################################################################


@app.get('/API/Modelo_Incendio')
async def StandAlone(direccion:str = None, nit :str = None, latitud:str = None, longitud:str = None):
    
    # Importacion de librerias
    import pandas as pd
    import numpy as np
    import requests
    import geopandas as gpd
    import xlsxwriter

    # Baases de datos necesarias
    Base = pd.read_excel(r"Archivos/Modelo_Incendio Versión 2.xlsx",
                        sheet_name="MODELO_COMPLETO", skiprows=1) # Informaccion del modelo completo

    Base2 = pd.read_excel(r"Archivos/Modelo_Incendio Versión 2.xlsx",
                        sheet_name="MODELO_SIN_MANZANEO", skiprows=1) # Informaccion del modelo completo

    Politicas = pd.read_excel(r"Archivos/Calificacion act. property 2021.xlsx") # Politicas de incendio

    ciiu = pd.read_excel(r"Archivos/Estructura-detallada-CIIU-4AC-2020-.xls")

    TUso = pd.read_excel(r"Archivos/TPredioV1.0.xls", sheet_name='30.Dominios  ') 

    ModeloCompleto = Base[["Nomenclatura", "Dominio", "Tipo", "Puntaje", "Peso"]] # Seleccion de algunas variables del modelo
    ModeloSinManz = Base2[["Nomenclatura", "Dominio", "Tipo", "Puntaje", "Peso"]]

    # Almacenar variables de entrada
    workbook = xlsxwriter.Workbook(r'Archivos/save3.xlsx')
    worksheet = workbook.add_worksheet('first')

    worksheet.write(1,0, direccion)
    worksheet.write(1,1, nit)
    worksheet.write(1,2, longitud)
    worksheet.write(1,3, latitud)

    worksheet.write(0,0, 'direccion')
    worksheet.write(0,1, 'nit')
    worksheet.write(0,2, 'longitud')
    worksheet.write(0,3, 'latitud')

    workbook.close()
    save3 = pd.read_excel(r"Archivos/save3.xlsx") 

    # Limpieza de la informacion de entrada
    DireccioN = []

    for i in range(0, len(direccion)):
        if not str(direccion) == 'nan':
            #direccion = direccion.replace(",", "")
            direccion = direccion.upper()
            direccion = direccion.replace("Á","A")
            direccion = direccion.replace("É","E")
            direccion = direccion.replace("Í","I")
            direccion = direccion.replace("Ó","O")
            direccion = direccion.replace("Ú","U")
            DireccioN.append(direccion)
        else:
            DireccioN.append('None')

    NiT = []
    for i in range(0,len(nit)):
        if not (type(nit) == type(None) or str(nit) == 'nan'):
            nit = int(str(nit).replace('.',''))
            nit = int(str(nit).replace(',',''))
        NiT.append(nit)

    LatituD = []
    for i in range(0,len(save3)):
        gamma = save3.iloc[i].iloc[2]
        if not (str(gamma) == 'nan' or type(gamma) == type(None)):
            gamma = float(str(gamma).replace(',','.'))
        LatituD.append(gamma) #
    LongituD = []
    for i in range(0,len(save3)):
        eta = save3.iloc[i].iloc[3]
        if not (str(eta) == 'nan' or type(eta) == type(None)):
            eta = float(str(eta).replace(',','.'))
        LongituD.append(eta)

    #E Estandarizador
    CarrerA = ["CARRERA", "CRA", "K", "KRA", "K.", "CRA.", "KRA.", "KR.", "CR"]
    CallE = ["CLL", "CALLE", "CL.", "CLL.", "C.", "KALLE"]
    DiagonaL = ["DIAGONAL", "DG.", "DIAG.", "DIAG", "D.", "DGL", "DGL."]
    TransversaL = ["TRANSVERSAL", "TV.", "TR.", "T.", "TRANS.", "TRR", "T", "TRANS", "TR"]
    AvenidA = ["AVENIDA", "AV.", "A.", "AVD", "AVDA"]
    AvenidaCalle = ["AV CL", "AC."]
    AvenidaCarrera = ["AK.", "AV KR"]
    Bodega = ["BODEGA", "BG.", "BOD", "BOD.", "BODEGAS", "BOEGAS", "BODG2", "BOEGA", "BD", "PLANTA"]
    Local = ["LOCAL", "LC.", "LOC", "LOCALES", "LOC."]
    Interior = ["INTERIOR", "INT", "INT.", "IN."]
    Apartamento = ["APT.", "AP.", "APARTAMENTO", "APT", "APTO", "APTO."]
    Oficina = ["OFICINA", "OF.", "OFICINAS", "CONSULTORIO", "CONSULT.", "CONSULT", "0FIC", "OFOF", "0F", "OFC", "OFC."]
    Torre = ["TORRE", "TO."]
    Lote = ["LOTE", "LOT", "LOT."]

    for i in range(0,len(DireccioN)):
            for j in range(0, len(CarrerA)):
                if CarrerA[j] in DireccioN[i].split():
                    DireccioN[i] = DireccioN[i].replace(CarrerA[j] + " ", "KR ")
                    break
            for j in range(0, len(CallE)):
                if CallE[j] in DireccioN[i].split():
                    DireccioN[i] = DireccioN[i].replace(CallE[j] + " ", "CL ")
                    break
            if not " BIS" in DireccioN[i]:
                if "BIS" in DireccioN[i]:
                    DireccioN[i] = DireccioN[i].replace("BIS", " BIS")
            if "ª" in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("ª", "")
            if "#" in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(" #", " ")
            elif "#" in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("#", "")
            elif "NO." in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(" NO. ", " ")
            elif "N°" in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(" N° ", " ")
            elif "Nº" in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(" Nº ", " ")
            elif "NO" in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(" NO ", " ")
            elif "NO." in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("NO.", "")
            elif "N°" in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("N°", "")
            elif "Nº" in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("Nº", "")
            if "-" in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(" - ", " ")
            elif "-" in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("-", " ")
            if "—" in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(" — ", " ")
            elif "—" in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("—", " ")
            if "−" in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(" − ", " ")
            elif "−" in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("−", " ")
            if "–" in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(" – ", " ")
            elif "–" in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("–", " ")
            for j in range(0, len(DiagonaL)):
                if DiagonaL[j] in DireccioN[i].split():
                    DireccioN[i] = DireccioN[i].replace(DiagonaL[j] + " ", "DG ")
                    break
            for j in range(0, len(TransversaL)):
                if TransversaL[j] in DireccioN[i].split():
                    DireccioN[i] = DireccioN[i].replace(TransversaL[j] + " ", "TV ")
                    break
            for j in range(0, len(AvenidA)):
                if AvenidA[j] in DireccioN[i].split():
                    DireccioN[i] = DireccioN[i].replace(AvenidA[j] + " ", "AV ")
                    break
            for j in range(0, len(Bodega)):
                if Bodega[j] in DireccioN[i].split():
                    DireccioN[i] = DireccioN[i].replace(Bodega[j] + " ", "BG ")
            for j in range(0, len(Local)):
                if Local[j] in DireccioN[i].split():
                    DireccioN[i] = DireccioN[i].replace(Local[j] + " ", "LC ")
            for j in range(0, len(Apartamento)):
                if Apartamento[j] in DireccioN[i].split():
                    DireccioN[i] = DireccioN[i].replace(Apartamento[j] + " ", "AP ")
            for j in range(0, len(Oficina)):
                if Oficina[j] in DireccioN[i].split():
                    DireccioN[i] = DireccioN[i].replace(Oficina[j] + " ", "OF ")
                elif Oficina[j] in DireccioN[i]:
                    DireccioN[i] = DireccioN[i].replace(Oficina[j], "OF ")
            for j in range(0, len(Torre)):
                if Torre[j] in DireccioN[i].split():
                    DireccioN[i] = DireccioN[i].replace(Torre[j] + " ", "TO ")
            for j in range(0, len(Lote)):
                if Lote[j] in DireccioN[i].split():
                    DireccioN[i] = DireccioN[i].replace(Lote[j] + " ", "LT ")
            for j in range(0, len(Interior)):
                if Interior[j] in DireccioN[i].split():
                    DireccioN[i] = DireccioN[i].replace(Interior[j] + " ", "IN ")
                    break
            for j in range(0, len(AvenidaCalle)):
                if AvenidaCalle[j] in DireccioN[i]:
                    DireccioN[i] = DireccioN[i].replace(AvenidaCalle[j] + " ", "AC ")
                    break
            for j in range(0, len(AvenidaCarrera)):
                if AvenidaCarrera[j] in DireccioN[i]:
                    DireccioN[i] = DireccioN[i].replace(AvenidaCarrera[j] + " ", "AK ")
                    break
            if "   " in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("   ", " ")
            if "  " in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("  ", " ")
            if "   " in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("   ", " ")
            if "  " in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("  ", " ")
            if "  " in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("  ", " ")


    NombreVariables = ModeloCompleto.iloc[:, 0].unique() # Variables contempladas en el modelo
    NombreVariables2 = ModeloSinManz.iloc[:, 0].unique()
    # Informacion suministrada desde el ID

    import psycopg2
    con = psycopg2.connect(database="ingdigital", user="postgres", password="Bolivar2021",
            host="35.153.192.47", port=8081)


    # Lectura desde PostgreSQL
    sql_predios = f"""SELECT * FROM predios_0321
    WHERE STRPOS(REPLACE("PreDirecc", '  ', ' '), '{DireccioN[0]}') > 0"""
    predios = pd.read_sql(sql_predios, con) 
    pd.set_option('display.max_columns', 100)
    predios

    if len(predios) == 0:
        sql_predios = f"""SELECT * FROM predios_0321
    WHERE STRPOS('{DireccioN[0]}', REPLACE("PreDirecc", '  ', ' ')) > 0"""
        predios = pd.read_sql(sql_predios, con) 

    U = 0 # Variable para seleccionar la fila de la tabla de predios de una dirección

    if "BG" in DireccioN[0]: # A veces aparece IN en vez de BG
        if len(predios) == 0:
            DireccioN[0] = DireccioN[0].replace("BG", "IN")
            sql_predios = f"""SELECT * FROM predios_0321
    WHERE REPLACE("PreDirecc", '  ', ' ') = '{DireccioN[0]}'"""
            predios = pd.read_sql(sql_predios, con)

    if len(predios) == 0:
        Letras = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "O", "P", "Q"]
        for i in range(0,len(DireccioN)):
            for j in range(0, len(Letras)):
                if Letras[j] in DireccioN[i].split():
                    DireccioN[i] = DireccioN[i].replace(" " + Letras[j], Letras[j])
                    sql_predios = f"""SELECT * FROM predios_0321
    WHERE REPLACE("PreDirecc", '  ', ' ') = '{DireccioN[0]}'"""
                    predios = pd.read_sql(sql_predios, con)

    if len(predios) == 0:
        if "BIS" in DireccioN[0]:
            DireccioN[0] = DireccioN[0].replace("BIS", "BIS ")
            sql_predios = f"""SELECT * FROM predios_0321
    WHERE REPLACE("PreDirecc", '  ', ' ') = '{DireccioN[0]}'"""
            predios = pd.read_sql(sql_predios, con)

    if len(predios) == 0:
        sql_predios = f"""SELECT * FROM predios_0321
        WHERE STRPOS(REPLACE("PreDSI", '  ', ' '), '{DireccioN[0]}') > 0"""
        predios = pd.read_sql(sql_predios, con) 
        if len(predios) == 0:
            sql_predios = f"""SELECT * FROM predios_0321
        WHERE STRPOS('{DireccioN[0]}', REPLACE("PreDSI", '  ', ' ')) > 0"""
            predios = pd.read_sql(sql_predios, con) 

    if not len(predios) == 0:
        sql_lotes = f"""SELECT * FROM lotes_0321
            WHERE STRPOS("LOTCODIGO", '{'00' + str(predios.iloc[U]["Barmanpre"])}') = 1"""
        lotes = gpd.GeoDataFrame.from_postgis(sql_lotes, con)  

    if not len(predios) == 0:
        if len(str(predios.iloc[U]["PreCCons"])) == 1:
            sql_construccion = f"""SELECT * FROM construccion_tabla_0321
                WHERE STRPOS("ConCodigo", '{'00' + str(predios.iloc[U]["Barmanpre"]) + '00' + str(predios.iloc[U]["PreCCons"])}') = 1"""
            construccion = gpd.GeoDataFrame.from_postgis(sql_construccion, con)
        elif len(str(predios.iloc[U]["PreCCons"])) > 1:
            sql_construccion = f"""SELECT * FROM construccion_tabla_0321
                WHERE STRPOS("ConCodigo", '{'00' + str(predios.iloc[U]["Barmanpre"]) + '0' + str(predios.iloc[U]["PreCCons"])}') = 1"""
            construccion = gpd.GeoDataFrame.from_postgis(sql_construccion, con)

    if not (str(LatituD[0]) == 'nan' or str(LongituD[0]) == 'nan'):
        if len(predios) == 0:
            if type(LatituD[0]) == str:
                LatituD[0] = LatituD[0].replace(',', '.')
            if type(LongituD[0]) == str:
                LongituD[0] = LongituD[0].replace(',', '.')
            sql_lotes2 = f"""SELECT * FROM lotes_0321
            WHERE ST_Intersects(
                geom,
                ST_Transform(ST_GeometryFromText('POINT({LongituD[0]} {LatituD[0]})', 4686), 4686)
                );
            """
            lotes2 = gpd.GeoDataFrame.from_postgis(sql_lotes2, con)
            if not len(lotes2) == 0:
                lotes = lotes2
            if not len(lotes2) == 0:
                sql_construccion2 = f"""SELECT * FROM construccion_tabla_0321
                WHERE ST_Intersects(
                    ST_Centroid(geom),
                    ST_GeomFromText('{lotes['geom'].iloc[0]}', 4686)
                    );
                """
                construccion2 = gpd.GeoDataFrame.from_postgis(sql_construccion2, con)
                if not len(construccion2) == 0:
                    construccion = construccion2

                # Predios
                sql_predios = f"""SELECT * FROM predios_0321
                    WHERE STRPOS('{lotes['LOTCODIGO'][0]}', CONCAT('0','0',"Barmanpre")) = 1"""
                predios = pd.read_sql_query(sql_predios, con)
                DireccioN[0] = predios["PreDirecc"].iloc[0]



    if len(predios) == 0:
        geolocalizador_entrada = {'direccion': DireccioN[0],
                'ciudad': "Bogota".upper().replace('Á', 'A'), 'f': 'json'}

    # GENERACIÓN DE LAS COORDENADAS A PARTIR DE LA DIRECCIÓN
        geolocalizador = 'https://www.segurosbolivar.com/arcgis/rest/services/Servicios_SB/geoEsri/GPServer/geoEsri/execute'
        geolocalizador_salida = requests.get(url=geolocalizador,
                        headers={'content-type': 'application/json'},
                        params=geolocalizador_entrada)
        print(geolocalizador_salida)
        if not len(geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')) == 1:
            try:
                LatituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[0]
                LongituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[1]
            except:
                urlGeocode = 'http://api.lupap.co/v2/co/'
                temp = requests.get(urlGeocode + 'bogota' + '?a=' + direccion+'&key=3bee5f0a19bf31eb0fa8a70376a4c61eb34d9ba8')
                LatituD[0] = temp.json()['response']['geometry']['coordinates'][1]
                LongituD[0] = temp.json()['response']['geometry']['coordinates'][0]
                
            sql_lotes2 = f"""SELECT * FROM lotes_0321
            WHERE ST_Intersects(
                geom,
                ST_Transform(ST_GeometryFromText('POINT({LongituD[0]} {LatituD[0]})', 4686), 4686)
                );
            """
            lotes2 = gpd.GeoDataFrame.from_postgis(sql_lotes2, con)
            if not len(lotes2) == 0:
                lotes = lotes2
            if not len(lotes2) == 0:
                sql_construccion2 = f"""SELECT * FROM construccion_tabla_0321
                WHERE ST_Intersects(
                    ST_Centroid(geom),
                    ST_GeomFromText('{lotes['geom'].iloc[0]}', 4686)
                    );
                """
                construccion2 = gpd.GeoDataFrame.from_postgis(sql_construccion2, con)
                if not len(construccion2) == 0:
                    construccion = construccion2 

                # Predios
                sql_predios = f"""SELECT * FROM predios_0321
                    WHERE STRPOS('{lotes['LOTCODIGO'][0]}', CONCAT('0','0',"Barmanpre")) = 1"""
                predios = pd.read_sql_query(sql_predios, con)
                DireccioN[0] = predios["PreDirecc"].iloc[0]
            if len(lotes2) == 0:
                sql_lotes3 = f"""SELECT * FROM lotes_0321
                WHERE ST_Distance(
                    geom,
                    ST_Transform(ST_GeometryFromText('POINT({LongituD[0]} {LatituD[0]})', 4686), 4686)
                    ) < 0.0002
                ORDER BY
                geom <-> ST_GeometryFromText('POINT({LongituD[0]} {LatituD[0]})', 4686):: geometry
                LIMIT 1;
                """
                lotes3 = gpd.GeoDataFrame.from_postgis(sql_lotes3, con)
                if not len(lotes3) == 0:
                    lotes = lotes3
                if not len(lotes3) == 0:
                    sql_construccion2 = f"""SELECT * FROM construccion_tabla_0321
                    WHERE ST_Intersects(
                        ST_Centroid(geom),
                        ST_GeomFromText('{lotes['geom'].iloc[0]}', 4686)
                        );
                    """
                    construccion2 = gpd.GeoDataFrame.from_postgis(sql_construccion2, con)
                    if not len(construccion2) == 0:
                        construccion = construccion2 

                    # Predios
                    sql_predios = f"""SELECT * FROM predios_0321
                        WHERE STRPOS('{lotes['LOTCODIGO'][0]}', CONCAT('0','0',"Barmanpre")) = 1"""
                    predios = pd.read_sql_query(sql_predios, con)
                    DireccioN[0] = predios["PreDirecc"].iloc[0]

    # Se vuelve a intentar con la dirección sin estandarizar

    if len(predios) == 0:
        DireccioN[0] = save3.iloc[0].iloc[0] 
        if not str(save3.iloc[i].iloc[0]) == 'nan':
            DireccioN[0] = DireccioN[0].upper()
            DireccioN[0] = DireccioN[0].replace("Á","A")
            DireccioN[0] = DireccioN[0].replace("É","E")
            DireccioN[0] = DireccioN[0].replace("Í","I")
            DireccioN[0] = DireccioN[0].replace("Ó","O")
            DireccioN[0] = DireccioN[0].replace("Ú","U")
        
        geolocalizador_entrada = {'direccion': DireccioN[0],
                'ciudad': "Bogota".upper().replace('Á', 'A'), 'f': 'json'}

        # GEOLOCALIZADOR DEVUELVE LA LATITUD Y LONGITUD DE LA DIRECCION INGRESADA
        # geolocalizador = 'https://www.segurosbolivar.com/arcgis/rest/services/Servicios_SB/geoEsri/GPServer/geoEsri/execute'

        geolocalizador_salida = requests.get(url=geolocalizador,
                        headers={'content-type': 'application/json'},
                        params=geolocalizador_entrada)
        if not len(geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')) == 1:
            try:
                LatituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[0]
                LongituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[1]
            except:
                urlGeocode = 'http://api.lupap.co/v2/co/'
                temp = requests.get(urlGeocode + 'bogota' + '?a=' + direccion+'&key=3bee5f0a19bf31eb0fa8a70376a4c61eb34d9ba8')
                LatituD[0] = temp.json()['response']['geometry']['coordinates'][0]
                LongituD[0] = temp.json()['response']['geometry']['coordinates'][1]
        
            sql_lotes2 = f"""SELECT * FROM lotes_0321
            WHERE ST_Intersects(
                geom,
                ST_Transform(ST_GeometryFromText('POINT({LongituD[0]} {LatituD[0]})', 4686), 4686)
                );

            """
            lotes2 = gpd.GeoDataFrame.from_postgis(sql_lotes2, con)
            if not len(lotes2) == 0:
                lotes = lotes2
            if not len(lotes2) == 0:
                sql_construccion2 = f"""SELECT * FROM construccion_tabla_0321
                WHERE ST_Intersects(
                    ST_Centroid(geom),
                    ST_GeomFromText('{lotes['geom'].iloc[0]}', 4686)
                    );
                """
                construccion2 = gpd.GeoDataFrame.from_postgis(sql_construccion2, con)
                if not len(construccion2) == 0:
                    construccion = construccion2 

                # Predios
                sql_predios = f"""SELECT * FROM predios_0321
                    WHERE STRPOS('{lotes['LOTCODIGO'][0]}', CONCAT('0','0',"Barmanpre")) = 1"""
                predios = pd.read_sql_query(sql_predios, con)
                DireccioN[0] = predios["PreDirecc"].iloc[0]
        
            if len(lotes2) == 0:
                sql_lotes3 = f"""SELECT * FROM lotes_0321
                WHERE ST_Distance(
                    geom,
                    ST_Transform(ST_GeometryFromText('POINT({LongituD[0]} {LatituD[0]})', 4686), 4686)
                    ) < 0.0002
                ORDER BY
                geom <-> ST_GeometryFromText('POINT({LongituD[0]} {LatituD[0]})', 4686):: geometry
                LIMIT 1;
                """
                lotes3 = gpd.GeoDataFrame.from_postgis(sql_lotes3, con)
                if not len(lotes3) == 0:
                    lotes = lotes3
                if not len(lotes3) == 0:
                    sql_construccion2 = f"""SELECT * FROM construccion_tabla_0321
                    WHERE ST_Intersects(
                        ST_Centroid(geom),
                        ST_GeomFromText('{lotes['geom'].iloc[0]}', 4686)
                        );
                    """
                    construccion2 = gpd.GeoDataFrame.from_postgis(sql_construccion2, con)
                    if not len(construccion2) == 0:
                        construccion = construccion2 

                    # Predios
                    sql_predios = f"""SELECT * FROM predios_0321
                        WHERE STRPOS('{lotes['LOTCODIGO'][0]}', CONCAT('0','0',"Barmanpre")) = 1"""
                    predios = pd.read_sql_query(sql_predios, con)
                    DireccioN[0] = predios["PreDirecc"].iloc[0]

    if not type(construccion) == type(None):
        if len(construccion) == 0:
            sql_construccion = f"""SELECT * FROM construccion_tabla_0321
                WHERE STRPOS("ConCodigo", '{'00' + str(predios.iloc[U]["Barmanpre"])}') = 1"""
            construccion = gpd.GeoDataFrame.from_postgis(sql_construccion, con)
            if not len(construccion) == 0:
                construccion = gpd.GeoDataFrame(construccion.iloc[0:1])

    sql_dane = f"""SELECT * FROM dane_2020
    WHERE "NIT" = '{int(nit)}'"""
    dane = pd.read_sql(sql_dane, con) 

    sql_emis = f"""SELECT * FROM emis_0521
    WHERE "n_id" = '{int(nit)}'"""
    emis = pd.read_sql(sql_emis, con) 

    razon_social = 'None'
    ciiu_dado = []
    ciiu_numero = []
    departamento_principal = 'None'
    direccion_principal = 'None'
    municipio_principal = 'None'
    telefono_principal = 'None'
    telefono2_principal = 'None'
    nombre_comercial = 'None'

    if not len(dane) == 0: 
        razon_social = dane['RAZON_SOCIAL'].iloc[0]
        nombre_comercial = None
        for i in range(0,len(dane)):
            if not str(dane['NOMBRE_COMERCIAL'].iloc[i]) == 'nan':
                nombre_comercial = dane['NOMBRE_COMERCIAL'].iloc[i]
        direccion_principal = dane['DIRECCION'].iloc[0]
        departamento_principal = dane['NOMBRE_DPTO'].iloc[0]
        municipio_principal = dane['NOMBRE_MPIO'].iloc[0]
        telefono_principal = str(int(dane['TELEFONO1'].iloc[0]))
        telefono2_principal = str(int(dane['TELEFONO1'].iloc[0]))

        def match_ciiu(self):
            '''Retorna el índice de la actividad económica correspondiente al código CIIU
            params:
            self = código CIIU correspondiente al NIT
            '''
            for index, s in enumerate(ciiu['Unnamed: 2']):
                if str(s) == str(self) or str(s) == '0' + str(self):
                        return index, s
                        break
                elif str(self)[:3] == str(ciiu['Unnamed: 3'].iloc[index]) or str(self) == '0' + str(ciiu['Unnamed: 3'].iloc[index]):
                    return index, ciiu['Unnamed: 1'].iloc[index]

        for i in range(0, len(dane)):
            print(ciiu_dado)
            ciiu_dado.append(ciiu['Unnamed: 3'].iloc[match_ciiu(int(dane['CIIU_ID_CIIU_4'].iloc[i]))[0]])
        for i in range(0, len(dane)):
            ciiu_numero.append(str(int(dane['CIIU_ID_CIIU_4'].iloc[i])))

    Latitud = LatituD[0] 
    Longitud = LongituD[0]

    LATITUD = Latitud
    LONGITUD = Longitud


    LatloN = [(None,None)]

    if not len(lotes) == 0:
        LatloN = []
        LatloN.append((lotes['geom'].iloc[0].centroid.y, lotes['geom'].iloc[0].centroid.x))

        #Número de 

    if not type(construccion) == type(None):
        ConstruccioN = []
        ConstruccioN.append(construccion['ConNPisos'])
        ConstruccioN.append(construccion['ConTSemis'])
        ConstruccioN.append(construccion['ConNSotano'])

    LATITUD = LatloN[0][0]
    LONGITUD = LatloN[0][1]

    ApiMapas = 'https://www.segurosbolivar.com/arcgis/rest/services/Servicios_SB/ingDigVerDos/GPServer/ingDig/execute'

    EntradaApiMapas = {'latitud': str(LATITUD),
                'longitud': str(LONGITUD), 'f': 'json'}
                
    resultado_api_mapas = requests.get(url=ApiMapas,
                        headers={'content-type': 'application/json'},
                        params=EntradaApiMapas)
    EntradaManzaneoPymes = {'latitud': str(LATITUD),
            'longitud': str(LONGITUD), 'f': 'json'}

    alpha = resultado_api_mapas.json()
    ValoreS = []

    if "error" in alpha.keys():
        pass
    else:
        if not alpha['results'][0]['value']['features'] == []:
                ValoreS.append((
                        alpha['results'][0]['value']['features'][0]['attributes']['RESTAURANTES'],
                        alpha['results'][0]['value']['features'][0]['attributes']['ACT_INCENDIO'],
                        alpha['results'][0]['value']['features'][0]['attributes']['G_AMEN_PRE'],
                        alpha['results'][0]['value']['features'][0]['attributes']['DIS_HIDRA'],
                        alpha['results'][0]['value']['features'][0]['attributes']['DIS_BOMBERO'],
                        ))

    if len(predios) >= 2:
        if not list(predios["PreAUso"].dropna()) == []:
            U = predios["PreAUso"].dropna().apply(lambda x: x.replace(',','.')).astype(float).idxmax()
        else:
            U = 0
    else:
        U = 0

    if not len(predios) == 0:
        DireccioN[0] = predios["PreDirecc"][0]

    def PreCUso(index):
        '''Retorna los usos de los predios de la dirección
        '''    
        for i in range(0, len(TUso.iloc[:,0:1])):
            if not (str(predios['PreCUso'].unique()[index]) == 'nan' or str(predios['PreCUso'].unique()[index]) == 'None'):
                if str(TUso.iloc[72:,:].iloc[i].iloc[0]) == '0' + str(int(predios['PreCUso'].unique()[index])) or str(TUso.iloc[72:,:].iloc[i].iloc[0]) == '00' + str(int(predios['PreCUso'].unique()[index])):
                    return f'''Etiqueta: {TUso.iloc[72:,:].iloc[i].iloc[2]}.
                    Definición: {TUso.iloc[72:,:].iloc[i].iloc[1]}'''
                    break

    def coma(name):
        '''Retorna el índice del carácter del string que es igual a una coma
        params:
        index = índice de la fila
        name = nombre de la columna
        '''
        for i in range(0,100):
            if predios.iloc[U][name][i] == '.':
                return i
                break

    def clase_suelo():
        '''Extrae la clase de suelo urbano de la Zona Homogénea Física'''
        if len(predios.iloc[U]['PreCZHF']) == 13:
            if predios.iloc[U]['PreCZHF'][0] == '5':
                return 'Clase de Suelo Urbano protegido'
            elif predios.iloc[U]['PreCZHF'][0] == '6':
                return 'Clase de Suelo Urbano no protegido'

    def topografia():
        '''Extrae la topografía de la Zona Homogénea Física (área urbana)'''
        if len(predios.iloc[U]['PreCZHF']) == 13:
            if predios.iloc[U]['PreCZHF'][0] == '5' or predios.iloc[U]['PreCZHF'][0] == '6':
                if predios.iloc[U]['PreCZHF'][5] == '1':
                    return 'Topografía plana: (Entre 0 y < 7%)'
                elif predios.iloc[U]['PreCZHF'][5] == '2':
                    return 'Topografía Inclinada: (Entre 7% y < 14%)'
                elif predios.iloc[U]['PreCZHF'][5] == '3':
                    return 'Topografía Empinada: (14% o más)'

    def clase_vias():
        '''Extrae la clase de vía de la Zona Homogénea Física (área urbana)'''
        if len(predios.iloc[U]['PreCZHF']) == 13:
            if predios.iloc[U]['PreCZHF'][0] == '5' or predios.iloc[U]['PreCZHF'][0] == '6':
                if predios.iloc[U]['PreCZHF'][8] == '1':
                    alpha = 'Sin vías'
                elif predios.iloc[U]['PreCZHF'][8] == '2':
                    alpha = 'Peatonles sin pavimentar'
                elif predios.iloc[U]['PreCZHF'][8] == '3':
                    alpha = 'Peatonales pavimentadas'
                elif predios.iloc[U]['PreCZHF'][8] == '4':
                    alpha = 'Vehiculares sin pavimentar'
                elif predios.iloc[U]['PreCZHF'][8] == '5':
                    alpha = 'Vehiculares pavimentadas'
                return alpha

    def estado_vias():
        '''Extrae el estado de la vía de la Zona Homogénea Física (área urbana)'''
        if len(predios.iloc[U]['PreCZHF']) == 13:
            if predios.iloc[U]['PreCZHF'][0] == '5' or predios.iloc[U]['PreCZHF'][0] == '6':
                if predios.iloc[U]['PreCZHF'][9] == '0':
                    alpha = 'Sin vías'
                elif predios.iloc[U]['PreCZHF'][9] == '1':
                    alpha = 'Estado vías Malo'
                elif predios.iloc[U]['PreCZHF'][9] == '2':
                    alpha = 'Estado vías Regular'
                elif predios.iloc[U]['PreCZHF'][9] == '3':
                    alpha = 'Estado vías Bueno'
                elif predios.iloc[U]['PreCZHF'][9] == '4':
                    alpha = 'Estado vías Excelente'
                return alpha

    def influencia_vias():
        '''Extrae la influencia de la vía de la Zona Homogénea Física (área urbana)'''
        if len(predios.iloc[U]['PreCZHF']) == 13:
            if predios.iloc[U]['PreCZHF'][0] == '5' or predios.iloc[U]['PreCZHF'][0] == '6':
                if predios.iloc[U]['PreCZHF'][10] == '0':
                    alpha = 'Sin vías'
                elif predios.iloc[U]['PreCZHF'][10] == '1':
                    alpha = 'Vial local'
                elif predios.iloc[U]['PreCZHF'][10] == '2':
                    alpha = 'Vial zonal o Intermedia'
                elif predios.iloc[U]['PreCZHF'][10] == '3':
                    alpha = 'Arterial complementario'
                elif predios.iloc[U]['PreCZHF'][10] == '4':
                    alpha = 'Arterial basico o principal'
                return alpha

    def estado_estructura():
        '''Extrae el estado de la estructura (en función de la tipología y la vetustez) de la base predios'''
        estado = None
        if (str(predios.iloc[U]['PreECons']) == 'nan' or str(predios.iloc[U]['PreECons']) == 'None'):
            pass
        elif int(predios.iloc[U]['PreECons']) == 141:
            estado = 'malo'
        elif int(predios.iloc[U]['PreECons']) == 142:
            estado = 'regular'
        elif int(predios.iloc[U]['PreECons']) == 143:
            estado = 'bueno'
        elif int(predios.iloc[U]['PreECons']) == 144:
            estado = 'excelente'
        return estado

    def bloque1():
        '''Extrae el área del terreno, área construida, año construcción, área uso'''
        area_terreno = predios.iloc[U]['PreATerre'][0:coma('PreATerre')+3] #+3 para 2 decimales
        area_construida =  predios.iloc[U]['PreAConst'][0:coma('PreAConst')+3]
        año_construccion = None
        area_uso = None
        if not (str(predios.iloc[U]['PreVetustz']) == 'nan' or str(predios.iloc[U]['PreVetustz']) == "None"):
            año_construccion = str(int(predios.iloc[U]['PreVetustz']))
        if not (str(predios.iloc[U]['PreAUso']) == 'nan' or str(predios.iloc[U]['PreAUso']) == 'None'):
            area_uso = predios.iloc[U]['PreAUso'][0:coma('PreAUso')+3] 
        print(año_construccion)
        return area_terreno, area_construida, año_construccion, area_uso

    def fachada():
        '''Extrae el tipo de acabado de la fachada'''
        alpha = None
        if not (str(predios.iloc[U]['PreAFachad']) == 'None' or str(predios.iloc[U]['PreAFachad']) == 'nan'):
            if int(predios.iloc[U]['PreAFachad']) == 211:
                alpha = 'Pobre'
            elif int(predios.iloc[U]['PreAFachad']) == 212:
                alpha = 'Sencilla'
            elif int(predios.iloc[U]['PreAFachad']) == 213:
                alpha = 'Regular'
            elif int(predios.iloc[U]['PreAFachad']) == 214:
                alpha = 'Buena'
            elif int(predios.iloc[U]['PreAFachad']) == 215:
                alpha = 'Lujosa'
            return alpha

    def cubrimiento_muros():
        '''Tipo de cubierta y muros de los Acabados
        '''
        alpha = None
        if not (str(predios.iloc[U]['PreACubier']) == 'nan' or str(predios.iloc[U]['PreACubier']) == 'None'):
            if int(predios.iloc[U]['PreACubier']) == 221:
                alpha = 'Sin Cubrimiento'
            elif int(predios.iloc[U]['PreACubier']) == 222:
                alpha = 'Pañete, Ladrillo prensado'
            elif int(predios.iloc[U]['PreACubier']) == 223:
                alpha = 'Estuco, Cerámica, Papel colgadura'
            elif int(predios.iloc[U]['PreACubier']) == 224:
                alpha = 'Madera, Piedra ornamental'
            elif int(predios.iloc[U]['PreACubier']) == 225:
                alpha = 'Marmol, Lujos y Otros'
            return alpha

    def acabado_pisos():
        '''Tipo de acabado de los pisos.
        '''
        alpha = None
        if not (str(predios.iloc[U]['PreAPisos']) == 'None' or str(predios.iloc[U]['PreAPisos']) == 'nan'):
            if int(predios.iloc[U]['PreAPisos']) == 231:
                alpha = 'Tierra pisada'
            elif int(predios.iloc[U]['PreAPisos']) == 232:
                alpha = 'Cemento, Madera burda'
            elif int(predios.iloc[U]['PreAPisos']) == 233:
                alpha = 'Baldosa común, Cemento, Tablón, Ladrillo'
            elif int(predios.iloc[U]['PreAPisos']) == 234:
                alpha = 'Listón Machihembriado'
            elif int(predios.iloc[U]['PreAPisos']) == 235:
                alpha = 'Tableta, Caucho, Acrílico, Granito, Baldosa fina'
            elif int(predios.iloc[U]['PreAPisos']) == 236:
                alpha = 'Parquet, Alfombra, Retal de marmol (grano pequeño)'
            elif int(predios.iloc[U]['PreAPisos']) == 237:
                alpha = 'Retal marmol, Marmol, Otros lujos'
            return alpha

    def estado_acabados():
        '''Se refiere al estado de los acabados en función de la “calidad de los materiales” y de su “estado de conservación”. Puede ser: mala, regular, buena o excelente.
        '''        
        alpha = None
        if not predios.iloc[U]['PreACons'] == None:
            if int(predios.iloc[U]['PreACons']) == 0:
                alpha = 'no se sabe'
            elif int(predios.iloc[U]['PreACons']) == 241:
                alpha = 'malo'
            elif int(predios.iloc[U]['PreACons']) == 242:
                alpha = 'regular'
            elif int(predios.iloc[U]['PreACons']) == 243:
                alpha = 'bueno'
            elif int(predios.iloc[U]['PreACons']) == 244:
                alpha = 'excelente'
            return alpha

    def muros():
        '''Tipo de muros de la estructura. Se refiere a los muros divisorios que no forman parte del armazón o estructura de la edificación.
        '''
        alpha = None
        if not (str(predios.iloc[U]['PreEMuros']) == 'nan' or str(predios.iloc[U]['PreEMuros']) == 'None'):
            if int(predios.iloc[U]['PreEMuros']) == 121:
                alpha = 'materiales de desecho, esterilla'
            elif int(predios.iloc[U]['PreEMuros']) == 122:
                alpha = 'bahareque, adobe, tapia'
            elif int(predios.iloc[U]['PreEMuros']) == 123:
                alpha = 'madera'
            elif int(predios.iloc[U]['PreEMuros']) == 124:
                alpha = 'concreto prefabricado'
            elif int(predios.iloc[U]['PreEMuros']) == 125:
                alpha = 'bloque, ladrillo'
            return alpha

    def armazon():
        '''
        '''
        alpha = None
        if not (str(predios.iloc[U]['PreEArmaz']) == 'nan' or str(predios.iloc[U]['PreEArmaz']) == 'None'):
            if int(predios.iloc[U]['PreEArmaz']) == 0:
                alpha = 'no se sabe'
            elif int(predios.iloc[U]['PreEArmaz']) == 111:
                alpha = 'Madera'
            elif int(predios.iloc[U]['PreEArmaz']) == 112:
                alpha = 'Prefabricado'
            elif int(predios.iloc[U]['PreEArmaz']) == 113:
                alpha = 'Mamposteria'
            elif int(predios.iloc[U]['PreEArmaz']) == 114:
                alpha = 'Concreto'
            elif int(predios.iloc[U]['PreEArmaz']) == 115:
                alpha = 'Concreto'
            return alpha

    def cubierta():
        '''
        '''
        alpha = None
        if not (str(predios.iloc[U]['PreECubier']) == 'nan' or str(predios.iloc[U]['PreECubier']) == 'None'):
            if int(predios.iloc[U]['PreECubier']) == 131:
                alpha = 'materiales de desechos, tejas asfálticas'
            elif int(predios.iloc[U]['PreECubier']) == 132:
                alpha = 'zinc, teja de barro, eternit rústico'
            elif int(predios.iloc[U]['PreECubier']) == 133:
                alpha = 'entrepiso (cubierta provisional) prefabricado'
            elif int(predios.iloc[U]['PreECubier']) == 134:
                alpha = 'eternit o teja de barro (cubierta sencilla)'
            elif int(predios.iloc[U]['PreECubier']) == 135:
                alpha = 'azotea, aluminio, placa sencilla con eternit, o teja de barro'
            elif int(predios.iloc[U]['PreECubier']) == 136:
                alpha = 'placa impermeabilizada, cubierta lujosa u ornamental'
            return alpha

    def cerchas():
        '''
        '''
        if str(predios.iloc[U]['PreCIndus']) == 'nan':
            pass
        else:
            alpha = None
            if predios.iloc[U]['PreCIndus'] == 511:
                alpha = '''
                Caracterización de las cerchas: ''' + 'madera'
            elif predios.iloc[U]['PreCIndus'] == 512:
                alpha = 'Caracterización de las cerchas: ' + 'metálica liviana (luz menor a 10 m)'
            elif predios.iloc[U]['PreCIndus'] == 513:
                alpha = 'Caracterización de las cerchas: ' + 'metálica mediana (luz 10-20 m)'
            elif predios.iloc[U]['PreCIndus'] == 514:
                alpha = 'Caracterización de las cerchas: ' + 'metálica pesada (luz mayor a 20 )'
            elif predios.iloc[U]['PreCIndus'] == 521:
                alpha = 'Caracterización de las cerchas: ' + 'altura mayor a 7mts en columna - puente grúa'
            return alpha

    def tipo():
        '''Tipo de Predio según clasificación de la UAECD en función del propietario
        '''
        alpha = None
        for i in range(0,len(TUso.iloc[41:69,:])):
            if str(TUso.iloc[41:69,:].iloc[i].iloc[0]) == str(predios.iloc[U]['PreCDestin']):
                alpha = TUso.iloc[41:69,:].iloc[i].iloc[2]                 
                return alpha
            
    def edificabilidad():
        '''Si es zona de alto riesgo no mitigable, en cuyo caso hay peligro de la vida por remoción en masa
        '''
        alpha = None
        if str(predios.iloc[U]['PreCZHF'])[0] == '5' or str(predios.iloc[U]['PreCZHF'])[0] == '6':
            if str(predios.iloc[U]['PreCZHF'])[3:5] == '65':
                alpha = 'Tratamiento Urbanistico Zonas de alto Riesgo no mitigable'
            else:
                alpha = "No figura"
        return alpha


    CatastrO = [] #Lista con los datos de catastro
    for k in range(0,len(DireccioN)):
        tupla = 0
        if not len(predios) == 0:
            tupla = bloque1(), armazon(), muros(), cubierta(), estado_estructura(), fachada(), estado_acabados(), tipo(), topografia(), cerchas(), edificabilidad(), clase_suelo(), clase_vias(), estado_vias(), influencia_vias(), cubrimiento_muros(), acabado_pisos()
        CatastrO.append(tupla)


    if not type(construccion) == type(None):
        ConstruccioN = []
        ConstruccioN.append(construccion['ConNPisos'])
        ConstruccioN.append(construccion['ConTSemis'])
        ConstruccioN.append(construccion['ConNSotano'])

    material = CatastrO[0][1]  # Material

    try: # Numero maximo de pisos de la propiedad
            NPIS = max([int(temp)for temp in  str(ConstruccioN[0]).split() if temp.isdigit()])
    except:
            NPIS = ConstruccioN[0]

    if CatastrO[0][0][2] is not None: # Año de construccion de la propiedad
            RCON = int(CatastrO[0][0][2])
    else:
            RCON = 1999

    '''
    pararrayos_inc = ValoreS[0][26]
    red_electrica_inc = ValoreS[0][27]
    uso_inc = ValoreS[0][28]
    restaurantes_inc = ValoreS[0][29]
    act_incendio_inc = ValoreS[0][30]
    g_amen_pre_inc = ValoreS[0][31]
    distHidrante = ValoreS[0][0] # Distancia a los hidrantes
    distBomberos = ValoreS[0][6] # distancia al cuerpo de bomberos
    '''


    restaurantes_inc = ValoreS[0][0]
    act_incendio_inc = ValoreS[0][1]
    g_amen_pre_inc = ValoreS[0][2]
    distHidrante = ValoreS[0][3] # Distancia a los hidrantes
    distBomberos = ValoreS[0][4] # distancia al cuerpo de bomberos


    ##if (pararrayos_inc is None) or (pd.isna(pararrayos_inc) == True):
        ##pararrayos_inc = "Sin Información"

    ##if (red_electrica_inc is None) or (pd.isna(red_electrica_inc) == True):
        ##red_electrica_inc = "Sin Información"

    ##if (uso_inc is None) or (pd.isna(uso_inc) == True):
        ##uso_inc = "Sin Información"

    if (restaurantes_inc is None) or (pd.isna(restaurantes_inc) == True):
        restaurantes_inc = "Sin Información"

    if (act_incendio_inc is None) or (pd.isna(act_incendio_inc) == True):
        act_incendio_inc = "Sin Información"

    if (g_amen_pre_inc is None) or (pd.isna(g_amen_pre_inc) == True):
        g_amen_pre_inc = "Sin Información"

    ##if (material is None) or (pd.isna(material) == True):
        ##material = "Sin Información"

    if (distHidrante is None) or (pd.isna(distHidrante) == True):
        distHidrante_inc = "Sin Información"
    if distHidrante <= 10:
        distHidrante_inc = "Menor a 10 metros"
    elif distHidrante >= 11 and distHidrante <= 20:
        distHidrante_inc = "Entre 11 y 20 metros"
    elif distHidrante >= 21 and distHidrante <= 30:
        distHidrante_inc = "Entre 21 y 30 metros"
    elif distHidrante >= 31 and distHidrante <= 40:
        distHidrante_inc = "Entre 31 y 40 metros"
    else:
        distHidrante_inc = "Mayor a 41 metros"

    if (distBomberos is None) or (pd.isna(distBomberos) == True):
        distBomberos_inc = "Sin Información"
    if distBomberos <= 1000:
        distBomberos_inc = "Menor a 1 km"
    elif distBomberos >= 1000 and distBomberos <= 3000:
        distBomberos_inc = "Entre 1 km y 3 km"
    elif distBomberos >= 3000 and distBomberos <= 7000:
        distBomberos_inc = "Entre 3 km y 7 km"
    elif distBomberos >= 7000 and distBomberos <= 10000:
        distBomberos_inc = "Entre 7 km y 10 km"
    else:
        distBomberos_inc = "Mayor a 10 km"

    if (RCON is None) or (pd.isna(RCON) == True):
        RCON_inc = "Sin Información"
    if RCON < 1985:
        RCON_inc = "Previo a 1985"
    elif RCON >= 1985 and RCON <= 1997:
        RCON_inc = "Entre 1985 y 1997"
    elif RCON >= 1998 and RCON <= 2010:
        RCON_inc = "Entre 1998 y 2010"
    elif RCON >= 2011 and RCON <= 2022:
        RCON_inc = "Entre 2011 y 2022"
    else:
        RCON_inc = "Posterior a 2022"

    '''
    if (NPIS is None) or (pd.isna(NPIS) == True):
        NPIS_inc = "Sin Información"
    if NPIS == 1:
        NPIS_inc = "1 Piso"
    elif NPIS >= 2 and NPIS <= 3:
        NPIS_inc = "Entre 2 y 3 pisos"
    elif NPIS >= 4 and NPIS <= 7:
        NPIS_inc = "Entre 4 y 7 pisos"
    elif NPIS >= 8 and NPIS <= 15:
        NPIS_inc = "Entre 8 y 15 Pisos"
    elif NPIS >= 16 and NPIS <= 25:
        NPIS_inc = "Entre 16 y 25 pisos"
    elif NPIS >= 26 and NPIS <= 35:
        NPIS_inc = "Entre 26 y 35 pisos"
    else:
        NPIS_inc = "Mas de 35 pisos"
    '''
    if any(int(ciiu_numero[0]) == Politicas["CODIGO CIIU"]):
        politicas_incendio = Politicas["Politicas Incendio"][Politicas["CODIGO CIIU"]==int(ciiu_numero[0])].iloc[0]
        if politicas_incendio == "Sin Información":
            politicas_incendio = Politicas["Calificación PR"][Politicas["CODIGO CIIU"]==int(ciiu_numero[0])].iloc[0]
    else:
        politicas_incendio = "Sin Información"

    '''
    Fila = [RCON_inc, NPIS_inc, material, distHidrante_inc, distBomberos_inc, pararrayos_inc, red_electrica_inc,
        uso_inc, restaurantes_inc, act_incendio_inc, g_amen_pre_inc, politicas_incendio]

    Fila2 = [RCON_inc, NPIS_inc, material, distHidrante_inc, distBomberos_inc,
        g_amen_pre_inc, politicas_incendio]
    '''
    Fila = [RCON_inc, distHidrante_inc, distBomberos_inc, g_amen_pre_inc, politicas_incendio, restaurantes_inc, act_incendio_inc]
    
    Fila2 = [RCON_inc, distHidrante_inc, distBomberos_inc, g_amen_pre_inc, politicas_incendio]

    riesgosCon = []

    fila = Fila
    fila2 = Fila2

    a = 0
    riesgoIncendioPeso = 0

    if (restaurantes_inc == "Sin Información") and (act_incendio_inc == "Sin Información"):
                # Recorre la cantidad de posibles respuestas del modelo
        for i in range(0, len(ModeloSinManz)):

        # Recorre la cantidad de variables del modelo (12)
            for j in range(0, len(NombreVariables2)):
            # Valida que la fila sea igual a una de las variables y que la respuesta sea igual a la columna
                if ModeloSinManz.iloc[i][0] == NombreVariables2[j]:
                    if ModeloSinManz.iloc[i][1] == fila2[j]:
                        print(ModeloSinManz.iloc[i][1]+ " = " + str(ModeloSinManz.iloc[i][3]))
                        a = a + 1
                        riesgoIncendioPeso =  riesgoIncendioPeso + ModeloSinManz.iloc[i][3] * ModeloSinManz.iloc[i][4]
        print("Direccion =", DireccioN[0])
        riesgosCon.append(round(riesgoIncendioPeso, 2))
        print("")
        print("Ponderacion =", riesgosCon[0])
        print("Longitud", Longitud)
        print("Latitud", Latitud)

    else:
        # Recorre la cantidad de posibles respuestas del modelo
        for i in range(0, len(ModeloCompleto)):

        # Recorre la cantidad de variables del modelo (12)
            for j in range(0, len(NombreVariables)):
            # Valida que la fila sea igual a una de las variables y que la respuesta sea igual a la columna
                if ModeloCompleto.iloc[i][0] == NombreVariables[j]:
                    if ModeloCompleto.iloc[i][1] == fila[j]:
                        print(ModeloCompleto.iloc[i][1]+ " = " + str(ModeloCompleto.iloc[i][3]))
                        a = a + 1
                        riesgoIncendioPeso =  riesgoIncendioPeso + ModeloCompleto.iloc[i][3] * ModeloCompleto.iloc[i][4]

        print("Direccion =", DireccioN[0])
        riesgosCon.append(round(riesgoIncendioPeso, 2))
        print("")
        print("Ponderacion =", riesgosCon[0])
        print("Longitud", Longitud)
        print("Latitud", Latitud)
    
    conceptoIncendio = "Sin info"
    nivelIncendio = "Sin info"

    if riesgosCon[0] <= 3.13:
        conceptoIncendio = "Asegurable"
        nivelIncendio = "Bajo"
    if 3.13 < riesgosCon[0] <= 3.30:
        conceptoIncendio = "Asegurable"
        nivelIncendio = "Medio Bajo"
    if 3.31 < riesgosCon[0] <= 3.46:
        conceptoIncendio = "Asegurable"
        nivelIncendio = "Medio"
    if 3.47 < riesgosCon[0] <= 3.62:
        conceptoIncendio = "Asegurable"
        nivelIncendio = "Medio Alto"
    if 3.63 < riesgosCon[0]:
        conceptoIncendio = "No asegurable"
        nivelIncendio = "Alto"

    
    mjs = {
        "Direccion": f'{DireccioN[0]}',
        "NIT": f'{nit}',
        "Latitud": f'{Latitud}',
        "Longitud": f'{Longitud}',
        "Año de construccion": f'{RCON}',
        "Material": f'{material}',
        "Cumulo de Restaurantes": f'{restaurantes_inc}',
        "Actividades Incendio": f'{act_incendio_inc}',
        "Amenaza Incidentes Incendio": f'{g_amen_pre_inc}',
        "Distancia a Hidrantes": f'{distHidrante}',
        "Distancia a Bomberos": f'{distBomberos}',
        "Politicas Incendio": f'{politicas_incendio}',
        "Nivel Incendio": f'{nivelIncendio}',
        "Concepto Incendio": f'{conceptoIncendio}',
        "Ponderacion": f'{riesgosCon[0]}',
                
    } 

    return JSONResponse(status_code=200, content=mjs)




################################ ID GENERICO #################################

@app.get('/API/GenerarInforme/ID GENERICO')
async def StandAlone(ciudad:str = None, departamento:str = None, direccion:str = None, latitud:str = None, longitud:str = None, nit: str = None, valor_a_asegurar: str = None, chip: str = None):
    
    inicio = time.time()


    # Estandarizacion del NIT
    if not type(nit) == type(None):
        nit = nit.replace('.','')
        nit = nit.replace(',','')
    

    # Almacenamiento de variables
    workbook = xlsxwriter.Workbook('Archivos/save2.xlsx')
    worksheet = workbook.add_worksheet('first')

    worksheet.write(1,0, direccion)
    worksheet.write(1,1, ciudad)
    worksheet.write(1,2, nit)
    worksheet.write(1,3, valor_a_asegurar)
    worksheet.write(1,4, latitud)
    worksheet.write(1,5, longitud)
    worksheet.write(1,6, chip)
    worksheet.write(1,7, departamento)

    worksheet.write(0,0, 'direccion')
    worksheet.write(0,1, 'ciudad')
    worksheet.write(0,2, 'nit')
    worksheet.write(0,3, 'valor')
    worksheet.write(0,4, "latitud")
    worksheet.write(0,5, "longitud")
    worksheet.write(0,6, "CHIP")
    worksheet.write(0,7, "departamento")

    workbook.close()
    
    print(f"La dirección es: {direccion}")
    print(f"El NIT es: {nit}")

    # Conteo de usos en la plataforma
    with open('Archivos/save.txt', 'a') as istr:
        istr.write(',1')
    with open('Archivos/save.txt', 'r') as istr:
        for line in istr:
            print(sum(map(int, line.split(','))))

    # Imprimir el mes con un 0 antes
    now = datetime.now()
    if len(str(now.month)) == 1:
        here = str(0) + str(now.month)


    import geopandas as gpd
    import psycopg2
    
    con = psycopg2.connect(database="ingdigital", user="postgres", password="Bolivar2021",
        host="35.153.192.47", port=8081)

    # Lectura de datos de entrada
    save2 = pd.read_excel("Archivos/save2.xlsx") 

    DireccioN = []
    

    # LIMPIEZA DE INFORMACION DE ENTRADA

    # Estandarizar direccion
    for i in range(0, len(save2)):
        direccion = save2.iloc[i].iloc[0]
        if not str(save2.iloc[i].iloc[0]) == 'nan':
            #direccion = direccion.replace(",", "")
            direccion = direccion.upper()
            direccion = direccion.replace("Á","A")
            direccion = direccion.replace("É","E")
            direccion = direccion.replace("Í","I")
            direccion = direccion.replace("Ó","O")
            direccion = direccion.replace("Ú","U")
            DireccioN.append(direccion)
        else:
            DireccioN.append('None')

    # Estandarizar ciudad
    Ciudad = []
    for i in range(0,len(save2)):
        ciudad = save2.iloc[i].iloc[1]
        if str(ciudad) == 'nan':
            ciudad = ""
        if not (str(ciudad) == 'nan' or type(ciudad) == None):
            ciudad = ciudad.upper()
            ciudad = ciudad.replace("Á", "A")
            ciudad = ciudad.replace("É", "E")
            ciudad = ciudad.replace("Í", "I")
            ciudad = ciudad.replace("Ó", "O")
            ciudad = ciudad.replace("Ú", "U")
        Ciudad.append(ciudad)
    
    # Estandarizar departamento
    Departamento = []
    for i in range(0,len(save2)):
        departamento = save2.iloc[i].iloc[7]
        if str(departamento) == 'nan':
            departamento = ""
        if not (str(departamento) == 'nan' or type(departamento) == None):
            departamento = departamento.upper()
            departamento = departamento.replace("Á", "A")
            departamento = departamento.replace("É", "E")
            departamento = departamento.replace("Í", "I")
            departamento = departamento.replace("Ó", "O")
            departamento = departamento.replace("Ú", "U")
        Departamento.append(departamento)

    # Estandarizacion del NIT, CHIP, etc.
    NiT = []
    for i in range(0,len(save2)):
        nit = save2.iloc[i].iloc[2]
        if not (type(nit) == type(None) or str(nit) == 'nan'):
            nit = int(str(nit).replace('.',''))
            nit = int(str(nit).replace(',',''))
        NiT.append(nit)
    ValoR = []
    for i in range(0,len(save2)):
        valor = save2.iloc[i].iloc[3]
        ValoR.append(valor)
    LatituD = []
    for i in range(0,len(save2)):
        gamma = save2.iloc[i].iloc[4]
        if not (str(gamma) == 'nan' or type(gamma) == type(None)):
            gamma = float(str(gamma).replace(',','.'))
        LatituD.append(gamma) #
    LongituD = []
    for i in range(0,len(save2)):
        eta = save2.iloc[i].iloc[5]
        if not (str(eta) == 'nan' or type(eta) == type(None)):
            eta = float(str(eta).replace(',','.'))
        LongituD.append(eta)
    ChiP = []
    for i in range(0,len(save2)):
        chip = save2.iloc[i].iloc[6]
        ChiP.append(chip)


    # ESTANDARIZADOR

    CarrerA = ["CARRERA", "CRA", "K", "KRA", "K.", "CRA.", "KRA.", "KR.", "CR"]
    CallE = ["CLL", "CALLE", "CL.", "CLL.", "C.", "KALLE"]
    DiagonaL = ["DIAGONAL", "DG.", "DIAG.", "DIAG", "D.", "DGL", "DGL."]
    TransversaL = ["TRANSVERSAL", "TV.", "TR.", "T.", "TRANS.", "TRR", "T", "TRANS", "TR"]
    AvenidA = ["AVENIDA", "AV.", "A.", "AVD", "AVDA"]
    AvenidaCalle = ["AV CL", "AC."]
    AvenidaCarrera = ["AK.", "AV KR"]
    Bodega = ["BODEGA", "BG.", "BOD", "BOD.", "BODEGAS", "BOEGAS", "BODG2", "BOEGA", "BD", "PLANTA"]
    Local = ["LOCAL", "LC.", "LOC", "LOCALES", "LOC."]
    Interior = ["INTERIOR", "INT", "INT.", "IN."]
    Apartamento = ["APT.", "AP.", "APARTAMENTO", "APT", "APTO", "APTO."]
    Oficina = ["OFICINA", "OF.", "OFICINAS", "CONSULTORIO", "CONSULT.", "CONSULT", "0FIC", "OFOF", "0F", "OFC", "OFC."]
    Torre = ["TORRE", "TO."]
    Lote = ["LOTE", "LOT", "LOT."]
    for i in range(0,len(DireccioN)):
        for j in range(0, len(CarrerA)):
            if CarrerA[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(CarrerA[j] + " ", "KR ")
                break
        for j in range(0, len(CallE)):
            if CallE[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(CallE[j] + " ", "CL ")
                break
        if not " BIS" in DireccioN[i]:
            if "BIS" in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace("BIS", " BIS")
        if "ª" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("ª", "")
        if "#" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" #", " ")
        elif "#" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("#", "")
        elif "NO." in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" NO. ", " ")
        elif "N°" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" N° ", " ")
        elif "Nº" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" Nº ", " ")
        elif "NO" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" NO ", " ")
        elif "NO." in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("NO.", "")
        elif "N°" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("N°", "")
        elif "Nº" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("Nº", "")
        if "-" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" - ", " ")
        elif "-" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("-", " ")
        if "—" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" — ", " ")
        elif "—" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("—", " ")
        if "−" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" − ", " ")
        elif "−" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("−", " ")
        if "–" in DireccioN[i].split():
            DireccioN[i] = DireccioN[i].replace(" – ", " ")
        elif "–" in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("–", " ")
        for j in range(0, len(DiagonaL)):
            if DiagonaL[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(DiagonaL[j] + " ", "DG ")
                break
        for j in range(0, len(TransversaL)):
            if TransversaL[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(TransversaL[j] + " ", "TV ")
                break
        for j in range(0, len(AvenidA)):
            if AvenidA[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(AvenidA[j] + " ", "AV ")
                break
        for j in range(0, len(Bodega)):
            if Bodega[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(Bodega[j] + " ", "BG ")
        for j in range(0, len(Local)):
            if Local[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(Local[j] + " ", "LC ")
        for j in range(0, len(Apartamento)):
            if Apartamento[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(Apartamento[j] + " ", "AP ")
        for j in range(0, len(Oficina)):
            if Oficina[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(Oficina[j] + " ", "OF ")
            elif Oficina[j] in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace(Oficina[j], "OF ")
        for j in range(0, len(Torre)):
            if Torre[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(Torre[j] + " ", "TO ")
        for j in range(0, len(Lote)):
            if Lote[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(Lote[j] + " ", "LT ")
        for j in range(0, len(Interior)):
            if Interior[j] in DireccioN[i].split():
                DireccioN[i] = DireccioN[i].replace(Interior[j] + " ", "IN ")
                break
        for j in range(0, len(AvenidaCalle)):
            if AvenidaCalle[j] in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace(AvenidaCalle[j] + " ", "AC ")
                break
        for j in range(0, len(AvenidaCarrera)):
            if AvenidaCarrera[j] in DireccioN[i]:
                DireccioN[i] = DireccioN[i].replace(AvenidaCarrera[j] + " ", "AK ")
                break
        if "   " in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("   ", " ")
        if "  " in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("  ", " ")
        if "   " in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("   ", " ")
        if "  " in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("  ", " ")
        if "  " in DireccioN[i]:
            DireccioN[i] = DireccioN[i].replace("  ", " ")

    '''
    Apiest = 'http://ec2-35-153-192-47.compute-1.amazonaws.com:8092/API/1a1'
    args = {'Ciudad' : 'Bogota', 'Direccion': direccion}
    response = requests.get(Apiest, params = args)
    DireccioN[0] = response.json()['DIRECCION_ESTANDAR']['0']
    nDireccion = []
    for i in DireccioN[0]:
        nDireccion.append((i))
        
    letras = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "O", "P", "Q"]
    a = 0
    for i in ((DireccioN[0])):
        for j in range (len(letras)):
            try:
                if letras[j] == i and nDireccion[a-1] == " ":
                    nDireccion.pop(a-1)
            except:
                pass
        a = a+1
    DireccioN[0] = "".join(nDireccion)
    '''


    # GENERACION DE LAS COORDENADAS A PARTIR DE LA DIRECCION

    geolocalizador = 'https://www.segurosbolivar.com/arcgis/rest/services/Servicios_SB/geoEsri/GPServer/geoEsri/execute'

    geolocalizador_entrada = {'direccion': DireccioN[0],
                'ciudad': Ciudad[0].upper().replace('Á', 'A'), 'f': 'json'}
                
    geolocalizador_salida = requests.get(url=geolocalizador,
                        headers={'content-type': 'application/json'},
                        params=geolocalizador_entrada)
    print(geolocalizador_salida)
    if not len(geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')) == 1:
            try:
                LatituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[0]
                LongituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[1]
            except:
                urlGeocode = 'http://api.lupap.co/v2/co/'
                temp = requests.get(urlGeocode  + '?a=' + direccion+'&key=3bee5f0a19bf31eb0fa8a70376a4c61eb34d9ba8')
                LatituD[0] = temp.json()['response']['geometry']['coordinates'][1]
                LongituD[0] = temp.json()['response']['geometry']['coordinates'][0]
                

    # Intento con la direccion sin estandarizar
    geolocalizador_entrada = {'direccion': DireccioN[0],
                'ciudad': Ciudad[0].upper().replace('Á', 'A'), 'f': 'json'}

    geolocalizador_salida = requests.get(url=geolocalizador,
                        headers={'content-type': 'application/json'},
                        params=geolocalizador_entrada)
    if not len(geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')) == 1:
            try:
                LatituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[0]
                LongituD[0] = geolocalizador_salida.json()['results'][0]['value'].replace('latitud: ', '').replace('|',',').replace('longitud:','').replace(',fuente:Esri','').split(',')[1]
            except:
                urlGeocode = 'http://api.lupap.co/v2/co/'
                temp = requests.get(urlGeocode + '?a=' + direccion+'&key=3bee5f0a19bf31eb0fa8a70376a4c61eb34d9ba8')
                LatituD[0] = temp.json()['response']['geometry']['coordinates'][0]
                LongituD[0] = temp.json()['response']['geometry']['coordinates'][1]
        

    # Asignacion de la direccion, longitud y latitud generadas
    DIRECCION = DireccioN[0]
    LATITUD = LatituD[0]
    LONGITUD = LongituD[0]
    
 

# 1) INFORMACION EMPRESARIAL

    modelo = 'Perfil cliente'

    version = '2.0'

    ramo = "Property"

    poliza = "Daños materiales"

    country = "Colombia"

    alcance = "Suscripción, renovación, prevención y comerciales"

    division = "Empresas"

    ciiu = pd.read_excel(r"Archivos/Estructura-detallada-CIIU-4AC-2020-.xls")
    ciiu_Politicas = pd.read_excel(r"Archivos/Politicas_ID.xlsx")
    # Se lee el excel con los datos de entrada
    # save2 = pd.read_excel("/home/ingeniero_digital/principal/PLATAFORMA/plataforma_proyecto/biblioteca_modelos/save2.xlsx")

    nit = save2.iloc[0].iloc[2]
    if str(nit) == 'nan':
        nit = 0

    # Informacion suministrada por el DANE
    sql_dane = f"""SELECT * FROM dane_2020
    WHERE "NIT" = '{int(nit)}'"""
    dane = pd.read_sql(sql_dane, con) 

    # Informacion suministrada por EMIS
    sql_emis = f"""SELECT * FROM emis_0521
    WHERE "n_id" = '{int(nit)}'"""
    emis = pd.read_sql(sql_emis, con) 

    razon_social = 'None'
    IsAseg = True
    IsAlerta = False
    ciiu_dado = []
    ciiu_numero = []
    departamento_principal = 'None'
    direccion_principal = 'None'
    ciudad_principal = 'None'
    telefono_principal = 'None'
    telefono2_principal = 'None'
    nombre_comercial = 'None'

    if not len(dane) == 0: 
        razon_social = dane['RAZON_SOCIAL'].iloc[0]
        nombre_comercial = None
        for i in range(0,len(dane)):
            if not str(dane['NOMBRE_COMERCIAL'].iloc[i]) == 'nan':
                nombre_comercial = dane['NOMBRE_COMERCIAL'].iloc[i]
        direccion_principal = dane['DIRECCION'].iloc[0]
        departamento_principal = dane['NOMBRE_DPTO'].iloc[0]
        ciudad_principal = dane['NOMBRE_MPIO'].iloc[0]
        telefono_principal = str(int(dane['TELEFONO1'].iloc[0]))
        telefono2_principal = str(int(dane['TELEFONO1'].iloc[0]))

        def match_ciiu(self):
            '''Retorna el índice de la actividad económica correspondiente al código CIIU
            params:
            self = código CIIU correspondiente al NIT
            '''
            for index, s in enumerate(ciiu['Unnamed: 2']):
                if str(s) == str(self) or str(s) == '0' + str(self):
                    return index, s
                    break
                elif str(self)[:3] == str(ciiu['Unnamed: 3'].iloc[index]) or str(self) == '0' + str(ciiu['Unnamed: 3'].iloc[index]):
                    return index, ciiu['Unnamed: 1'].iloc[index]

        for i in range(0, len(dane)):
            print(ciiu_dado)
            ciiu_dado.append(ciiu['Unnamed: 3'].iloc[match_ciiu(int(dane['CIIU_ID_CIIU_4'].iloc[i]))[0]])
        for i in range(0, len(dane)):
            ciiu_numero.append(str(int(dane['CIIU_ID_CIIU_4'].iloc[i])))
            
    ciiu_numero_float = [float(x) for x in ciiu_numero]

    filtro = ciiu_Politicas["CIIU"].isin(ciiu_numero_float)
    riesgos_politicas = ciiu_Politicas[filtro]

    ciiu_numero_index = {float(numero): index for index, numero in enumerate(ciiu_numero)}

    riesgos_politicas["CIIU"] = riesgos_politicas["CIIU"].astype(float)
    riesgos_politicas["Order"] = riesgos_politicas["CIIU"].map(ciiu_numero_index)
    riesgos_politicas = riesgos_politicas.sort_values("Order")

    riesgos_politicas = riesgos_politicas.drop(columns=["Order"])
    print(riesgos_politicas[["CIIU", "Incendio", "All Risk", "Sustracción", "R.M", "E.E", "Manejo", "RC"]])
    
    for ciiu_principal in ciiu_numero:
        ciiu_principal_float = float(ciiu_principal)
        filtro2 = ciiu_Politicas["CIIU"].eq(ciiu_principal_float)
        riesgos_pp = ciiu_Politicas[filtro2]
        
        if not riesgos_pp.empty:

            if any(riesgos_politicas[col].iloc[0] == 5.0 for col in ["CIIU","Incendio", "All Risk", "Sustracción","R.M","E.E", "Manejo", "RC"]):
                IsAseg = False
                print("No es asegurable por políticas")

            if any((riesgos_politicas[col].iloc[1:] == 5.0).any() for col in ["CIIU","Incendio", "All Risk", "Sustracción","R.M","E.E", "Manejo", "RC"]):
                IsAlerta = True
                print("Se genera alerta por riesgo en actividades secundarias")
            elif IsAseg == True:
                print("Es asegurable según políticas")

        if riesgos_pp.empty:
            print("La lista está vacía")
  

    #coding: utf-8
    #Biblioteca de Modelos

    modelo = 'Modelo de integración'

    version = '1.0'

    ramo = "Property"

    poliza = "Daños materiales"

    country = "Colombia"

    alcance = "Suscripción y prevención"

    division = "Empresas"

    #https://2.python-requests.org/es/latest/user/quickstart.html
    EntradaApiMapas = {'latitud': str(LATITUD),
            'longitud': str(LONGITUD), 'f': 'json'}

    # API Mapas Servicio de Manzaneo
    ApiMapas = 'https://www.segurosbolivar.com/arcgis/rest/services/Servicios_SB/ingDigVerDos/GPServer/ingDig/execute'

    resultado_api_mapas = requests.get(url=ApiMapas,
                    headers={'content-type': 'application/json'},
                    params=EntradaApiMapas)
    EntradaManzaneoPymes = {'latitud': str(LATITUD),
            'longitud': str(LONGITUD), 'f': 'json'}

    print("ESTA ES LA DIRECCION ", DIRECCION)
    print("ESTA ES LA LATITUD", LATITUD)
    print("ESTA ES LA LONGITUD", LONGITUD)
    if resultado_api_mapas.status_code == 200:
        print('Éxitoso')
    else:
        print('Hay un error')
    alpha = resultado_api_mapas.json() # alpha es el que debe variar para múltiples solicitudes
    MatrizAmenazas = []
    ValoreS = []

    if "error" in alpha.keys():
        print("Error")
        MatrizAmenazasManzaneo = []
        MatrizAmenazas = []
        pass
    else:
        if not alpha['results'][0]['value']['features'] == []:
            

            MatrizAmenazasManzaneo = [alpha['results'][0]['value']['features'][0]['attributes']['INCENDIO'], 
            alpha['results'][0]['value']['features'][0]['attributes']['SUSTRACCION'], 
            alpha['results'][0]['value']['features'][0]['attributes']['ANEGACION'], 
            alpha['results'][0]['value']['features'][0]['attributes']['TERREMOTO'], 
            alpha['results'][0]['value']['features'][0]['attributes']['AMIT'],
            alpha['results'][0]['value']['features'][0]['attributes']['DANO_ELECT'], 
            alpha['results'][0]['value']['features'][0]['attributes']['VIENTOS']]
            

            MatrizAmenazas= [alpha['results'][0]['value']['features'][0]['attributes']['TERREMO'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['VIENTO'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['REMOCI'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['SUSTRA'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['ORDENPU'].capitalize(),
            alpha['results'][0]['value']['features'][0]['attributes']['RAYO'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['INUNDA'].capitalize(), 
            alpha['results'][0]['value']['features'][0]['attributes']['AMIT_1'].capitalize()]
            
            ValoreS = [alpha['results'][0]['value']['features'][0]['attributes']['Material'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Nombre_1'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Dirección'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Teléfonos'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Descripción'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Horario'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Direccion_Sitio'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Telefono'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Correo_Electronico'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Descripción_1'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Dirección_Sitio'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Telefono_1'],
                    alpha['results'][0]['value']['features'][0]['attributes']['Correo_Electronico_1'],                        
                    alpha['results'][0]['value']['features'][0]['attributes']['Presion'],
                    alpha['results'][0]['value']['features'][0]['attributes']['NIVEL_SUST'],
                    alpha['results'][0]['value']['features'][0]['attributes']['PARARRAYOS'],
                    alpha['results'][0]['value']['features'][0]['attributes']['RED_ELECTRICA'],
                    alpha['results'][0]['value']['features'][0]['attributes']['USO'],
                    alpha['results'][0]['value']['features'][0]['attributes']['RESTAURANTES'],
                    alpha['results'][0]['value']['features'][0]['attributes']['ACT_INCENDIO'],
                    alpha['results'][0]['value']['features'][0]['attributes']['SIST_EST'],
                    alpha['results'][0]['value']['features'][0]['attributes']['EDAD'],
                    alpha['results'][0]['value']['features'][0]['attributes']['DIS_HIDRA'],
                    alpha['results'][0]['value']['features'][0]['attributes']['DIS_BOMBERO']]

    print("paso cuadro de amenaza")
    
    RCON1 = ["<1985", "MENOR A 1985"]
    RCON2 = ["1985 A 1997", "1985 Y 1997"]
    RCON3 = ["1998 A 2010", "1998 Y 2010"]
    RCON4 = [">2010", "MAYOR A 2010"]
    
    if(len(ValoreS) < 1):
        print("No hay información del manzaneo")
        ValoreS = [None]
        rango_año_construccion = "Sin información"
    else:
        for i, val in enumerate(ValoreS):
            if val == None:
                print(f"La variable número: {i} es None")
        if not ValoreS[21] == None:
            for j in range(0, len(RCON1)):
                if RCON1[j] == ValoreS[21]:
                    ValoreS[21] = ValoreS[21].replace(RCON1[j], "PREVIO A 1985")
                    break
            for j in range(0, len(RCON2)):
                if RCON2[j] == ValoreS[21]:
                    ValoreS[21] = ValoreS[21].replace(RCON2[j], "ENTRE 1985 Y 1997")
                    break    
            for j in range(0, len(RCON3)):
                if RCON3[j] == ValoreS[21]:
                    ValoreS[21] = ValoreS[21].replace(RCON3[j], "ENTRE 1998 Y 2010")
                    break
            for j in range(0, len(RCON4)):
                if RCON4[j] == ValoreS[21]:
                    ValoreS[21] = ValoreS[21].replace(RCON4[j], "POSTERIOR A 2010")
                    break
            print(ValoreS[21])
            rango_año_construccion = ValoreS[21]
        else:
            rango_año_construccion = "Sin información"


    ConceptoManzaneo = [None]
   
    try:
        if not alpha["results"][0]["value"]["features"] == []:
            ConceptoManzaneo = []
            ConceptoManzaneo.append(alpha["results"][0]["value"]["features"][0]["attributes"]['PROHIB'])
    except:
            ConceptoManzaneo = ["Sin informacion"]    
    # 2) RIESGOS CATASTROFICOS
    
    colors = ['rgb(51.0, 128.0, 0.0)', 'rgb(102.0, 128.0, 0.0)', 'rgb(128.0, 102.0, 0.0)', 'rgb(128.0, 51.0, 0.0)', 'rgb(128.0, 0.0, 0.0)']
    colors2 = n_colors('rgb(249, 249, 249)', 'rgb(179, 179, 179)', 5, colortype='rgb')
    ame = []
    for i in range(0, len(MatrizAmenazas)):
        if (MatrizAmenazas[i].lower() == "bajo" or MatrizAmenazas[i].lower() == "baja" or MatrizAmenazas[i].lower() == "baja o muy baja"):
            ame.append(0)
        elif (MatrizAmenazas[i].lower() == "media baja" or MatrizAmenazas[i].lower() == "medio bajo" or MatrizAmenazas[i].lower() == "medio-bajo"):
            ame.append(1)
        elif (MatrizAmenazas[i].lower() == "media" or MatrizAmenazas[i].lower() == "medio"):
            ame.append(2)
        elif (MatrizAmenazas[i].lower() == "media alta" or MatrizAmenazas[i].lower() == "medio alto" or MatrizAmenazas[i].lower() == "medio-alto"):
            ame.append(3)
        elif (MatrizAmenazas[i].lower() == "alto" or MatrizAmenazas[i].lower() == "alta"):
            ame.append(4)
        elif (MatrizAmenazas[i].lower() == "sin información" or MatrizAmenazas[i].lower() == "sin informacion"):
            ame.append(0)
    
    if len(MatrizAmenazas) == 0:
        MatrizAmenazas = [None] 
    #####################

    #Tabla de color con las amenazas

    goldbach = pd.concat([pd.Series(["Terremoto", "Vientos", "Remoción en masa", "Sustracción", "Orden público", "Rayos", "Inundación", "AMIT"]), pd.Series(ame), pd.Series(MatrizAmenazas)], axis=1).sort_values(by=[1],axis=0)
    goldbach = goldbach.fillna(value={1:"0"})
    goldbach[1] = goldbach[1].astype(int)


    fig = go.Figure(data=[go.Table(header=dict(align=['right','center'],values=['AMENAZA', 'NIVEL'],     line_color='rgb(249,249,249)', fill_color='rgb(249,249,249)',font=dict(color='black', size=10)),
                    cells=dict(align=['right','center'],values=[goldbach[0], goldbach[2]],
                        line_color=[np.array(colors2)[goldbach[1]],np.array(colors)[goldbach[1]]],
        fill_color=[np.array(colors2)[goldbach[1]],np.array(colors)[goldbach[1]]], font=dict(color=["black", "white"], size=10)))
        ])

    fig.update_layout(
        autosize=True,
        width=360.6,
        height=206.4,
            margin=dict(
            l=0,
            r=0,
            b=0,
            t=6.4,
            pad=4
        ),
        paper_bgcolor="rgb(249,249,249)",
    )
    print("paso la tabla")
    fig.write_image("Archivos/PNG/ID_GENERICO/" + str(DireccioN[0]) + "_tabla" + ".png", scale=2) # scale=4
    
# MATRIZ MANZANEO    

    

    ameManz = []
    ameManzIn = ["No hay información"]
    IsNone = False
    if MatrizAmenazasManzaneo:
        for i, elem in enumerate(MatrizAmenazasManzaneo):
            try:
                if elem is not None:
                    IsNone = True
                    print("No es None")
                    if (elem.lower() == "bajo" or elem.lower() == "baja" or elem.lower() == "baja o muy baja"):
                        ameManz.append(0)
                    elif (elem.lower() == "media baja" or elem.lower() == "medio bajo" or elem.lower() == "medio-bajo"):
                        ameManz.append(1)
                    elif (elem.lower() == "media" or elem.lower() == "medio"):
                        ameManz.append(2)
                    elif (elem.lower() == "media alta" or elem.lower() == "medio alto" or elem.lower() == "medio-alto"):
                        ameManz.append(3)
                    elif (elem.lower() == "alto" or elem.lower() == "alta"):
                        ameManz.append(4)
                    elif (elem.lower() == "sin información" or elem.lower() == "sin informacion"):
                        ameManz.append(0)
                elif elem is None:
                    IsNone = False
                    print("Es none")
                    print(ameManzIn)
            except AttributeError as e:
                print(f"Error en el índice {i}: {e}")
    else:
        MatrizAmenazasManzaneo = ["Sin información"] * 7

    MatrizAmenazasManzaneo = ["Sin información" if pd.isna(val) else val for val in MatrizAmenazasManzaneo]

    goldbach = pd.concat([pd.Series(["Incendio_M", "Sustraccion_M", "Anegacion_M", "Terremoto_M", "AMIT_M", "Daño Electrico_M", "Vientos_M"]), pd.Series(ameManz), pd.Series(MatrizAmenazasManzaneo)], axis=1).sort_values(by=[1], axis=0)
    goldbach = goldbach.fillna(value={1: "0"})
    goldbach[1] = goldbach[1].astype(int)


    fig2 = go.Figure(data=[go.Table(header=dict(align=['right','center'],values=['AMENAZA', 'NIVEL'],     line_color='rgb(249,249,249)', fill_color='rgb(249,249,249)',font=dict(color='black', size=10)),
                    cells=dict(align=['right','center'],values=[goldbach[0], goldbach[2]],
                        line_color=[np.array(colors2)[goldbach[1]],np.array(colors)[goldbach[1]]],
        fill_color=[np.array(colors2)[goldbach[1]],np.array(colors)[goldbach[1]]], font=dict(color=["black", "white"], size=10)))
        ])

    fig2.update_layout(
        autosize=True,
        width=300.6,
        height=200.4,
            margin=dict(
            l=0,
            r=0,
            b=0,
            t=6.4,
            pad=4
        ),
        paper_bgcolor="rgb(249,249,249)",
    )
    print("paso tabla")



    fig2.write_image("Archivos/PNG/ID_GENERICO/" + str(DireccioN[0]) + "_tablaM" + ".png", scale=2) # scale=4

    class PDF(FPDF):
        def footer(self):
            self.set_y(-0.59)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128)
            self.cell(0, .4, 'Page ' + str(self.page_no()), 0, 0, 'C')

    # AMENAZAS

    # Amenaza de terremoto
    amenaza_terremoto = None
    if not MatrizAmenazas == []:
        amenaza_terremoto = MatrizAmenazas[0]
        if "MEDIO-BAJO" in amenaza_terremoto.upper():
            amenaza_terremoto = 2
        elif "MEDIO-ALTO" in amenaza_terremoto.upper():
            amenaza_terremoto = 4
        elif "BAJO" in amenaza_terremoto.upper():
            amenaza_terremoto = 1
        elif "MEDIO" in amenaza_terremoto.upper():
            amenaza_terremoto = 3
        elif "ALTO" in amenaza_terremoto.upper():
            amenaza_terremoto = 5

    amenaza_terremoto_niveles_descripcion = "bajo < 0.3 G, medio-bajo 0.3 < Sa <== 0.4 G, medio 0.4 < Sa <== 0.7 G, medio alto 0.7 < Sa <== 0.8 G, alto Sa > 0.8 G"
    terremoto_riesgo = None


    # Base de datos SIRE
    sql_sire = f"""SELECT * FROM "SIRE_0221"
    WHERE STRPOS("Dirección", '{DIRECCION}') = 1"""
    sire = pd.read_sql(sql_sire, con) 

    # Texto para el PDF
    alerta_sire = f"""Alerta SIRE:
    {sire[["Fecha reporte", "Tipo de afectación"]]}.
Concepto manzaneo: {ConceptoManzaneo[0]}
"""
    perfil_txt = ""
    perfil_emis = ""
    if not list(razon_social) == []:
        perfil_txt = f"""Razón social: {razon_social}
Actividad económica: {ciiu_numero} {ciiu_dado}.
Departamento: {departamento_principal}, ciudad: {ciudad_principal}, dirección principal: {direccion_principal}, teléfono(s): {telefono_principal} / {telefono2_principal}
"""
    perfil_emis = f"""{emis}"""

    if not nombre_comercial == None:
        tomador = nombre_comercial
    else:
        tomador = razon_social
    input = f"""{DireccioN[0]}
{ciudad}
Latitud, longitud: {[LATITUD, LONGITUD]}
NIT: {nit}
{tomador}
Valor a asegurar: {valor_a_asegurar}
"""


    # Base de datos del SIAR
    sql_siar = f"""SELECT * FROM "SIAR_BD"
WHERE "NUMERO_IDENTIFICACION_CLIENTE" = '{int(nit)}'
"""
    siar = pd.read_sql(sql_siar, con) 
    if not len(siar) == 0:
        lista = []
        lista2 = []
        lista3 = []
        for i in siar["ANO_SOLICITUD"].unique():
            lista.append((len(siar[siar["ANO_SOLICITUD"] == i]),i))
            lista2.append(len(siar[siar["ANO_SOLICITUD"] == i]))
        for i in lista:
            if i[0] == max(lista2):
                lista3.append(i[1])
        siar = siar[siar["ANO_SOLICITUD"] == max(lista3)]
        siar = siar[['ENUNCIADO_PREGUNTA', 'VALOR_RESPUESTA']]
    else:
        siar = "No figura."


    # Base de datos de siniestros
    sql_siniestros = f"""SELECT * FROM siniestros_nit_0621
    WHERE "NIT" = {nit}"""
    siniestros = pd.read_sql(sql_siniestros, con) 
    if len(siniestros) == 0:
        siniestros = "No presenta."
    siniestralidad = f"""{siniestros}
"""
    siar_base = f"""{siar}
"""

    # ANEXOS

    # Mapas
    f =open('Archivos/Mapas/ID_GENERICO/'+str(DIRECCION)+'.png','wb')
    f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/staticmap?center='+str(LATITUD)+','+str(LONGITUD)+'&zoom=18&size=600x600&maptype=roadmap&markers=color:red%7Clabel:%7C'+str(LATITUD)+','+str(LONGITUD)+'&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
    f.close()

    
    f =open('Archivos/Mapas/ID_GENERICO/'+str(DIRECCION)+'S.png','wb')
    f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/staticmap?center='+str(LATITUD)+','+str(LONGITUD)+'&zoom=18&size=600x600&maptype=satellite&markers=color:red%7Clabel:%7C'+str(LATITUD)+','+str(LONGITUD)+'&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
    f.close()

    # Streetview
    f = open('Archivos/Mapas/ID_GENERICO/'+str(DIRECCION)+'C0.jpeg','wb')
    f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/streetview?size=1000x800&location='+str(LATITUD)+','+str(LONGITUD)+'&fov=90&heading=0&pitch=0&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
    f.close()
    f = open('Archivos/Mapas/ID_GENERICO/'+str(DIRECCION)+'C90.jpeg','wb')
    f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/streetview?size=1000x800&location='+str(LATITUD)+','+str(LONGITUD)+'&fov=90&heading=90&pitch=0&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
    f.close()
    f = open('Archivos/Mapas/ID_GENERICO/'+str(DIRECCION)+'C180.jpeg','wb')
    f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/streetview?size=1000x800&location='+str(LATITUD)+','+str(LONGITUD)+'&fov=90&heading=180&pitch=0&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
    f.close()
    f = open('Archivos/Mapas/ID_GENERICO/'+str(DIRECCION)+'C270.jpeg','wb')
    f.write(urllib.request.urlopen('https://maps.googleapis.com/maps/api/streetview?size=1000x800&location='+str(LATITUD)+','+str(LONGITUD)+'&fov=90&heading=270&pitch=0&key=AIzaSyAuNt7JXO3AfSAkIc2ohCs0mvuLt3Xzbcc').read())
    f.close()

    ant = pd.read_excel("Archivos/ANTIGUEDADES.xlsx")
    ult = pd.read_excel("Archivos/Siniestros_Reportados.xlsx")
    vig = pd.read_excel("Archivos/vigentes.xlsx")
    for i in range (len(vig)):
        if vig.iloc[i][0] == nit:
            vigencia = "Activo"
            break
        else:
            vigencia = "Inactivo"

    for i in range (len(ant)):
        if ant.iloc[i][0] == nit:
            antiguedad = ant.iloc[i][1]
            break
    for i in range (len(ult)):
        if ult.iloc[i][0] == nit:
            ultSiniestro = ult.iloc[i][1]
            break
    try:
        ultSiniestro = str(ultSiniestro).replace("'", "").replace(" 00:00:00", "") 
    except:
        pass
    try:
        antiguedad = str(antiguedad).replace("'", "").replace(" 00:00:00", "") 
        anti = True
    except:
        anti = False
        pass

    ####################### CREACION DEL PDF #######################

    pdf=FPDF(format='letter', unit='in')
    pdf.add_page()

    pdf.set_font('Times','',10.0) 
    th = pdf.font_size
    ac = 0.25

    epw = pdf.w - 2 * pdf.l_margin


    # 0) PAGINA INTRODUCCION

    print("Entro a generar PDF")
    pdf.image(r'Archivos/Logo.jpg', x =2.8, y = pdf.get_y(), w = 3, h = 3)
    pdf.set_font('Times','B', 18.0) 
    pdf.ln(ac*15)
    pdf.cell(epw, 2, "INFORME DE", align = 'C')
    pdf.ln(ac)
    pdf.cell(epw, 2, "EVALUACIÓN DE RIESGOS", align = 'C')
    pdf.ln(ac*2)
    pdf.cell(epw, 2, tomador, align = 'C')
    pdf.ln(ac*10)
    pdf.set_font('Times','', 12.0) 
    pdf.cell(epw, 2, "INGENIERO DIGITAL GENÉRICO - API:", align = 'C')
    pdf.ln(ac*2)
    pdf.cell(epw, 2, "Fecha de realización:", align = 'C')
    pdf.ln(ac)
    now = datetime.now()
    pdf.cell(epw, 2, str(now.date()), align = 'C')
    

    # 1) INFORMACION EMPRESARIAL

    pdf.add_page()
    informacionGeneral = [['Nombre Tomador / Asegurado', tomador],
        ['NIT', nit],
        ['Actividad Económica', str(ciiu_numero).replace("'", "")],
        ['Valor a asegurar', valor_a_asegurar],
        ['Dirección', direccion],
        ['Ciudad', str(Ciudad[0]).capitalize()],
        ['Departamento', str(Departamento[0]).capitalize()],
        ['Teléfono', telefono_principal]]

    pdf.set_font('Times','B', 14.0) 
    pdf.cell(epw, 0.0, '1 - INFORMACIÓN GENERAL', align='C')
    pdf.set_font('Times','',10.0) 
    pdf.ln(0.3)

    for row in informacionGeneral:
        for i in row:
            pdf.cell(epw/2, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)

    # 2) RIESGOS CATASTROFICOS

    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, '2 - AMENAZAS (Visor mapas - Manzaneo)', align='C')
    pdf.ln(0.3)
    pdf.cell(epw/2, 3, '', align='C', border = 1)
    pdf.cell(epw/2, 3, '', align='C', border = 1)
    pdf.ln(3 + ac)
    print("Info primera pagina completa")

    pdf.image(r'Archivos/PNG/ID_GENERICO/' + str(DireccioN[0])  + "_tabla" + ".png", x =0.5, y = ac * 13 , w = 3.5, h = 2.5)

    pdf.image(r'Archivos/PNG/ID_GENERICO/' + str(DireccioN[0])  + "_tablaM" + ".png", x =4.5, y = ac * 13 , w = 3.5, h = 2.5)
    

    # 4) SINIESTROS
    pdf.add_page()
    
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, "5 - SINIESTROS", border=0, align = 'C') 
    pdf.ln(ac*2)

    tituloSiniestros = [["#"],["NOMBRE COBERTURA"],["SINIESTROS HISTÓRICOS"],["PÓLIZAS HISTORICAS"]]
    pdf.set_font('Times','B',12.0)
    pdf.cell(epw, ac, "HISTÓRICO DE SINIESTROS", border=1, align = 'C') 
    pdf.set_font('Times','',8.0) 
    pdf.ln(ac)
    if type(siniestros) is not str:
        for row in tituloSiniestros:
            for i in row:
                pdf.set_font('Times','B',8.0) 
                if i == "NOMBRE COBERTURA":
                    pdf.set_xy((epw/5)+pdf.l_margin, pdf.l_margin+(ac*3))
                    pdf.cell(epw/2.5, ac, str(i), border=1, align = 'C') 
                else:
                    pdf.cell(epw/5, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)

        for i in range (len(siniestros)):
            pdf.multi_cell(epw/5 , ac, str(i+1), border = 1, align = 'C')

        y = 4
        for i in siniestros['NOMBRE_COBERTURA']:
            pdf.set_font('Times', '',8.0) 
            pdf.set_xy((epw/5)+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/2.5 , ac, str(i), border = 1, align = 'C')
            y = y+1

        y = 4
        for i in siniestros['CANTIDAD_SINIESTROS']:
            pdf.set_xy((epw/5)*3+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/5 , ac, str(i), border = 1, align = 'C')
            y = y+1
    
        y = 4
        for i in siniestros['CANTIDAD_POLIZAS']:
            pdf.set_xy((epw/5)*4+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/5 , ac, str(i), border = 0, align = 'C')
            y = y+1
        pdf.cell(epw, ac, "LA FECHA DEL ÚLTIMO SINIESTRO FUE EL "+ ultSiniestro, border=1, align = 'C')
        pdf.ln(ac)
    else:
        pdf.cell(epw, ac, "NO HA PRESENTADO SINIESTROS", border=1, align = 'C')
        pdf.ln(ac)
    pdf.set_font('Times','B',10.0) 
    pdf.cell(epw, ac, "Usuario " +vigencia+ " dentro de la compañia." , border=1, align = 'C')
    pdf.ln(ac)
    if anti == True:
        pdf.set_font('Times','B',10.0) 
        pdf.cell(epw, ac, "La primera vinculación de este cliente se genero el " + antiguedad, border=1, align = 'C')
        pdf.ln(ac)
    else:
        pdf.set_font('Times','B',10.0) 
        pdf.cell(epw, ac, "SE TRATA DE UN CLIENTE NUEVO DENTRO DE LA COMPAÑIA ", border=1, align = 'C')
        pdf.ln(ac)
    
    # 3) ACTIVIDAD ECONOMICA
    
    pdf.ln(ac*2)
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, "ACTIVIDAD ECONOMICA", border=0, align = 'C') 
    pdf.ln(ac*2)

    try:
        pdf.set_font('Times', 'B', 14.0)
        pdf.cell(epw, ac, "DESCRIPCIÓN ACTIVIDAD ECONÓMICA", border=1, align='C')
        pdf.set_font('Times', '', 10.0)
        if len(ciiu_numero)>0:
            pdf.ln(ac)
            pdf.cell(epw, ac*(len(ciiu_numero)+1), "", border = 1, align='C')
            for i in range(0,len(ciiu_dado)):
                pdf.ln(ac)
                pdf.cell(epw, ac, str(ciiu_numero[i])+ ": " + str(ciiu_dado[i]), border=0, align='C')
        pdf.ln(ac)
    except:
        pass
     
    pdf.ln(ac)
    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(epw, ac, "RIESGOS POR ACTIVIDAD ECONÓMICA", border=1, align='C')

    headers = ["CIIU", "Incendio", "All Risk", "Sustracción","R.M", "E.E", "Manejo", "RC"]

    data = riesgos_politicas[headers].astype(str).values.tolist()
    
    pdf.ln()
    pdf.set_font('Times', 'B', 9.5)
    for header in headers:
        pdf.cell(epw / 8, ac, header, border=1, align='C')
    pdf.ln()

    pdf.set_font('Times', '', 9.5)

    for row in data:
        for item in row:
            if item.lower() == 'nan' or item.lower() == 'sin información':
                print("No hay información del riesgo para ciiu")
                item = 'Sin Información'
                pdf.set_fill_color(192,192,192)
            elif item == '5.0':
                pdf.set_fill_color(255, 0, 0)
            elif item == '4.0':
                pdf.set_fill_color(255, 128, 0)
            elif item == '3.0':
                pdf.set_fill_color(255, 255, 0)
            elif item == '2.0':
                pdf.set_fill_color(0, 180, 100)
            elif item == '1.0':
                pdf.set_fill_color(0, 255, 0)
            else:
                pdf.set_fill_color(255, 255, 255)

            int_item = "{:g}".format(float(item)) if item.lower() != 'sin información' else item
            pdf.cell(epw / 8, ac, str(int_item), border=1, align='C', fill=True)

        pdf.ln()
    
    if IsAseg == False and IsAlerta == False:
        riesgosAE = f"El predio posee los altos niveles de riesgo asociados con el desarrollo de su actividad económica principal ({ciiu_numero[0]})"
        var = 1
        text_lines = textwrap.wrap(riesgosAE, width=140)
        var = len(text_lines)
        pdf.cell(epw, ac*var, '', align='C', border=1)
        pdf.ln(ac/8)
        for line in text_lines:
            pdf.cell(epw, ac, line, border=0, align='L')
            pdf.ln(ac)
    elif IsAseg == False and IsAlerta == True:
        riesgosAE = f"El predio posee los altos niveles de riesgo asociados con el desarrollo de su actividad económica principal ({ciiu_numero[0]}) y de sus actividades económicas secundarias."
        var = 1
        text_lines = textwrap.wrap(riesgosAE, width=140)
        var = len(text_lines)
        pdf.cell(epw, ac*var, '', align='C', border=1)
        pdf.ln(ac/8)
        for line in text_lines:
            pdf.cell(epw, ac, line, border=0, align='L')
            pdf.ln(ac)
    else:
        riesgosAE = f"El predio cumple con las políticas de asegurabilidad de la compañía."
        var = 1
        text_lines = textwrap.wrap(riesgosAE, width=127)
        var = len(text_lines)
        pdf.cell(epw, ac*var, '', align='C', border=1)
        pdf.ln(ac/8)
        for line in text_lines:
            pdf.cell(epw, ac, line, border=0, align='L')
            pdf.ln(ac)
    pdf.ln(ac)           

    # EMIS
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, "REPORTE EMIS", border=1, align = 'C') 
    pdf.set_font('Times','',10.0) 
    locale.setlocale( locale.LC_ALL, '' )
    if len(emis != 0):
        empleados = int(emis['num_empleados'].values[0])
        ingresos = float(emis['ingresos_totales_ult_ano_usd'].values[0])

        vEmis = [['Fecha de Actualización', str(emis['fecha_actualizacion'].values[0]).replace("00:00:00 UTC", " ")],
        ['Estatus de la compañia', emis['estatus'].values[0]],
        ['Número de empleados', emis['num_empleados'].values[0]],
        ['Tipo de compañia', emis['tipo_compania'].values[0]],
        ['Ingresos totales del último año (USD)', emis['ingresos_totales_ult_ano_usd'].values[0]],
        ['Moneda capital del mercado', emis['moneda_capital_mercado'].values[0]],
        ['Año de ingresos totales', emis['ano_ingresos_totales'].values[0]]]
        
        for row in vEmis:
            pdf.ln(ac)
            for i in row:
                pdf.cell(epw/2, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)
        pdf.set_font('Times','B',12.0) 
        pdf.cell(epw, ac, "DESCRIPCIÓN SEGÚN EMIS", border=1, align = 'C') 
        pdf.set_font('Times','',10.0) 
        pdf.ln(ac)
        if len(emis['descripcion'].values[0]) > 120:
            var = round(len(emis['descripcion'].values[0]) / 120) + 1
            pdf.cell(epw, ac*var , '', align='C', border = 1)
            pdf.ln(ac/8)
            a = 0
            b = 120
            for i in range(var):
                text = emis['descripcion'].values[0][a:b]
                a = a + 120
                b = b + 120
                text_encoded = text.encode('latin-1', 'replace').decode('latin-1')  # Codificar en Latin-1
                pdf.cell(epw, ac, text_encoded, border=0, align='C')
                pdf.ln(ac)
            pdf.ln(ac)

    else:
        empleados = None
        ingresos = None
        pdf.ln(ac)
        pdf.cell(epw, ac, "Sin Información", border=1, align = 'C')
        pdf.ln(ac)


    def reemplazar(cadena, dic):
        for k,v in dic.items():
            cadena=cadena.replace(k, v)
        return cadena
    print("Actividad empresarial completa")


    # 5) ANALISIS DE RIESGO 

    pdf.ln(ac)
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, "5 - ANÁLISIS DE RIESGO (Manzaneo)", border=0, align = 'C') 
    pdf.ln(ac*2)
    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "CONCEPTO DE MANZANEO", border=1, align = 'C') 
    pdf.ln(ac)
    pdf.set_font('Times','',10.0) 
    if ConceptoManzaneo[0] == "N":
        pdf.cell(epw, ac, "Concepto Favorable ", border=1, align = 'C') 
    elif ConceptoManzaneo[0] == "S":
        pdf.cell(epw, ac, "Concepto desfavorable", border=1, align = 'C') 
    else:
        pdf.cell(epw, ac, "Sin información", border=1, align = 'C') 
    pdf.ln(ac*2)
    print("Información interna completa")

##################GA######################
    texto = '''Durante la vigencia de la póliza, se realizará la suspensión del suministro de energía eléctrica durante las horas y días no laborables a los circuitos de distribución eléctrica.Esta suspensión se aplicará a los equipos o áreas que no son indispensables para el desarrollo de las actividades del asegurado.Se entiende como indispensables aquellos circuitos que suministran energía a equipos o áreas que, debido al funcionamiento de la empresa, no pueden quedarse sin energía.La implementación de esta suspensión debe documentarse mediante un procedimiento que incluya responsables definidos y registros suficientes.''' 
    texto1= '''Durante la vigencia de la póliza, el asegurado debe mantener un sistema de puesta a tierra de capacidad suficiente para proteger los equipos electrónicos existentes en las instalaciones y realizar mantenimiento preventivo anual al sistema. Evidenciar las actividades de mantenimiento por medio de un registro documentado. Para la instalación de un sistema apropiado de puesta a tierra, tomar en consideración el Reglamento Técnico de Instalaciones Eléctricas (RETIE).'''
    pdf.add_page()
    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(epw, ac, " 6 - GARANTÍAS", border=0, align='C')
    pdf.ln(ac*2)

    # Cambiar a la fuente regular
    pdf.set_font('Times', '', 12.0)

    # Calcular el número de páginas necesarias para el texto
    pdf.cell(w = 0, h = 0.25, txt = 'CORTE DE ENERGÍA 405-5', border = 1, ln=1, align = 'C', fill = 0)
    var = 1
    if len(texto) > 110:
        var = round(len(texto) / 110) + 1
    # Agregar un espacio en blanco con borde
    pdf.cell(epw, ac*var, ' ', align='C', border=1)
    pdf.ln(ac/8)

# Inicializar las variables de fragmentación
    a = 0
    b = 110

# Crear una lista para almacenar los fragmentos de texto
    fragmentos = []

    # Dividir el texto en fragmentos y almacenarlos en la lista
    for i in range(var):
        text = texto[a:b]
        fragmentos.append(text)
        a = b
        b += 110

    # Agregar los fragmentos al PDF
    for fragmento in fragmentos:
        pdf.cell(epw, ac, fragmento, border=0, ln=1, align='L', fill=0)

    pdf.cell(w = 0, h = 0.25, txt = 'SISTEMA DE PUESTA A TIERRA 421-3', border = 1, ln=1, align = 'C', fill = 0)
    var = 1
    if len(texto1) > 110:
        var = round(len(texto1) / 110) + 1
    # Agregar un espacio en blanco con borde
    pdf.cell(epw, ac*var, ' ', align='C', border=1)
    pdf.ln(ac/8)
    # Inicializar las variables de fragmentación
    a = 0
    b = 110

# Crear una lista para almacenar los fragmentos de texto
    fragmentos = []

    # Dividir el texto en fragmentos y almacenarlos en la lista
    for i in range(var):
        text = texto1[a:b]
        fragmentos.append(text)
        a = b
        b += 110

    # Agregar los fragmentos al PDF
    for fragmento in fragmentos:
        pdf.cell(epw, ac, fragmento, border=0, ln=1, align='L', fill=0)    
    print("garantíasgenerico")
    
        ################## CONCEPTO ID ###############################
    
    pdf.add_page()
    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(epw, ac, "10 - CONCEPTO INGENIERO DIGITAL", border=0, align='C')
    pdf.ln(ac*2)

    pdf.set_font('Times', '', 12.0)
    
    def agregar_concepto(pdf, titulo, mensaje):
        pdf.set_font('Times', 'B', 14.0)
        pdf.cell(epw, ac, titulo, border=1, align='C')
        pdf.ln() 
        
        pdf.set_font('Times', '', 10.0)
        var = 1
        text_lines = textwrap.wrap(mensaje, width=120)
        var = len(text_lines)
        pdf.cell(epw, ac*var, '', align='C', border=1)
        pdf.ln(ac/8)    
        for line in text_lines:
            pdf.cell(epw, ac, line, border=0, align='L')
            pdf.ln(ac)
        pdf.ln()


    print(f"La amenaza de terremoto es: {MatrizAmenazas[0]}")
    print(f"La amenaza de remoción es: {MatrizAmenazas[2]}")
    
    if IsAseg == False:
        condicion1 = "No asegurable"
    else:
        condicion1 = "Asegurable"
    if MatrizAmenazasManzaneo[0] == "Sin información" or ConceptoManzaneo[0] == "Sin informacion":
        condicion2 = "Sin informacion"   
    elif ConceptoManzaneo[0] == "S" and MatrizAmenazasManzaneo[0].lower() == "alto":
        condicion2 = "No asegurable"
    else:
        condicion2 = "Asegurable"
    if rango_año_construccion == "Sin información" or amenaza_terremoto == "None":
        condicion3 = "Sin información"
    if (MatrizAmenazas[0].lower() == "media alta" or MatrizAmenazas[0].lower() == "medio alto" or MatrizAmenazas[0].lower() == "medio-alto" or MatrizAmenazas[0].lower() == "alto" or MatrizAmenazas[0].lower() == "alta") and rango_año_construccion == "PREVIO A 1985":
        condicion3 = "No asegurable"
    else:
        condicion3 = "Asegurable"
    if rango_año_construccion == "Sin información" or MatrizAmenazas[2] == "Sin informacion":
        condicion4 = "Sin información"
    if (MatrizAmenazas[0].lower() == "media alta" or MatrizAmenazas[2].lower() == "medio alto" or MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2].lower() == "alto" or MatrizAmenazas[2].lower() == "alta") and rango_año_construccion == "PREVIO A 1985":
        condicion4 = "No asegurable"
    else:
        condicion4 = "Asegurable"
        
        
    pdf.set_font('Times', 'B', 12.0)
    pdf.cell(6, ac, "Concepto del ID", border=1, align='C')
    pdf.set_font('Times', '', 10.0)
    pdf.ln(ac)

    rID = [
        ['Actividad económica', condicion1],
        ['Concepto Manzaneo - Amenaza de incendio Manz', condicion2],
        ['Rango de edad zona - Amenaza de incendio VM', condicion3],
        ['Rango de edad zona - Amenaza de remoción VM', condicion4]
    ]
    x = pdf.get_x()
    for row in rID:
        for item in row:
            pdf.cell(6/2, ac, str(item), border=1, align='C')  # Ajustar el tamaño de la celda según sea necesario
        pdf.ln(ac)
    pdf.set_x(x)  
    pdf.ln(ac)
    
    if rango_año_construccion == "Sin información":
        justificacionID = "Se trata de la empresa " +str(tomador)+" ubicada en la "+str(direccion)+"."
    else:
        justificacionID = "Se trata de la empresa " +str(tomador)+" ubicada en la "+str(direccion)+". El rango de edad de la zona donde se encuentra ubicado el predio es " +str(rango_año_construccion)+ "." 
    if (IsAseg == False) or (ConceptoManzaneo[0] == "S" and MatrizAmenazasManzaneo[0].lower() == "alto") or ((MatrizAmenazas[0].lower() == "media alta" or MatrizAmenazas[0].lower() == "medio alto" or MatrizAmenazas[0].lower() == "medio-alto" or MatrizAmenazas[0].lower() == "alto" or MatrizAmenazas[0].lower() == "alta") and rango_año_construccion == "PREVIO A 1985") or ((MatrizAmenazas[0].lower() == "media alta" or MatrizAmenazas[2].lower() == "medio alto" or MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2].lower() == "alto" or MatrizAmenazas[2].lower() == "alta") and rango_año_construccion == "PREVIO A 1985"):
        conceptoID = "No asegurable"
        
        #Condición 1
        if (IsAseg == False):
            justificacionID += " La empresa " +str(tomador)+ " tiene como actividad económica principal " +str(ciiu_dado[0])+ ", la cual se considera como fuera de políticas de acuerdo con las políticas establecidas por la compañía."
        elif (IsAseg == True):
            justificacionID += " La empresa " +str(tomador)+ " tiene como actividad económica principal " +str(ciiu_dado[0])+ ", la cual se encuentra amparada por las políticas establecidas por la empresa."
        
        #Condición 2
        if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "Sin informacion":
            justificacionID += " No hay información del concepto del manzaneo ni de la amenaza de incendio."
        if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "S":
            justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es desfavorable."
        if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "N":
            justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es favorable."     
        if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and MatrizAmenazasManzaneo[0].lower() == "alto"):
            justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable igual que la amenaza de incendio de la capa de manzaneo."
        if not(MatrizAmenazasManzaneo[0] == "Sin información") and (not(ConceptoManzaneo[0] == "S") and MatrizAmenazasManzaneo[0].lower() == "alto"):
            justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable pero la amenaza de incendio de la capa de manzaneo es Alta."
        if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and not(MatrizAmenazasManzaneo[0].lower() == "alto")):
            justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable pero la amenaza de incendio de la capa de manzaneo es aceptable."
        if not(MatrizAmenazasManzaneo[0] == "Sin información") and not(ConceptoManzaneo[0] == "S") and not (MatrizAmenazasManzaneo[0].lower() == "alto"):
            justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable igual que la amenaza de incendio de la capa de manzaneo."
       
        #Condición 3
        if rango_año_construccion == "Sin información":
            justificacionID += " No hay información del rango de edad de la zona."
        if amenaza_terremoto == "None":
            justificacionID += "  No hay información de la amenaza de terremoto según el VM."
        if (MatrizAmenazas[0].lower() == "media alta" or MatrizAmenazas[0].lower() == "medio alto" or MatrizAmenazas[0].lower() == "medio-alto" or MatrizAmenazas[0].lower() == "alto" or MatrizAmenazas[0].lower() == "alta") and rango_año_construccion == "PREVIO A 1985":
            justificacionID += " También, la amenaza de terremoto es desfavorable según el visor de mapas."
        if (not(MatrizAmenazas[0].lower() == "media alta" or MatrizAmenazas[0].lower() == "medio alto" or MatrizAmenazas[0].lower() == "medio-alto" or MatrizAmenazas[0].lower() == "alto" or MatrizAmenazas[0].lower() == "alta")) and rango_año_construccion == "PREVIO A 1985":
            justificacionID += " También, la amenaza de terremoto es aceptable según el visor de mapas."
        if (MatrizAmenazas[0].lower() == "media alta" or MatrizAmenazas[0].lower() == "medio alto" or MatrizAmenazas[0].lower() == "medio-alto" or MatrizAmenazas[0].lower() == "alto" or MatrizAmenazas[0].lower() == "alta") and not(rango_año_construccion == "PREVIO A 1985"):
            justificacionID += " También, la amenaza de terremoto es desfavorable según el visor de mapas."
        elif not((MatrizAmenazas[0].lower() == "media alta" or MatrizAmenazas[0].lower() == "medio alto" or MatrizAmenazas[0].lower() == "medio-alto" or MatrizAmenazas[0].lower() == "alto" or MatrizAmenazas[0].lower() == "alta")) and not (rango_año_construccion == "PREVIO A 1985"):
            justificacionID += " También, la amenaza de terremoto es favorable según el visor de mapas."
        
        #Condición 4
        if rango_año_construccion == "Sin información":
            print()
        if MatrizAmenazas[2] == "None":
            justificacionID += "  No hay información de la amenaza de remoción en masa según el VM."
        if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alto") and rango_año_construccion == "PREVIO A 1985":
            justificacionID += " Por otro lado, la amenaza de remoción en masa es desfavorable según el visor de mapas."
        if (not(MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alto")) and rango_año_construccion == "PREVIO A 1985":
            justificacionID += " Por otro lado, la amenaza de remoción en masa es aceptable según el visor de mapas."
        if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alto") and not(rango_año_construccion == "PREVIO A 1985"):
            justificacionID += " Por otro lado, la amenaza de remoción en masa es desfavorable según el visor de mapas."
        elif not((MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alto")) and not (rango_año_construccion == "PREVIO A 1985"):
            justificacionID += " Por otro lado, la amenaza de remoción en masa es favorable según el visor de mapas."
        
        justificacionID += " El concepto final de asegurabilidad del ID dada toda la justificación anterior es NO ASEGURABLE." 
    
    else:
        conceptoID = "Asegurable"
        
        #Condición 1
        if (IsAseg == False):
            justificacionID += " La empresa " +str(tomador)+ " tiene como actividad económica principal " +str(ciiu_dado[0])+ ", la cual se considera como fuera de políticas de acuerdo con las políticas de la compañía."
        elif (IsAseg == True):
            justificacionID += " La empresa " +str(tomador)+ " tiene como actividad económica principal " +str(ciiu_dado[0])+ ", la cual se encuentra amparada por las políticas establecidas por la empresa."
        
        #Condición 2
        if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "Sin informacion":
            justificacionID += " No hay información del concepto del manzaneo ni de la amenaza de incendio."
        if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "S":
            justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es desfavorable."
        if MatrizAmenazasManzaneo[0] == "Sin información" and ConceptoManzaneo[0] == "N":
            justificacionID += " Por parte del manzaneo no hay información de la amenaza de incendio del predio. Sin embargo, el concepto general del manzaneo es favorable."    
        if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and MatrizAmenazasManzaneo[0].lower() == "alto"):
            justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable igual que la amenaza de incendio de la capa de manzaneo."
        if not(MatrizAmenazasManzaneo[0] == "Sin información") and (not(ConceptoManzaneo[0] == "S") and MatrizAmenazasManzaneo[0].lower() == "alto"):
            justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable pero la amenaza de incendio de la capa de manzaneo es Alta."
        if not(MatrizAmenazasManzaneo[0] == "Sin información") and (ConceptoManzaneo[0] == "S" and not(MatrizAmenazasManzaneo[0].lower() == "alto")):
            justificacionID += " Así mismo, el concepto por parte del manzaneo es desfavorable pero la amenaza de incendio de la capa de manzaneo es aceptable."
        if not(MatrizAmenazasManzaneo[0] == "Sin información") and not(ConceptoManzaneo[0] == "S") and not (MatrizAmenazasManzaneo[0].lower() == "alto"):
            justificacionID += " Así mismo, el concepto por parte del manzaneo es favorable igual que la amenaza de incendio de la capa de manzaneo."
        
        #Condición 3
        if rango_año_construccion == "Sin información":
            justificacionID += " No hay información del rango de edad de la zona."
        if amenaza_terremoto == "None":
            justificacionID += "  No hay información de la amenaza de terremoto según el VM."
        if rango_año_construccion == "PREVIO A 1985" and (MatrizAmenazas[0].lower() == "medio-alto" or MatrizAmenazas[0] == "alto"):
            justificacionID += " También, la amenaza de terremoto es desfavorable según el visor de mapas."
        if rango_año_construccion == "PREVIO A 1985" and (not(MatrizAmenazas[0].lower() == "medio-alto" or MatrizAmenazas[0] == "alto")):
            justificacionID += " También, la amenaza de terremoto es aceptable según el visor de mapas."
        if (MatrizAmenazas[0].lower() == "medio-alto" or MatrizAmenazas[0] == "alto") and not(rango_año_construccion == "PREVIO A 1985"):
            justificacionID += " También, la amenaza de terremoto es desfavorable según el visor de mapas."
        elif not((MatrizAmenazas[0].lower() == "medio-alto" or MatrizAmenazas[0] == "alto")) and not (rango_año_construccion == "PREVIO A 1985"):
            justificacionID += " También, la amenaza de terremoto es favorable según el visor de mapas."
        
        #Condición 4
        if rango_año_construccion == "Sin información":
            justificacionID += " No hay información del rango de edad de la zona."
        if MatrizAmenazas[2] == "None":
            justificacionID += "  No hay información de la amenaza de remoción en masa según el VM."
        if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alto" or MatrizAmenazas[2] == "alta") and rango_año_construccion == "PREVIO A 1985":
            justificacionID += " Por otro lado, la amenaza de remoción en masa es desfavorable según el visor de mapas."
        if (not(MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alto" or MatrizAmenazas[2] == "alta")) and rango_año_construccion == "PREVIO A 1985":
            justificacionID += " Por otro lado, la amenaza de remoción en masa es aceptable según el visor de mapas."
        if (MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alto" or MatrizAmenazas[2] == "alta") and not(rango_año_construccion == "PREVIO A 1985"):
            justificacionID += " Por otro lado, la amenaza de remoción en masa es desfavorable según el visor de mapas."
        elif not((MatrizAmenazas[2].lower() == "medio-alto" or MatrizAmenazas[2] == "alto" or MatrizAmenazas[2] == "alta")) and not (rango_año_construccion == "PREVIO A 1985"):
            justificacionID += " Por otro lado, la amenaza de remoción en masa es favorable según el visor de mapas."
        justificacionID += " El concepto final de asegurabilidad del ID dada toda la justificación anterior es ASEGURABLE."
      
    agregar_concepto(pdf,"Justificación del ID", justificacionID)
    
    y = pdf.get_y() 
    if conceptoID == "Asegurable":
        pdf.image(r'Archivos/Check.png', x = epw/1.15, y = y*0.15 , w = ac*4, h = ac*4)
    if conceptoID == "No asegurable":
        pdf.image(r'Archivos/Error.png', x = epw/1.15, y = y*0.15 , w = ac*4, h = ac*4)
    
    # 6) ANEXOS

    pdf.add_page()
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, "7 - ANEXOS", border=0, align = 'C') 
    pdf.ln(ac*2)
    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "1- MAPA DE LA ZONA", border=0, align = 'L') 
    pdf.image(r'/home/ingeniero_digital/principal/PLATAFORMA/plataforma_proyecto/anexos/Mapas/'+str(DIRECCION)+'.png', x = 1.5, y = ac*5 , w = ac*20, h = ac*20)
    pdf.image(r'/home/ingeniero_digital/principal/PLATAFORMA/plataforma_proyecto/anexos/Mapas/'+str(DIRECCION)+'S.png', x = 1.5, y = ac*25 , w = ac*20, h = ac*20)
    pdf.ln(ac*22)

    pdf.add_page()
    pdf.cell(epw, ac, "2 - CAPTURAS DE STREETVIEW", border=0, align = 'L') 
    pdf.image(r'/home/ingeniero_digital/principal/PLATAFORMA/plataforma_proyecto/anexos/Streetview/'+str(DIRECCION)+'C0.jpeg', x = 1, y = ac*5 , w = ac*14, h = ac*14)
    pdf.image(r'/home/ingeniero_digital/principal/PLATAFORMA/plataforma_proyecto/anexos/Streetview/'+str(DIRECCION)+'C90.jpeg', x = 1+(ac*14), y = ac*5 , w = ac*14, h = ac*14)
    pdf.image(r'/home/ingeniero_digital/principal/PLATAFORMA/plataforma_proyecto/anexos/Streetview/'+str(DIRECCION)+'C180.jpeg', x = 1, y = ac*25 , w = ac*14, h = ac*14)
    pdf.image(r'/home/ingeniero_digital/principal/PLATAFORMA/plataforma_proyecto/anexos/Streetview/'+str(DIRECCION)+'C270.jpeg', x = 1+(ac*14), y = ac*25 , w = ac*14, h = ac*14)


    # print("Anexos completo")
    pdf.output('Archivos/PDF/ID_GENERICO/' + DireccioN[0] + 'NI.pdf', 'F')
    ruta = str("Archivos/PDF/ID_GENERICO/"+ DireccioN[0] + "NI.pdf")

    print("PDF GENERADO")
    mapas = ""

    # Exepciones
    try: 
        Terremoto = MatrizAmenazas[0]
        Vientos = MatrizAmenazas[1]
        Remocion = MatrizAmenazas[2]
        Sustraccion = MatrizAmenazas[3]
        Orden = MatrizAmenazas[4]
        Rayos = MatrizAmenazas[5]
        Inundacion = MatrizAmenazas[6]
        AMIT = MatrizAmenazas[7]    
    except:
        Terremoto = "Sin info"
        Vientos = "Sin info"
        Remocion = "Sin info"
        Sustraccion = "Sin info"
        Orden = "Sin info"
        Rayos = "Sin info"
        Inundacion = "Sin info"
        AMIT = "Sin info"  
        mapas = True

    fin = time.time()
    tiempo = fin - inicio
    print("Llego a guardar info")
    try:
            
        reg = ["API_pruebas", str(DIRECCION), datetime.now(), str(nit), str(tomador), str(ValoR), str(ConceptoManzaneo[0]), str(Terremoto),
            str(Vientos), str(Remocion), str(Sustraccion), str(Orden), str(Rayos), str(Inundacion), str(AMIT), str(ciiu_numero).replace("'", ""), str(direccion), 
            str(LATITUD), str(LONGITUD), 
            str(sire[["Fecha reporte", "Tipo de afectación"]]), tiempo, 
            empleados,
            ingresos,
            "Exitoso"]

        con2 = psycopg2.connect(database="ingDigitalCA", user="postgres", password="Bolivar2021",
            host="35.153.192.47", port=8081)

        cur = con2.cursor()
        cur.execute("""INSERT INTO first_consultas("usuario", "direccionEstand", "fechaConsulta",  "nit", "razonSocial",
        "valorAsegurar", "manzaneo","terremoto","vientos","remocion", "sustraccion",
        "orden", "rayos", "inundacion", "amit", "ciuu",
        "direccion", "barrio", "upz", "localidad", "latitud",
        "longitud",  "sire", "tiempoRespuesta", "emisEmpleados", "emisIngresos",
        "respuesta") VALUES (
                                                                                    %s, %s, %s, %s, %s,
                                                                                    %s, %s, %s, %s, %s, 
                                                                                    %s, %s, %s, %s, %s,
                                                                                    %s, %s, %s, %s, %s, 
                                                                                    %s, %s, %s, %s, %s, 
                                                                                    %s, %s, %s, %s, %s,
                                                                                    %s, %s, %s, %s, %s, 
                                                                                    %s, %s, %s, %s, %s, 
                                                                                    %s, %s, %s, %s, %s,
                                                                                    %s, %s, %s, %s, %s, 
                                                                                    %s, %s, %s, %s, %s,
                                                                                    %s, %s, %s, %s, %s,
                                                                                    %s, %s);""", reg)
        con2.commit()
        cur.close()
        con2.close()
        print("Guardo info")
    except:
            
        con2 = psycopg2.connect(database="ingDigitalCA", user="postgres", password="Bolivar2021",
            host="35.153.192.47", port=8081)
        
        reg = ["API_pruebas", direccion, datetime.now(), str(nit), "ERROR"]

        cur = con2.cursor()
        cur.execute("""INSERT INTO first_consultas("usuario", "direccion", "fechaConsulta",  "nit", "respuesta") VALUES (%s, %s, %s, %s, %s);""", reg)
        con2.commit()
        cur.close()
        con2.close()
        print("No logro guardar")

    #JSON    
    mjs = {
        "Nombre tomador": f'{tomador}',
        "NIT":f'{nit}',
        "Dirección": f'{direccion}',
        "Dirección estandarizada ": f'{DireccioN[0]}',
        "Rango de edad del predio": f'{rango_año_construccion}',
        "Latitud": f'{LATITUD}',
        "Longitud": f'{LONGITUD}',
        "Valor a asegurar": f'{valor_a_asegurar}',
        "Manzaneo": f'{ConceptoManzaneo[0]}',
        "Terremoto":f'{Terremoto}',
        "Vientos":f'{Vientos}',
        "Remocion":f'{Remocion}',
        "Sustraccion":f'{Sustraccion}',
        "Orden":f'{Orden}',
        "Rayos":f'{Rayos}',   
        "Inundacion":f'{Inundacion}',
        "AMIT":f'{AMIT}',
        "Mapas": f'{mapas}',
        "CIIU info": f'{ciiu_dado, ciiu_numero}',
        "SIRE": f'{sire[["Fecha reporte", "Tipo de afectación"]]}',
        "Número de empleados": f'{emis["num_empleados"]}',
        "Ingresos": f'{emis["ingresos_totales_ult_ano_usd"]}',
        "Incendio Manzaneo":f'{MatrizAmenazasManzaneo[0]}',
        "Sustraccion Manzaneo":f'{MatrizAmenazasManzaneo[1]}',
        "Anegación Manzaneo":f'{MatrizAmenazasManzaneo[2]}',
        "Terremoto Manzaneo":f'{MatrizAmenazasManzaneo[3]}',
        "AMIT Manzaneo":f'{MatrizAmenazasManzaneo[4]}',
        "Daño eléctrico Manzaneo":f'{MatrizAmenazasManzaneo[5]}',
        "Vientos Manzaneo":f'{MatrizAmenazasManzaneo[6]}',
        "Riesgos por AE": f'{IsAseg}',
        "Concepto del ID": f'{conceptoID}',
        "Justificación del ID": f'{justificacionID}',
        "Condición 1 Aseg": f'{condicion1}',
        "Condición 2 Aseg": f'{condicion2}',
        "Condición 3 Aseg": f'{condicion3}',
        "Condición 4 Aseg": f'{condicion4}',
        "Ruta": f'{ruta}'
    } 
    return JSONResponse(status_code=200, content=mjs)



# ID MYE
@app.post('/API/MAQUINARIA_Y_EQUIPO')
async def StandAlone(nit: int = None, ubicacionOperacion: str = None, ubicacionComercial: str = None, file:UploadFile = File('..')):

    from collections import Counter
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    import pandas as pd  
    from fpdf import FPDF
    from datetime import datetime
    import locale
    import psycopg2
    import shutil

    with open("Archivos/PLANTILLA.xlsx","wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    

    
    #Conexión con base de datos postgress
    con = psycopg2.connect(database="ingdigital", user="postgres", password="Bolivar2021", host="35.153.192.47", port=8081)

    #ACCEDER A LA HOJA DE RESPUESTAS DEL FORMULARIO(Acceso por keyDrive)
    #https://docs.google.com/spreadsheets/d/1FXq5FEuuOlvaYpjCSlrqQfDgTcvqaHS3QjroDXOXUsQ/edit?resourcekey&usp=forms_web_b#gid=193012832
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("/home/ingeniero_digital/principal/ID_MYE/keyDrive.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("Formato de evaluación de riesgos y asegurabilidad Equipo y Maquinaria Contratista").sheet1  #Abrir spreadhseet
    data = pd.DataFrame(sheet.get_all_records())  #Obtener todos los registros
    #Calificaciones formulario
    eval = pd.read_excel("/home/ingeniero_digital/principal/ID_MYE/Calificación MYE.xlsx")
    #Capa de amenaza EYM
    amenazaMYE = pd.read_excel("/home/ingeniero_digital/principal/ID_MYE/Amenaza MYE ciudades.xlsx")


    #!!!ESTE NO SE DE DONDE SE TRAERA (POR AHORA INFORME DUMMIE)
    maquinaria = pd.read_excel("Archivos/PLANTILLA.xlsx", sheet_name= "PLANTILLA NOMINA E Y M")

    #Limpieza archivo relación de maquinaria
    maquinaria = maquinaria[7::]
    maquinaria = maquinaria.iloc[:,1:10]
    

    #Listado preguntas del formulario
    nombreVariables = data.columns.tolist()
    
    print(len(nombreVariables))

    for i in range(0, len(data)):

        if data.iloc[i][22] == nit:
            fila = data.iloc[i]
            break
    a = 0
    riesgoMYE = 0
    anexoInspeccion = True
    anexoInstructivos = True
    anexoProtocolosMovi = True
    anexopProtocolosRobo = True

    try:
        if int(fila[19])<=60 :
            riesgoMYE = riesgoMYE + 5
        if 60 < int(fila[19]) <=85 :
            riesgoMYE = riesgoMYE + 3
        if 85 < int(fila[19]):
            riesgoMYE = riesgoMYE + 1

        print("LOGRO GUARDAR PUNTAJE SGSST")
    except:
        riesgoMYE = riesgoMYE + 3
        print("NO LOGRO GUARDAR PUNTAJE SGSST")
        print("ESTE ES EL PUNTAJE "+str(fila[19]))
        pass
    
    countProtección = int(fila[20].count(','))
    
    if fila[20] == "Ninguna":
        riesgoMYE = riesgoMYE + 5

    if countProtección == 0 and fila[20] != "Ninguna":
        riesgoMYE = riesgoMYE + 4

    if countProtección == 1:
        riesgoMYE = riesgoMYE + 2

    if countProtección == 2:
        riesgoMYE = riesgoMYE + 1
    
    
    
    #RECORRE TODAS LAS POSIBLES RESPUESTAS 
    for i in range(0, len(eval)):
    #POR CADA INGRESO RECORRE CADA UNA DE LAS VARIABLES 

        for j in range(0, len(nombreVariables)):
            #VALIDA QUE LA FILA SEA IGUAL A UNA DE LAS VARIABLES Y QUE LA RESPUESTA SEA IGUAL A LA COLUMNA 
            if eval.iloc[i][0] == nombreVariables[j]:
            
                if eval.iloc[i][1] == fila[j]:
                    
                    if eval.iloc[i][0] == "3 - Respecto a su plan de mantenimiento de la maquinaria, ¿Dispone de formatos de mantenimiento e inspección de los equipos?" and fila[8] == "":
                        riesgoMYE = riesgoMYE + 4
                        anexoInspeccion = False    
                        print("No anexo documentación en numeral 3")
                        

                    if eval.iloc[i][0] == "5 -  ¿Dispone de instructivos, cartillas y/o procedimientos debidamente documentados y socializados para la operación de la maquinaria o la actividad a desarrollar?" and fila[11] == "":
                        riesgoMYE = riesgoMYE + 4
                        anexoInstructivos = False
                        print("No anexo documentación en numeral 5")
                    
                    if eval.iloc[i][0] == "6 -  ¿Cuenta con protocolos para el transporte o movilización, cargue y descargue de los equipos y/o maquinaria?" and fila[14] == "":
                        riesgoMYE = riesgoMYE + 4
                        anexopProtocolosMovi = False
                        print("No anexo documentación en numeral 6")

                    if eval.iloc[i][0] == "7. ¿ Dispone de protocolos documentados y socializados al personal para protección de la maquinaria y equipo contra ROBO?" and fila[21] == "":
                        riesgoMYE = riesgoMYE + 4
                        anexopProtocolosRobo = False
                        print("No anexo documentación en numeral 7")
                    
                    riesgoMYE = riesgoMYE + eval.iloc[i][2]
    
    

    riesgoMYE = riesgoMYE/11


    for i in range (0,1):
        if 1 < riesgoMYE < 1.8:
            riesgoMYE = "BAJO"
            break
        if 1.8 < riesgoMYE < 2.6:
            riesgoMYE = "MEDIO BAJO"
            break
        if 2.6 < riesgoMYE < 3.4:
            riesgoMYE = "MEDIO"
            break
        if 3.4 < riesgoMYE < 4.2:
            riesgoMYE = "MEDIO ALTO"
            break
        if 4.2 < riesgoMYE < 5:
            riesgoMYE = "ALTO"
            break

    print(fila[0])
    
    print(fila[1])
    
    print(fila[2])
    
    print(fila[3])
    
    print(fila[4])
    
    print(fila[5])
    
    print(fila[0])
    
    print(fila[0])
    
    print(fila[0])
    
    print(fila[0])
    
    print(fila[0])
    
    print(fila[0])
    
    print(fila[0])
    
    print(fila[0])
    
    print(fila[0])
    
    print(fila[0])
    
    print(fila[0])
    print(fila[0])
    
    print(fila[0])
    
    print(fila[0])
    for i in range(0,1):
        if fila[16] == "SÍ":
            riesgoMYE = "ALTO"
            break

        if anexoInspeccion is False and fila[5] != "1 - 3 años":
            riesgoMYE = "ALTO"
            break
        
        if fila[19] < 60 and fila[5] != "1 - 3 años":
            riesgoMYE = "ALTO"
            break

        if 60 < fila[19] < 85 and fila[5] != "1 - 3 años":
            riesgoMYE = "MEDIO ALTO"
            break

        if anexoInspeccion is False and fila[5] == "1 - 3 años":
            riesgoMYE = "MEDIO BAJO"
            break

        if 85 < fila[19]:
            riesgoMYE = "BAJO"
            break




    print(riesgoMYE)






    '''
    def ingenieroDigitalMYE(valorAsegurado, tipoMaquinaria, alertaVisita):
        print(valorAsegurado)
        print(tipoMaquinaria)
        print(alertaVisita)
        
    #Caso que sea maquinaria individual
    if tipoMaquinaria == "Maquinaria individual":
    if valorAsegurado >= 700000000:
        alertaVisita = True
    ingenieroDigitalMYE(valorAsegurado, tipoMaquinaria, alertaVisita)

    #Caso que sea maquinaria parque
    else:
    tipoMaquinaria = "Maquinaria Parque"
    if valorAsegurado >= 1400000000:
        alertaVisita = True
    ingenieroDigitalMYE(valorAsegurado, tipoMaquinaria, alertaVisita)
    

    if not type(nit) == type(None):
        nit = nit.replace('.','')
        nit = nit.replace(',','')
    '''
    #OBTENCIÓN INFO A PARTIR DEL NIT
    ciiu = pd.read_excel(r"Archivos/Estructura-detallada-CIIU-4AC-2020-.xls")
    sql_dane = f"""SELECT * FROM dane_2020
    WHERE "NIT" = '{int(nit)}'"""
    dane = pd.read_sql(sql_dane, con) 
    telefono_principal = ""
    ciiu_dado = []
    ciiu_numero = []
    if not len(dane) == 0: 
        razon_social = dane['RAZON_SOCIAL'].iloc[0]
        nombre_comercial = None
        for i in range(0,len(dane)):
            if not str(dane['NOMBRE_COMERCIAL'].iloc[i]) == 'nan':
                nombre_comercial = dane['NOMBRE_COMERCIAL'].iloc[i]
        direccion_principal = dane['DIRECCION'].iloc[0]
        departamento_principal = dane['NOMBRE_DPTO'].iloc[0]
        municipio_principal = dane['NOMBRE_MPIO'].iloc[0]
        telefono_principal = str(int(dane['TELEFONO1'].iloc[0]))
        telefono2_principal = str(int(dane['TELEFONO1'].iloc[0]))

        def match_ciiu(self):
            '''Retorna el índice de la actividad económica correspondiente al código CIIU
            params:
            self = código CIIU correspondiente al NIT
            '''
            for index, s in enumerate(ciiu['Unnamed: 2']):
                if str(s) == str(self) or str(s) == '0' + str(self):
                    return index, s
                    break
                elif str(self)[:3] == str(ciiu['Unnamed: 3'].iloc[index]) or str(self) == '0' + str(ciiu['Unnamed: 3'].iloc[index]):
                    return index, ciiu['Unnamed: 1'].iloc[index]
        try:
            for i in range(0, len(dane)):
                ciiu_dado.append(ciiu['Unnamed: 3'].iloc[match_ciiu(int(dane['CIIU_ID_CIIU_4'].iloc[i]))[0]])
            for i in range(0, len(dane)):
                ciiu_numero.append(str(int(dane['CIIU_ID_CIIU_4'].iloc[i])))
        except:
            pass    
    try: 
        tomador = razon_social
    except:
        tomador = ""
        


    #SINIESTROS PRODUCTO 152
    sql_siniestros = f"""SELECT * FROM siniestroseym
    WHERE "key_id_asegurado" = '{str(nit)}'"""
    siniestros = pd.read_sql(sql_siniestros, con) 
    if len(siniestros) == 0:
        siniestros = "No presenta"
   
    #SINIESTROS PATRIMONIAL
    sql_siniestros_historicos = f"""SELECT * FROM historicospatrimonial
    WHERE "key_id_tomador" = '{str(nit)}'"""
    siniestros_historicos = pd.read_sql(sql_siniestros_historicos, con) 
    if len(siniestros_historicos) == 0:
        siniestros_historicos = "No presenta"
    siniestros_historicos

    #PRIMAS DEVENGADAS
    sql_primas_historicas = f"""SELECT CAST ("PRIMA" AS INT) FROM primas_152
    WHERE "numero_documento_tomador" = '{str(nit)}'"""
    primas_152 = pd.read_sql(sql_primas_historicas, con) 
    if len(sql_primas_historicas) == 0:
        primas_152 = 0
    primas_152 


    totalLiquidado = 0
    totalLiquidadoHistorico = 0
    try:
            
        if siniestros is not str:
            for i in range(0, len(siniestros)):
                totalLiquidado = totalLiquidado + int(siniestros.iloc[i]['liquidado'])

            totalLiquidadoHistorico = 0

            for i in range(0, len(siniestros_historicos)):
                if siniestros_historicos.iloc[i]['liquidado_desde_2019'] != None:
                    totalLiquidadoHistorico = totalLiquidadoHistorico + int(siniestros_historicos.iloc[i]['liquidado_desde_2019'])
    except: 
        if siniestros != "No presenta":
            for i in range(0, len(siniestros)):
                totalLiquidado = totalLiquidado + int(siniestros.iloc[i]['liquidado'])

            totalLiquidadoHistorico = 0

            for i in range(0, len(siniestros_historicos)):
                if siniestros_historicos.iloc[i]['liquidado_desde_2019'] != None:
                    totalLiquidadoHistorico = totalLiquidadoHistorico + int(siniestros_historicos.iloc[i]['liquidado_desde_2019'])
    

    #PYG GENERAL


    if len(primas_152>0):
        PYG = int(primas_152.iloc[0][0])- totalLiquidadoHistorico
        severidad = totalLiquidadoHistorico/int(primas_152.iloc[0][0])
        if severidad >=0.6:
            print("SINIESTRALIDAD SUPERA LIMITE PERMITIDO")
        else:
            print("SINIESTRALIDAD PERMITIDA")
    else:
        PYG = "SIN HISTORICO"
        severidad = "SIN HISTORICO"
        print("NO HAY HISTORICO DEL CLIENTE")        
    


    edad = 0
    a = 0
    for i in range(0, len(maquinaria)):
        try:
            edad = edad + int(maquinaria.iloc[i][2])
            a = a+1
        except:
            pass
    edad = edad/a

    amenazaCiudad = []

    for i in range(0, len(amenazaMYE)):
        if fila["Municipio de operación de la maquinaria"] == amenazaMYE.iloc[i][2]:
            amenaza = amenazaMYE.iloc[i][1]
            amenazaCiudad = amenazaMYE.iloc[i][2::]
            break

    amenazaLista = ["Municipio", "Departamento", "Descripción", "Grupos Delictivos", "Descuento", "Deducible", "Complemento", "Mineria", "Extorción", "COB_TRANS", "COB_HURTO", "COB_AMIT"]


    valor_a_asegurar = maquinaria.iloc[0,8]
    marcasMaquinaria = maquinaria.iloc[0:len(maquinaria), 0]
    claseMaquinaria = maquinaria.iloc[0:len(maquinaria), 1]
    anoMaquinaria = maquinaria.iloc[0:len(maquinaria), 2]
    lineaMaquinaria = maquinaria.iloc[0:len(maquinaria), 3]
    autoPropMaquinaria = maquinaria.iloc[0:len(maquinaria), 7]
    sumaAseMaquinaria = maquinaria.iloc[0:len(maquinaria), 8]

    print(claseMaquinaria)
    for i in range(0, len(claseMaquinaria)):
        try:
            claseMaquinaria.iloc[i] = claseMaquinaria.iloc[i].replace("MAQUINARIA ", "")
        except:
            pass
    #CREACIÓN DEL PDF
    # Creaar instancia de PDF
    # Tamaño carta y unidad de medida en pulgadas
    pdf = FPDF(format='letter', unit='in')
    pdf.add_page()

    # Estableces fuente del texto
    pdf.set_font('Times','',10.0) 
    # Text height is the same as current font size
    th = pdf.font_size
    ac = 0.25

    # Effective page width
    epw = pdf.w - 2 * pdf.l_margin


    #PAGINA INTRODUCCIÓN
    print("Entro a generar PDF")
    pdf.image(r'Archivos/Logo.jpg', x =2.8, y = pdf.get_y(), w = 3, h = 3)
    pdf.set_font('Times','B', 18.0) 
    pdf.ln(ac*12)
    pdf.cell(epw, 2, "MAQUINARIA Y EQUIPO PARA CONTRATISTAS", align = 'C')
    pdf.ln(ac*2)
    pdf.cell(epw, 2, "INFORME DE", align = 'C')
    pdf.ln(ac)
    pdf.cell(epw, 2, "EVALUACIÓN DE RIESGOS", align = 'C')
    pdf.ln(ac*2)
    pdf.cell(epw, 2, tomador, align = 'C')
    pdf.ln(ac*10)
    pdf.set_font('Times','', 12.0) 
    pdf.cell(epw, 2, "INGENIERO DIGITAL MAQUINARIA Y EQUIPO", align = 'C')
    pdf.ln(ac*2)
    pdf.cell(epw, 2, "Fecha de realización:", align = 'C')
    pdf.ln(ac)
    now = datetime.now()

    pdf.cell(epw, 2, str(now.date()), align = 'C')

    pdf.add_page()

    # 1 - INFORMACIÓN PERSONAL
    informacionGeneral = [['Nombre Tomador / Asegurado', tomador],
    ['NIT', nit],
    ['Actividad Económica', str(ciiu_numero).replace("'", "")],
    ['Valor a asegurar', valor_a_asegurar],
    ['Dirección Comercial', ubicacionComercial],
    ['Direccion Operación', ubicacionOperacion],
    ['Ciudad Operación', str(data.iloc[0][18])], 
    ['Telefono', telefono_principal]]

    pdf.set_font('Times','B', 14.0) 
    pdf.cell(epw, 0.0, '1 - INFORMACIÓN GENERAL', align='C')
    pdf.set_font('Times','',10.0) 
    pdf.ln(0.3)


    for row in informacionGeneral:
        for i in row:
            pdf.cell(epw/2, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)

    pdf.ln(0.5)

    pdf.set_font('Times','B', 14.0) 
    pdf.cell(epw, 0.0, '2 - RELACIÓN DE MAQUINARIA', align='C')
    pdf.set_font('Times','',10.0) 
    pdf.ln(0.3)

    #DISTRIBCUIÓN MAQUINARIA Y EQUIPO ASEGURADA

    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "MAQUINARIA", border=1, align = 'C') 
    pdf.ln(ac)
    pdf.set_font('Times','',10.0) 

    tituloRelacion = [["Marca"],["Clase"],["Año de fabricación"], ["Linea"], ["Autopropulaso"], ["Valor Asegurado"]]
    for row in tituloRelacion:
        for i in row:
            pdf.cell(epw/6, ac, str(i), border=1, align = 'C') 
    pdf.ln(ac)

    for i in marcasMaquinaria:
        pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')

    y = 14.4
    pdf.set_font('Times','',7.0) 
    for i in claseMaquinaria:
        pdf.set_xy(epw/6+pdf.l_margin, pdf.l_margin+(ac*y))
        pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
        y = y+1


    pdf.set_font('Times','',10.0)
    
    y = 14.4

    for i in anoMaquinaria:
        pdf.set_xy((epw/6)*2+pdf.l_margin, pdf.l_margin+(ac*y))
        pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
        y = y+1


    y = 14.4
    for i in lineaMaquinaria:
        pdf.set_xy((epw/6)*3+pdf.l_margin, pdf.l_margin+(ac*y))
        pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
        y = y+1

    y = 14.4
    for i in autoPropMaquinaria:
        pdf.set_xy((epw/6)*4+pdf.l_margin, pdf.l_margin+(ac*y))
        pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
        y = y+1

    y = 14.4
    for i in sumaAseMaquinaria:
        pdf.set_xy((epw/6)*5+pdf.l_margin, pdf.l_margin+(ac*y))
        pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
        y = y+1


    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "Total valor asegurado = " +str(maquinaria.iloc[-1,6]), border=1, align = 'C') 
    pdf.ln(ac)

    sql_emis = f"""SELECT * FROM emis_0521 WHERE "n_id" = '{int(nit)}'"""
    emis = pd.read_sql(sql_emis, con) 

    # DESCRIPCION ACTIVIDAD ECONOMICA

    pdf.ln(ac*2)
    pdf.set_font('Times','B', 14.0) 
    pdf.cell(epw, 0.0, '3 - INFORMACIÓN EMPRESARIAL', align='C')
    pdf.set_font('Times','',10.0) 
    pdf.ln(0.3)


    try:
        pdf.set_font('Times', 'B', 14.0)
        pdf.cell(epw, ac, "DESCRIPCIÓN ACTIVIDAD ECONOMICA", border=1, align='C')
        pdf.set_font('Times', '', 10.0)
        if len(ciiu_numero)>0:
            pdf.ln(ac)
            pdf.cell(epw, ac*(len(ciiu_numero)+1), "", border = 1, align='C')
            for i in range(0,len(ciiu_dado)):
                pdf.ln(ac)
                pdf.cell(epw, ac, str(ciiu_numero[i])+ ": " + str(ciiu_dado[i]), border=0, align='C')
        pdf.ln(ac)
    except:
        pass

    #EMIS

    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, "REPORTE EMIS", border=1, align = 'C') 
    pdf.set_font('Times','',10.0) 
    locale.setlocale( locale.LC_ALL, '' )
    if len(emis != 0):
        empleados = int(emis['num_empleados'].values[0])
        ingresos = float(emis['ingresos_totales_ult_ano_usd'].values[0])

        vEmis = [['Fecha de Actualización', str(emis['fecha_actualizacion'].values[0]).replace("00:00:00 UTC", " ")],
        ['Estatus de la compañia', emis['estatus'].values[0]],
        ['Numero de empleados', emis['num_empleados'].values[0]],
        ['Tipo de compañia', emis['tipo_compania'].values[0]],
        ['Ingresos totales del ultimo año (USD)', emis['ingresos_totales_ult_ano_usd'].values[0]],
        ['Moneda capital del mercado', emis['moneda_capital_mercado'].values[0]],
        ['Año de ingresos totales', emis['ano_ingresos_totales'].values[0]]]
        
        for row in vEmis:
            pdf.ln(ac)
            for i in row:
                pdf.cell(epw/2, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)
        pdf.set_font('Times','B',12.0) 
        pdf.cell(epw, ac, "DESCRIPCIÓN SEGUN EMIS", border=1, align = 'C') 
        pdf.set_font('Times','',10.0) 
        pdf.ln(ac)
        var = 1
        if len(emis['descripcion'].values[0]) > 120:
            var = round(len(emis['descripcion'].values[0]) / 120) + 1
        pdf.cell(epw, ac*var , '', align='C', border = 1)
        pdf.ln(ac/8)
        a = 0
        b = 120
        for i in range(var):
            text = emis['descripcion'].values[0][a:b]
            a = a +120
            b = b +120
            pdf.cell(epw, ac, text, border=0, align = 'C')
            pdf.ln(ac) 
        pdf.ln(ac) 

    else:
        empleados = None
        ingresos = None
        pdf.ln(ac)
        pdf.cell(epw, ac, "SIN INFORMACIÓN", border=1, align = 'C')
        pdf.ln(ac)



    def reemplazar(cadena, dic):
        for k,v in dic.items():
            cadena=cadena.replace(k, v)
        return cadena
    print("Actividad empresarial completa")

    #SINIESTROS
    pdf.add_page()
    pdf.set_font('Times','B',14.0) 
    pdf.cell(epw, ac, "3 - SINIESTROS", border=0, align = 'C') 
    pdf.ln(ac*2)

    tituloSiniestros = [["#"],["NRO. DE POLIZA"],["NRO. DE SINIESTRO"],["CAUSA"],["FECHA"],["LIQUIDADO"]]
    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "HISTORICO DE SINIESTROS PRODCUTO 152", border=1, align = 'C') 
    pdf.set_font('Times','',8.0) 
    pdf.ln(ac)
    if type(siniestros) is not str:
        for row in tituloSiniestros:
            for i in row:
                pdf.set_font('Times','B',8.0) 
                pdf.cell(epw/6, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)
        pdf.set_font('Times','',8.0) 

        for i in range (len(siniestros)):
            pdf.multi_cell(epw/6 , ac, str(i+1), border = 1, align = 'C')
        
        y = 4

        for i in siniestros['numero_poliza']:
            pdf.set_xy((epw/6)+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
            y = y+1


        y = 4
    
        for i in siniestros['numero_siniestro']:
            pdf.set_xy((epw/6)*2+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
            y = y+1

        y = 4

        for i in siniestros['descripcion_causa']:
            pdf.set_xy((epw/6)*3+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
            y = y+1


        y = 4
        for i in siniestros['fecha_siniestro']:
            pdf.set_xy((epw/6)*4+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
            y = y+1

        y = 4
        for i in siniestros['liquidado']:
            pdf.set_xy((epw/6)*5+pdf.l_margin, pdf.l_margin+(ac*y))
            pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
            y = y+1

    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "Total liquidado historico = " +str(totalLiquidado), border=1, align = 'C') 
    pdf.ln(ac*3)



    tituloSiniestros = [["RAMO EMISIÓN"],["# POLIZAS VIGENTES"],["# RIESGOS VIGENTES"],["VALOR ASEGURADO"],["# SINIESTROS"], ['TOTAL LIQUIDADO']]
    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "HISTORICO DE SINIESTROS GENERAL", border=1, align = 'C') 
    pdf.set_font('Times','',8.0) 
    pdf.ln(ac)
    if type(siniestros) is not str:
        for row in tituloSiniestros:
            for i in row:
                pdf.set_font('Times','B',8.0) 
                pdf.cell(epw/6, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)
        pdf.set_font('Times','',8.0) 
        
        y = pdf.get_y()

    
        for i in siniestros_historicos['nombre_ramo_emision']:
            pdf.set_xy(pdf.l_margin, y)
            pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
            y = y+ac

        y = pdf.get_y() - (len(siniestros_historicos)*ac)
        for i in siniestros_historicos['cantidad_polizas_vigentes']:
            pdf.set_xy((epw/6)+pdf.l_margin, y)
            pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
            y = y+ac

        y = pdf.get_y() - (len(siniestros_historicos)*ac)
        for i in siniestros_historicos['cantidad_riesgos_vigentes']:
            pdf.set_xy((epw/6)*2+pdf.l_margin,y)
            pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
            y = y+ac
        y = pdf.get_y() - (len(siniestros_historicos)*ac)
        for i in siniestros_historicos['valor_asegurado']:
            pdf.set_xy((epw/6)*3+pdf.l_margin, y)
            pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
            y = y+ac


        y = pdf.get_y() - (len(siniestros_historicos)*ac)
        for i in siniestros_historicos['cantidad_siniestros_desde_2019']:
            pdf.set_xy((epw/6)*4+pdf.l_margin,y)
            pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
            y = y+ac
        y = pdf.get_y() - (len(siniestros_historicos)*ac)
        for i in siniestros_historicos['liquidado_desde_2019']:
            pdf.set_xy((epw/6)*5+pdf.l_margin, y)
            pdf.multi_cell(epw/6 , ac, str(i), border = 1, align = 'C')
            y = y+ac

    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "Total liquidado general desde 2019= " +str(totalLiquidadoHistorico), border=1, align = 'C') 
    pdf.ln(ac*2)

    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "POLIZAS DEVENGADAS HISTORICAS", border=1, align = 'C') 
    pdf.set_font('Times','',12.0) 
    pdf.ln(ac)
    if(len(primas_152>0)):
        pdf.cell(epw, ac, str(primas_152.iloc[0][0]), border=1, align = 'C') 
    else:
        pdf.cell(epw, ac, "SIN HISTORICO", border=1, align = 'C') 
    pdf.ln(ac*2)


    pdf.set_font('Times','',12.0) 
    pdf.cell(epw, ac, "PYG GENERAL", border=1, align = 'C') 
    pdf.ln(ac)
    if(len(primas_152>0)):
        pdf.cell(epw, ac, "Balance general = " +str(PYG), border=1, align = 'C') 
        pdf.ln(ac)
        pdf.cell(epw, ac, "Severidad(Liquidado) = " + str(severidad), border=1, align = 'C') 

    else:
        pdf.cell(epw, ac, "SIN HISTORICO", border=1, align = 'C') 
    pdf.ln(ac*2)



    pdf.add_page()

    # 4 - INFORMACIÓN RIESGO
    informacionRiesgo = [['Años de experiencia del tomador', str(fila[5])],
    ['Cantidad de maquinaria que posee', str(fila[6])],
    ['Realiza mantenimiento a los equipos', str(fila[7])],
    ['Certifica a sus colaboradores', str(fila[9])],
    ['Capacaita a su personal', str(fila[10])],
    ['Protege la movilización de la maquinaria', str(fila[13])],
    ['Tiene protocolos para hurto', str(fila[20])], 
    ['Los equipos estaran cerca a una fuente hidrica', str(fila[17])],
    ['Protecciones de seguridad', str(fila[15])],
    ['Puntaje Sistema de Gestión', str(fila[19])],
    ['La maquinaria es operada por personal propio',  str(fila[16])],
    ['Edad Promedio maquinaria', str(edad)]]


    pdf.set_font('Times','B', 14.0) 
    pdf.cell(epw, 0.0, '4 - INFORMACIÓN RIESGO', align='C')
    pdf.set_font('Times','',10.0) 
    pdf.ln(0.3)


    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "VULNERABILIDAD", border=1, align = 'C') 
    pdf.set_font('Times','',8.0) 
    pdf.ln(ac)

    for row in informacionRiesgo:
        for i in row:
            pdf.cell(epw/2, ac, str(i), border=1, align = 'C') 
        pdf.ln(ac)

    pdf.set_font('Times','B',12.0) 
    pdf.cell(epw, ac, "Puntaje de riesgo Vulnerabilidad = " +str(riesgoMYE), border=1, align = 'C') 
    pdf.ln(ac*2)


    tituloAmenaza= [["NOMBRE"],["DESCRIPCIÓN"]]
    pdf.cell(epw, ac, "AMENAZA", border=1, align = 'C') 
    pdf.set_font('Times','',8.0) 
    pdf.ln(ac)


    for row in tituloAmenaza:
        for i in row:
            pdf.set_font('Times','B',8.0) 
            if i == "DESCRIPCIÓN":
                pdf.cell(epw/1.25, ac, str(i), border=1, align = 'C') 
            else:
                pdf.cell(epw/5, ac, str(i), border=1, align = 'C') 
    pdf.ln(ac)



    y = pdf.get_y() + ac
    for i in range (0, len(amenazaLista)):
        pdf.multi_cell(epw/5 , ac, str(amenazaLista[i]), border = 1, align = 'C')

    y = pdf.get_y()+(47.3*ac)

    for i in range (1, len(amenazaCiudad)):
        pdf.set_font('Times', '',8.0) 
        pdf.set_xy((epw/5)+pdf.l_margin, (ac*y))
        pdf.multi_cell(epw/1.25 , ac, str(amenazaCiudad[i]), border = 1, align = 'C')
        y = y+1

    pdf.set_font('Times','B',12.0) 
    try:

        pdf.cell(epw, ac, "AMENAZA = " +str(amenaza.upper()), border=1, align = 'C') 
    except:
        pdf.cell(epw, ac, "AMENAZA = " +str(amenaza.upper()), border=1, align = 'C') 
    pdf.ln(ac*2)
    pdf.ln(0.5)

    #CONCEPTO ASEGURABILIDAD
    pdf.add_page()
    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(epw, ac, "CONCEPTO DE ASEGURABILIDAD", border=0, align='C')
    pdf.ln(ac*2)
    pdf.set_font('Times', 'B', 12.0)
    pdf.cell(epw/2, ac, "MAQUINARIA Y EQUIPO", border=1, align='C')
    y = pdf.get_y()
    pdf.ln(ac)
    pdf.set_font('Times', '', 10.0)

    rConcepto = [['Vulnerabilidad', str(riesgoMYE)],
    ['Amenaza', str(amenaza.upper())],
    ['Severidad', str(severidad)]]

    x = pdf.get_x()
    for row in rConcepto:
        for i in row:
            pdf.cell(epw/4, ac, str(i), border=1, align='C')
        pdf.ln(ac)

    amenaza = amenaza.upper()
    concepto = "Asegurable"

    if riesgoMYE == "ALTO" and amenaza == "MEDIA":
        concepto == "No asegurable"

    if riesgoMYE == "ALTO" and amenaza == "MEDIA ALTA":
        concepto == "No asegurable"
    
    if riesgoMYE == "ALTO" and amenaza == "ALTA":
        concepto = "No asegurable"
    
    if amenaza == "ALTA" and riesgoMYE == "MEDIO":
        concepto = "No asegurable"
    
    if amenaza == "ALTA" and riesgoMYE == "MEDIO ALTO":
        concepto = "No asegurable"


    if fila[16] == "No":
        concepto = "No asegurable"

    if severidad != "SIN HISTORICO":
        if severidad > 0.6:
            concepto = "No asegurable"

    if concepto == "Asegurable":
        pdf.image(r'Archivos/Check.png', x = epw/1.35, y = y , w = ac*4, h = ac*4)
    if concepto == "No asegurable":
        pdf.image(r'Archivos/Error.png', x = epw/1.35, y = y , w = ac*4, h = ac*4)

    pdf.ln(ac)
    pdf.set_font('Times', 'B', 12.0)
    pdf.cell(epw, ac, "Justificación", border=1, align='C')
    pdf.ln(ac)
    pdf.set_font('Times', '', 10.0)
    justificacion_negativa = []
    justificacion_positiva = []
    
    if (concepto == "Asegurable"):        
        justificacion_positiva.append(str("Se trata de una maquinara a cargo de la empresa "+tomador+" con un valor asegurado total de "+str(maquinaria.iloc[-1,6])+". Esta empresa ha presentado a lo largo de su vinculación con la compañia un PYG de " +str(PYG)
        + ". Gracias a el formulario de calificación se calculo un nivel de vulnerabilidad de "+str(riesgoMYE)+", y de acuerdo a la ciudad de operación la calificación de amenaza es "+ str(amenaza)
        +". Teniendo todo esto en cuenta se sugiere dar un concepto ASEGURABLE"))
    
    else:
        justificacion_negativa.append(str("Se trata de una maquinara a cargo de la empresa "+tomador+" con un valor asegurado total de "+str(maquinaria.iloc[-1,6])+". Esta empresa ha presentado a lo largo de su vinculación con la compañia un PYG de" +str(PYG)
        + ". Gracias a el formulario de calificación se calculo un nivel de vulnerabilidad de "+str(riesgoMYE)+", y de acuerdo a la ciudad de operación la calificación de amenaza es "+ str(amenaza)
        +  ". Teniendo todo esto en cuenta se sugiere dar un concepto NO ASEGURABLE"))
    

    if concepto == "Asegurable":
        
        for i in justificacion_positiva:
            pdf.multi_cell(epw , ac, str(i), border = 1, align = 'C')
            y = y+ac
            pdf.ln(ac)
    else: 
        
        for i in justificacion_negativa:
            pdf.multi_cell(epw , ac, str(i), border = 1, align = 'C')
            y = y+ac

    print("Concepto completo")

    
    pdf.output('/home/ingeniero_digital/principal/ID_MYE/' + tomador + ' ID_EYM.pdf', 'F')
    
    def cargarPdf(nombre):
        
        import os 

        #Drive 

        ruta_destino = '/ARCI/Informes ID MYE'
        ruta_origen = '/home/ingeniero_digital/principal/ID_MYE/'
        filename_out= nombre

        print(os.system(f"rclone copy '{ruta_origen}{filename_out}' ARCI:'{ruta_destino}'"))
    
    cargarPdf(str(tomador)+ ' ID_EYM.pdf')

    return{"File_name": file.filename}
    
    