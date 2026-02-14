import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from postprocess import *
from snowflake_util import get_connection, get_posts_embeddings

np.seterr(divide="ignore", over="ignore", invalid="ignore")


def main():
    # post = PostProcessor()
    # data = post.read_csv("data/raw_posts.csv")
    # data = data.fillna('')
    # X = (data["title"] + data["selftext"]).to_list()
    # X = list(map(lambda x: post.tokenize(post.clean_text(x)), X))
    # X = post.doc2vec(X, 20, 2, 50)
    con = get_connection()
    posts_with_embeddings_df = get_posts_embeddings(con)
    X = posts_with_embeddings_df["EMBEDDING"].to_list()

    y = posts_with_embeddings_df["TOPIC"].to_list()
    labels = np.unique(y)

    model = KMeans(n_clusters=len(labels), init="k-means++", n_init="auto")
    model.fit(X)

    pca = PCA(n_components=2)
    pca.fit(X)
    dX = pca.transform(X)

    y_pred = model.predict(X)

    xx = [x[0] for x in dX]
    xy = [x[1] for x in dX]

    cmap = {label: i for i, label in enumerate(labels)}

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].scatter(xx, xy, c=[cmap[yy] for yy in y])
    axes[0].set_title("topic")
    axes[1].scatter(xx, xy, c=y_pred)
    axes[1].set_title("clustering")
    plt.show()


if __name__ == "__main__":
    main()
