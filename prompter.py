import joblib
from snowflake_util import get_connection, get_model_status, embed_text
import pandas as pd

while True:
    con = get_connection()
    message = input("Please enter a message or keywords: ")
    status = get_model_status(con)

    if status:
        print("Model update in progress. Please wait a few minutes and try again.")
    else:
        model = joblib.load("model/kmeans_model.joblib")

        message_embedding = embed_text(con, message)
        message_cluster_id = model.predict([message_embedding])[0]
        print(f"The message belongs to cluster {message_cluster_id}.")

        print("Sample posts from the same cluster:")
        posts_with_embeddings_df = pd.read_csv("data/posts_with_clusters.csv")
        cluster_rows = posts_with_embeddings_df[
            posts_with_embeddings_df["CLUSTER_ID"] == message_cluster_id
        ]

        topic_counts = cluster_rows["TOPIC"].value_counts()
        print("\nCluster composition by subreddit:")
        for t, cnt in topic_counts.head(5).items():
            print(f"  {t:<20} {cnt}")

        print("\nSample posts from the same cluster:")
        sample = cluster_rows[["TITLE", "TOPIC", "TEXT"]].dropna().head(5)

        for _, row in sample.iterrows():
            title = str(row["TITLE"])[:80]
            topic = str(row["TOPIC"])
            text = str(row["TEXT"])[:120].replace("\n", " ")
            print(f"- [{topic}] {title}\n  {text}...\n")

    con.close()
