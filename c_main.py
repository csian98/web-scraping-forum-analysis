from matplotlib.colors import ListedColormap
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from snowflake_util import get_connection, get_posts_embeddings
import joblib

np.seterr(divide="ignore", over="ignore", invalid="ignore")


def main():
    con = get_connection()
    posts_with_embeddings_df = get_posts_embeddings(con)
    X = posts_with_embeddings_df["EMBEDDING"].to_list()

    model = KMeans(n_clusters=2, init="k-means++", n_init="auto")
    model.fit(X)
    joblib.dump(model, "model/kmeans_model.joblib")

    pca = PCA(n_components=2)
    pca.fit(X)
    dX = pca.transform(X)

    y_pred = model.predict(X)

    posts_with_embeddings_df["CLUSTER_ID"] = y_pred
    posts_text_id_0 = posts_with_embeddings_df[
        posts_with_embeddings_df["CLUSTER_ID"] == 0
    ]["TEXT"].tolist()
    posts_text_id_1 = posts_with_embeddings_df[
        posts_with_embeddings_df["CLUSTER_ID"] == 1
    ]["TEXT"].tolist()
    print("\nSample posts from Cluster 0:")
    for text in posts_text_id_0[:2]:
        print(f"- {text[:100]}...")  # Print first 100 characters of the post text

    print("\nSample posts from Cluster 1:")
    for text in posts_text_id_1[:2]:
        print(f"- {text[:100]}...")  # Print first 100 characters of the post text

    xx = [x[0] for x in dX]
    xy = [x[1] for x in dX]

    cluster_cmap = ListedColormap(["tab:blue", "tab:orange"])

    fig, ax = plt.subplots(1, 1, figsize=(6, 5))
    ax.scatter(xx, xy, c=y_pred, cmap=cluster_cmap)
    ax.set_title("clustering (k=2)")
    plt.show()

    # cmap = {label: i for i, label in enumerate(labels)}

    # fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    # axes[0].scatter(xx, xy, c=[cmap[yy] for yy in y])
    # axes[0].set_title("topic")
    # axes[1].scatter(xx, xy, c=y_pred)
    # axes[1].set_title("clustering")
    # plt.show()


if __name__ == "__main__":
    main()
