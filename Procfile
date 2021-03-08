web: gunicorn app:run_app --max-requests 2 -b 0.0.0.0:5000 --access-logfile=- --preload_app True 
heroku ps:scale web=1