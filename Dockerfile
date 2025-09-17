FROM python:3

WORKDIR /edu_app

COPY . .

RUN rm -rf .venv

RUN pip install --upgrade pip

RUN mkdir -p static

RUN pip install -r requirements.txt

CMD uvicorn main:app --host 0.0.0.0 --port 8011 --reload
