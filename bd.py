import os
from sqlalchemy import create_engine

DB_USER = "postgres"
DB_PASS = "Pctr-3856.cpa.ppcolabs"
DB_NAME = "bitacoramantto"
INSTANCE = "app-colaboradores-d408c:us-central1:postgres-bsf"

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@/{DB_NAME}"
    f"?host=/cloudsql/{INSTANCE}"
)