from app import app, db
from app.models import Entities, Video, Category

# allows us to import these modules by running `flask shell`
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Entities': Entities, 'Video': Video, 'Category': Category}

from app.routes import *
