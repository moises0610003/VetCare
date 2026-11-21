import os

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4".format(
        user=os.getenv("DB_USER", "root"), password=os.getenv("DB_PASSWORD", ""), host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "3306"), name=os.getenv("DB_NAME", "veterinaria_db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
