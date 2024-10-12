from flask import Flask, render_template, request, jsonify
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

app = Flask(__name__)


# TODO: Fetch dataset, initialize vectorizer and LSA here
newsgroups_data = fetch_20newsgroups(subset='all', remove=('headers', 'footers', 'quotes'))
stop_words = stopwords.words('english')

vectorizer = TfidfVectorizer(stop_words=stop_words)
X_tfidf = vectorizer.fit_transform(newsgroups_data.data)

n_components = 100  # Number of dimensions
lsa = TruncatedSVD(n_components=n_components)
X_lsa = lsa.fit_transform(X_tfidf)

def search_engine(query):
    """
    Function to search for top 5 similar documents given a query
    Input: query (str)
    Output: documents (list), similarities (list), indices (list)
    """
    query_vec = vectorizer.transform([query])
    query_lsa = lsa.transform(query_vec)
    similarities = cosine_similarity(query_lsa, X_lsa).flatten()
    top_indices = similarities.argsort()[-5:][::-1]
    top_similarities = similarities[top_indices]
    top_documents = [newsgroups_data.data[i] for i in top_indices]
    return top_documents, top_similarities, top_indices

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    documents, similarities, indices = search_engine(query)

    # Convert NumPy arrays to lists
    documents = documents.tolist() if isinstance(documents, np.ndarray) else documents
    similarities = similarities.tolist() if isinstance(similarities, np.ndarray) else similarities
    indices = indices.tolist() if isinstance(indices, np.ndarray) else indices

    # Return JSON response
    return jsonify({'documents': documents, 'similarities': similarities, 'indices': indices})


if __name__ == '__main__':
    app.run(debug=True)
