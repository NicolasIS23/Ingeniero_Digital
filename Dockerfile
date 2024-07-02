FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

USER root

RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python3 get-pip.py

WORKDIR /app

COPY requirements.txt .
COPY Archivos /app/Archivos
COPY Archivos/Mapas /app/Archivos/Mapas
COPY Archivos/PDF /app/Archivos/PDF
COPY Archivos/PNG /app/Archivos/PNG
COPY prueba.py /app/

RUN python3 -m pip install -r requirements.txt

EXPOSE 8093

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8093"]

