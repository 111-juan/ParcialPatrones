
FROM python:3.11-slim


WORKDIR /code


COPY ./requirements.txt /code/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY ./ /code/app


EXPOSE 8000


CMD ["fastapi","run", "app/main.py", "--host","0.0.0.0", "--port", "8000", "--reload"]
                                                                                                