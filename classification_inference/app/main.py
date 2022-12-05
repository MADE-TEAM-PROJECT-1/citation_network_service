import os

import dill
import gdown
from app import schemas
from fastapi import FastAPI, status

app = FastAPI()
classifier = None


@app.on_event("startup")
def startup_event():
    gdown.download(
        url=os.environ["MODEL_LINK"],
        output="models/transformer.pkl",
        quiet=False,
        fuzzy=True,
    )
    global classifier
    with open("models/transformer.pkl", "rb") as file:
        classifier = dill.load(file)


@app.get("/health")
def health():
    if classifier is None:
        return status.HTTP_503_SERVICE_UNAVAILABLE
    return status.HTTP_200_OK


@app.post("/predict_tags", response_model=schemas.Predictions)
def predict_tags(article: schemas.Article):
    return schemas.Predictions(
        predictions=classifier.predict(article.title + " " + article.abstract)
    )
