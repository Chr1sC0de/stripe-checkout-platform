from bbm_backend.main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")