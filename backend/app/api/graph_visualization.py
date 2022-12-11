import pandas as pd
import numpy as np
from tqdm.notebook import tqdm
from itertools import combinations
from collections import Counter
from pyvis.network import Network
import logging
from app.core.config import SCHEMA_NAME, LOGS_DIR, LOGS_MESSAGE_FORMAT

logging.basicConfig(
    filename=LOGS_DIR, level=logging.DEBUG, format=LOGS_MESSAGE_FORMAT, filemode="a+"
)


class graph_model:
    def get_info(self, df: pd.DataFrame, columns_list) -> pd.DataFrame:
        data = pd.DataFrame()
        for col in columns_list:
            data[col] = df[col]
        return data

    def __init__(self, df: pd.DataFrame, size_cut=0):
        articles = self.get_info(df, ["id", "authors", "year"])
        if size_cut == 0:
            size_cut = articles.shape[0]
        dataset = []
        coauthors = set()
        for _, article in tqdm(articles.iloc[:size_cut].iterrows(), total=size_cut):
            logging.info(f"article is {article}")
            authors = sorted(author["id"] for author in article.authors)
            dataset.extend(
                [[author, "AUTHOR", article.id, article.year] for author in authors]
            )

            curr_coauthors = set(
                filter(lambda p: p not in coauthors, combinations(authors, 2))
            )
            dataset.extend(
                [
                    [author1, "COAUTHOR", author2, article.year]
                    for (author1, author2) in curr_coauthors
                ]
            )

            coauthors |= curr_coauthors

        self.data = np.array(dataset)

        connect_list = dict()
        for edge in self.data:
            if edge[1] not in connect_list:
                connect_list[edge[1]] = dict()
            if edge[0] not in connect_list[edge[1]]:
                connect_list[edge[1]][edge[0]] = [edge[2]]
            else:
                connect_list[edge[1]][edge[0]].append(edge[2])

        self.connect_list = connect_list
        author_weights = dict()
        for item in self.data:
            author_weights[item[0]] = 1
        for item in self.data:
            if item[1] == "AUTHOR":
                if item[0] not in author_weights:
                    author_weights[item[0]] += 1

        self.author_weights = author_weights

    def build_graph(
        self, start_ver="", edge_type="COAUTHOR", max_dfs_depth=10, use_weights=True
    ):
        self.graph = Network(notebook=True)
        edges_list = []
        nodes = []
        weights = []
        if len(start_ver) == 0:
            nodes = list(self.author_weights.keys())
            weights = list(self.author_weights.values())
            for item in self.data:
                if (
                    item[1] == edge_type
                    and item[0] in self.author_weights
                    and item[2] in self.author_weights
                ):
                    edges_list.append((item[0], item[2]))
                    edges_list.append((item[2], item[0]))
        else:
            queue = [(0, start_ver)]
            used_ver = set()
            used_ver.add(start_ver)
            while len(queue) > 0:
                d, v = queue.pop(0)
                if v in self.connect_list[edge_type]:
                    for to in self.connect_list[edge_type][v]:
                        if (
                            to not in used_ver
                            and d + 1 < max_dfs_depth
                            and to in self.author_weights
                        ):
                            queue.append((d + 1, to))
                            used_ver.add(to)
            nodes = list(used_ver)
            weights = [self.author_weights[v] for v in used_ver]
            for item in self.data:
                if item[1] == edge_type and item[0] in used_ver and item[2] in used_ver:
                    edges_list.append((item[0], item[2]))
                    edges_list.append((item[2], item[0]))
        if use_weights:
            self.graph.add_nodes(nodes, value=weights)
        else:
            self.graph.add_nodes(nodes)

        for edge in edges_list:
            self.graph.add_edge(edge[0], edge[1])

    def show_graph(self):
        self.graph.show_buttons(filter_=["physics"])
        return self.graph.generate_html()
