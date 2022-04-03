import subprocess
import time

migrate = subprocess.Popen('python3 manage.py migrate', shell=True)
migrate.wait(60)

nginx = subprocess.Popen('nginx -g "daemon off;"', shell=True)
backend = subprocess.Popen('python3 manage.py runserver 0.0.0.0:8000', shell=True)

while True:
    time.sleep(60)

    if nginx.poll() is not None:
        print("nginx is dead")
        exit()

    if backend.poll() is not None:
        print("backend is dead")
        exit()
