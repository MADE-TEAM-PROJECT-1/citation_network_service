import os
import pickle
import uvicorn
import logging
import numpy as np
import math
import gdown
from fastapi import FastAPI, status
from typing import List, Tuple
from numpy import ndarray
from ampligraph.discovery import find_nearest_neighbours
from ampligraph.utils import restore_model
from scipy.spatial import distance

from app import schemas


app = FastAPI()

logger = logging.getLogger("logging_service")
logger.setLevel(logging.INFO)
formatter_stdout = logging.Formatter("%(asctime)s\t%(levelname)s\t%(name)20s\t%(message)s",
                                     datefmt="%Y-%m-%d %H:%M:%S")
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter_stdout)
logger.addHandler(stream_handler)

model_name = "Graph model"
version = "v1.0.0"
model = None


@app.get("/")
def main() -> str:
    entry_point = "It is entry point of our service. "
    return entry_point


@app.get('/info')
async def model_info() -> dict:
    return {
        "name": model_name,
        "version": version
    }


@app.on_event("startup")
def load_model():
    logger.info("Server started")
    logger.info("Start loading model")
    global model
    url = os.environ["MODEL_LINK"]
    if url is None:
        err = f"Link to model {url} is None"
        logger.info(err)
        raise RuntimeError(err)

    model_path = os.environ["MODEL_PATH"]

    gdown.download(
        url=url,
        output=model_path,
        quiet=False,
        fuzzy=True,
    )

    model = restore_model(model_path)
    logger.info("Model was loaded successful")


@app.get("/health")
def health_model():
    if model is None:
        return status.HTTP_503_SERVICE_UNAVAILABLE
    return status.HTTP_200_OK


def get_neighbors_one_entities(
    model, entities, n_neighbors: int, metric: str = "cosine"
) -> Tuple[ndarray, ndarray]:
    """
    @model: fitted graph model
    @entities: list of entities id's (article of author)
    @n_neighbors: number of nearest neighbors to be returned
    @metric: metric for nearest neighboors search
    return: (neighbors, dist), where neighbors and dist are ndarrays of shape (len(entities), n_neighbors)
            where neighboors is ndarray of n_neighbors for each entity from entities
            and ndarray of distances
    """
    neighbors, dist = find_nearest_neighbours(
        model, entities=entities, n_neighbors=n_neighbors + 1, metric=metric
    )  # прибавляем 1 к числу соседей, так как среди ближайших соседей функция вернет саму статью тоже (на 1 месте)
    # поэтому мы просто возьмем k статей после первой
    return neighbors, dist


@app.on_event("startup")
def load_all_embeddings():
    logger.info("Start loading embeddings")
    url = os.environ["ARTICLE_EMBED"]
    if url is None:
        err = f"Link to aticles embeddings {url} is None"
        logger.info(err)
        raise RuntimeError(err)
    article_embed__path = os.environ["ARTICLE_EMBED_PATH"]
    gdown.download(
        url=url,
        output=article_embed__path,
        quiet=False,
        fuzzy=True,
    )
    global articles_embeddings
    with open(article_embed__path, 'rb') as f:
        articles_embeddings = np.load(f, allow_pickle=True).item()
    logger.info("Embeddings load successful")


@app.get("/health")
def health_embeddings():
    if articles_embeddings is None:
        return status.HTTP_503_SERVICE_UNAVAILABLE
    return status.HTTP_200_OK


def find_nearest_neighbors(receive_id, k, mean_article):
    dict_dists = dict()
    for key, val in articles_embeddings.items():
        dict_dists[key] = distance.cosine(mean_article, val)
    sorted_dict_dists = dict(sorted(dict_dists.items(), key=lambda kv: kv[1]))
    nearest_neighbor = []
    list_keys = list(sorted_dict_dists.keys())
    # не хотим рекомендовать пользователю статьи, которые он уже видел, поэтому исключаем статьи с ключами из receive_id
    i = 0
    while True:
        if list_keys[i] not in receive_id:
            nearest_neighbor.append(list_keys[i])
            i += 1
        else:
            i += 1
        if len(nearest_neighbor) >= k:
            break
    return nearest_neighbor


def get_neighbors_for_user(receive_id, k):
    n = len(receive_id)
    weights = np.zeros(n)
    for i in range(n):
        weights[n - i - 1] = 1. / math.log(i + 2)  # хотим чтобы веса увеличивались слева направо
        #  так как статьи приходят от самой поздней к самой новой
    weights = weights / sum(weights)
    articles = model.get_embeddings(receive_id)
    mean_article = np.average(articles, axis=0, weights=weights)
    # теперь надо по эмбеддингу найти ближайшие статьи и вернуть их

    nearest_neighbors = find_nearest_neighbors(receive_id, k, mean_article)
    return nearest_neighbors


@app.post('/get_neighbors', response_model=schemas.Predictions)
async def model_predict(input: schemas.ReceiveId):
    receive_id = input.__dict__['id']
    n_neighbors = 5
    if not receive_id:
        # холодный старт
        neighbors = [
            '53e9986eb7602d97020ab93b',
            '53e9b587b7602d97040c7931',
            '53e9bb52b7602d9704790954',
            '53e9a95db7602d97032b5715',
            '53e9983db7602d9702065035'
        ]
    elif len(receive_id) == 1:
        # либо пользователь посмотрел только одну статью, и ему надо рекомендовать похожие
        # либо это автор и ему надо рекомендовать соавторов
        neighbors, dist = get_neighbors_one_entities(
            model, receive_id, n_neighbors
        )
        neighbors = neighbors[0]
        neighbors = neighbors[1:6].tolist()

    else:
        # В этом случае пользователь посмотрел больше одной статьи и мы хотим взять среднее
        neighbors = get_neighbors_for_user(receive_id, n_neighbors)

    return schemas.Predictions(neighbors=neighbors)
