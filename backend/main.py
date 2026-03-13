from pathlib import Path
from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from routers import template

app = FastAPI()

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
config = dotenv_values(ENV_PATH)

app.include_router(template.router)


# -- MongoDB connection lifecycle --

@app.on_event("startup")
def startup_db_client():
    # Initialisation du client MongoDB lors du démarrage de l'application
    app.mongodb_client = MongoClient(config["MONGO_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    print(f"Connected to MongoDB — base : {config['DB_NAME']}")

@app.on_event("shutdown")
def shutdown_db_client():
    # Fermeture du client MongoDB lors de l'arrêt de l'application
    app.mongodb_client.close()
    print("Connexion MongoDB closed")

@app.get("/")
async def root():
    return {"message": "Welcome to the Deal Viewers Project!"}