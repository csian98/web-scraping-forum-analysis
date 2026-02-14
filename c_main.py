import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from postprocess import *

def main():
    post = PostProcessor()
    data = post.read_csv("data/raw_posts.csv")
    data = data.fillna('')
    X = (data["title"] + data["selftext"]).to_list()
    X = list(map(lambda x: post.tokenize(post.clean_text(x)), X))
    X = post.doc2vec(X, 2, 2, 50)
    
    # y = post.get_topic(X, 3)
    y = data["subreddit"].to_list()
    labels = np.unique(y)

    model = KMeans(n_clusters=len(labels), init="k-means++", n_init="auto")
    model.fit(X)

    y_pred = model.predict(X)

    xx = [x[0] for x in X]
    xy = [x[1] for x in X]

    cmap = {label:i for i, label in enumerate(labels)}

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].scatter(xx, xy, c=[cmap[yy] for yy in y])
    axes[0].set_title("topic")
    axes[0].legend(cmap)
    axes[1].scatter(xx, xy, c=y_pred)
    axes[1].set_title("clustering")
    
    plt.show()


if __name__ == "__main__":
    main()
    
