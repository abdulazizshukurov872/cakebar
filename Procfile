release: python manage.py migrate --noinput
web: python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
worker: python manage.py expire_unpaid_orders --loop
