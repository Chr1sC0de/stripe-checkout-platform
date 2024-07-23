from api_lib.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")