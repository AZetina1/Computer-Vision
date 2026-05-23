FROM python:3.10-slim

# Instalar dependencias del sistema necesarias para OpenCV y gráficos headless
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

# Comando para arrancar la app en el puerto 7860 (el puerto estándar que exige Hugging Face)
CMD ["uvicorn", "main.app", "--host", "0.0.0.0", "--port", "7860"]