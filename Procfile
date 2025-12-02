release: python manage.py migrate --noinput && python load_initial_data.py
web: gunicorn backend.wsgi --log-file -
