:: set environment varibles (app and debug mode)
set FLASK_APP=run:app
set FLASK_ENV=development
flask init-db
flask run
pause