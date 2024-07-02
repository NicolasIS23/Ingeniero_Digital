# Ingeniero Digital

## Descripción

El ingeniero digital (ID) es una API/herramienta digital cuya función es el análisis de predios via remota para el estudio de asegurabilidad de un cliente. El ID solo requiere de los siguientes inputs para hacer el estudio del predio: NIT de la empresa o C.C de la persona y dirección del predio. El resultado que entrega el ID es un informe de aproximadamente 15 páginas en el que se encuentra información de la empresa y un datos relevantes para el estudio de asegurabilidad del cliente como Capas de Amenaza, Actividad económica del cliente, Histórico de Siniestros, etc. Además escribe todos los datos analizados en una base de datos para un posterior estudio analítico.

### Generalidades del Proyecto
- **Tipo de Impacto**: Automatización de procesos manuales de generación de informes y conceptos de ingeniería.
- **Tiempo de ejecución**: Alrededor de 155 segundos
- **Gerencia**: Gerencia de Vivienda e ingeniería.
- **Línea de Negocio**: Propiedad.
- **Responsables**:
  - **Backend**: Nicolás Ibarra
- **Enlaces de Interés**:
  - [Link API](http://35.153.192.47:8093/docs#/)

## Implementación

La solución está estructurada de la siguiente manera:

### Estructura del Proyecto
- **Archivos/**: Carpeta que contiene los archivos estáticos que consume el ID.
- **tests/**: Carpeta que contiene los scripts de prueba.
- **app.py**: Código de la solución.
- **requirements.txt**: Dependencias del proyecto.
- **logAPI1**: Archivo para visualizar la ejecución de la API.
- **Dockerfile**: Para crear una imagen Docker y ejecutar el proyecto en un contenedor.
- **README**: Instructivo del proyecto.

### Documentos Relacionados
- Carpeta **Archivos**: Contiene todos los archivos estáticos que consume el ID.
- **Dockerfile**: Para ejecutar el código en un contenedor de manera automática y continua.
- **requirements.txt**: Lista de dependencias necesarias.

## Requisitos

Para ejecutar la solución, necesita los siguientes elementos:

### Dependencias
- Python 3.11.4
- Librerías especificadas en `requirements.txt`:
  - `pdfplumber`
  - `pandas`
  - `requests`
  - `tiktoken`

### Pasos para la Ejecución local
1. Instalar las dependencias:
   ```sh
   pip install -r requirements.txt
2. Ejecutar API localmente:
   ```sh
   uvicorn app:app --reload --port 800X
3. Ejecutar el script con Docker (opcional):
    1. Crear imagen.
       ```sh
       docker build -t ingeniero_digital/1.0.0 .
    2. Crear contenedor.
       ```sh
       docker run -d --name ingeniero_digital_1.0.0 ingeniero_digital/1.0.0 .
    3. El informe queda subido a la siguiente carpeta de Drive: (https://drive.google.com/drive/u/0/folders/1riwAn_B0eWNCq6yGff0FC4_X5zO2HD32
       
#