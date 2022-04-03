FROM node:17-alpine as frontend-build
WORKDIR /app
COPY ./potoforio-frontend/ .
RUN npm install
RUN npm run build


FROM nginx:1.21-alpine as runtime

RUN apk add python3 py3-pip build-base --no-cache

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

VOLUME ["/data"]
ENV DB_DIR=/data/

COPY ./manage.py .
COPY ./potoforio/ ./potoforio
COPY --from=frontend-build /app/dist ./dist

COPY ./packaging/nginx.conf /etc/nginx/conf.d/default.conf
COPY ./packaging/entrypoint.py ./entrypoint.py

CMD ["python3", "./entrypoint.py"]
