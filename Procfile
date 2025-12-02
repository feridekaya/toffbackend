release: python manage.py migrate --noinput && python load_initial_data.py
web: gunicorn backend.wsgi --bind 0.0.0.0:$PORT --log-file -
