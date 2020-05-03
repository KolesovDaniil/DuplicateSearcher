from flask_migrate import Migrate

from app.factory import create_app
from app.database import db

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
