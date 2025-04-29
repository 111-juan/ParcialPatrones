FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de dependencias
COPY ./requirements.txt /app/requirements.txt

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copiar el resto del código de la aplicación al contenedor
COPY ./ /app

# Exponer el puerto en el que se ejecutará la aplicación
EXPOSE 5500

# Comando para ejecutar la aplicación con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5500", "--reload"]
