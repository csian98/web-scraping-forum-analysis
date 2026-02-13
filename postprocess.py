import json
import re
import string

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import TfidfVectorizer

from gensim.models.doc2vec import Doc2Vec, TaggedDocument

nltk.download("stopwords")
nltk.download("punkt")
nltk.download("punkt_tab")

class PostProcessor:
    def __init__(self):
        self.stop_words = set(stopwords.words("english")) | set(string.punctuation)
        self.tfidf = TfidfVectorizer()
        
    def read_json(self, json_file: str):
        with open(json_file, 'r', encoding="utf-8") as fp:
            j = json.load(fp)
            
        return j
    
    def tokenize(self, text: str):
        tokens = word_tokenize(text.lower())
        return [token for token in tokens \
                if token not in self.stop_words and re.search(r"[a-zA-Z]", token) is not None]
    
    def get_topic(self, data, top_k=3):
        tfidf = TfidfVectorizer()
        
        cocat = list(map(lambda x: ' '.join(x), data))
        result = tfidf.fit_transform(cocat)
        terms = tfidf.get_feature_names_out()
        
        topics = []
        for idx, row in enumerate(result):
            row_array = row.toarray().flatten()
            top_indices = row_array.argsort()[::-1][:top_k]
            topics.append([terms[i] for i in top_indices])
            
        return topics
    
    def doc2vec(self, data, vector_size=5, min_count=2, epochs=50):
        cocat = list(map(lambda x: ' '.join(x), data))
        tagged_data = [TaggedDocument(words=word_tokenize(doc.lower()), tags=[str(i)]) \
                       for i, doc in enumerate(cocat)]
        model = Doc2Vec(vector_size=vector_size, min_count=min_count, epochs=epochs)
        model.build_vocab(tagged_data)
        model.train(tagged_data, total_examples=model.corpus_count, epochs=model.epochs)
        vector = [model.infer_vector(word_tokenize(doc.lower())) for doc in cocat]
        return vector
        
"""
if __name__ == "__main__":
    post = PostProcessor()
    data = post.read_json("data/static-scrapping.txt")
    data = [post.tokenize(f"{document['title']} {document['selftext']}") for document in data]
    topics = post.get_topic(data)
    
    vector = post.doc2vec(data, 2, 2, 50)
"""
