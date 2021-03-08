web: gunicorn app:run_app --max-requests 2 -b 0.0.0.0:5000 --access-logfile=-
heroku ps:scale web=1