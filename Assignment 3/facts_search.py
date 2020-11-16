import json
import pprint
import pickle
import nltk
import itertools
import string
import numpy as np
import os
from nltk.stem import SnowballStemmer

TRAINING_FILE = "./train.jsonl"

nltk.download('punkt')
nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words('english')
stemmer = SnowballStemmer("english")

# a dictionary for mapping tokens to indices in matrix
tokens_index = {}


def tokenize(text):

    # this function tokenizes and stems both queries and original documents
    from nltk.tokenize import word_tokenize

    tokens = word_tokenize(text)
    tokens = [token.lower() for token in tokens if token not in stopwords and token not in string.punctuation]
    tokens = [stemmer.stem(token) for token in tokens]

    return tokens


def build_TDM_matrix(training_data):
    from collections import Counter
    from scipy.sparse import coo_matrix

    # a counter for each doc to count tokens
    doc_counters = []

    for sentence_idx, instance in enumerate(training_data):
        text = instance['claim']
        tokens = tokenize(text)

        # check if the token is present in the global tokens dictionary
        for token in tokens:
            try:
                _ = tokens_index[token]
            except KeyError:
                l = len(tokens_index)
                tokens_index[token] = l

        # add the current token to the current document counter
        doc_counters.append(Counter(tokens))

    # construct a sparse matrix (rows = docs) (cols = stemmed normalized tokens)
    rows, cols, values = [], [], []

    for sentence_idx, counter in enumerate(doc_counters):
        num_tokens = len(counter)
        rows.extend(itertools.repeat(sentence_idx, num_tokens))
        cols.extend(map(tokens_index.get, counter.keys()))
        values.extend(counter.values())

    _matrix = coo_matrix((values, (rows, cols)), dtype=np.int8)
    print(_matrix.shape)

    return _matrix


def perform_svd(matrix):

    """
    perform truncated svd on the sparse matrix
    I set the number of components to 1600 which kept around 75% of the variance
    As you can see since we need almost double the components to have a +8% it means that we included enough principal
    components, the variance curve is getting flat around the 1500-1600 point (something similar to the elbow rule)
    I think using svd in this particular case isn't ideal at all
    The high number of principal components to keep such an average variance suggests that the matrix is sparse,
    in a way that if we assuem that every principal component is a topic, the topics are mostly single or 2 tokens at
    most, which also means that probably implementing a normal inverted index would have yielded the same or similar results.
    """

    from sklearn.decomposition import TruncatedSVD
    components = 1600

    svd = TruncatedSVD(n_components=components)
    svd.fit(matrix)

    print("Number of componenets :: ", components)
    assert components > 0

    return svd


def build_index(svd, matrix):
    from annoy import AnnoyIndex

    """
    Build the annoy index
    First transform the original matrix using the fitted svd
    add them row by row
    """

    print("Started building index")
    print("Getting the embedded matrix of documents")
    transformed = svd.transform(matrix)
    components = transformed.shape[1]
    index = AnnoyIndex(components, "angular")

    print("Adding documents to the index")
    for idx, row in enumerate(transformed):
        index.add_item(idx, row.flatten())

    index.build(10, n_jobs=-1)
    print("Index finished")
    return index


def process_query(sentence , index , svd):

    global_tokens_count = len(tokens_index)

    # tokenize and normalize the query
    tokens = tokenize(sentence)

    # build a counter vector
    vec = np.zeros(shape=(1, global_tokens_count))
    for token in tokens:
        idx = tokens_index.get(token, None)
        if idx:
            vec[0][idx] += 1

    # project the query document vector
    projection = svd.transform(vec).flatten()

    # get closest 10 documents
    ret = index.get_nns_by_vector(projection , 10 , include_distances = False)

    return [training_data[idx]['claim'] for idx in ret]


def start_shell(index, svd):

    print("Start writing sentences to search for, write `quit!` to terminate")
    global_tokens_count = len(tokens_index)
    print("Number of global tokens :: " , global_tokens_count)
    while True:
        sentence = input()
        if sentence == "quit!":
            break
        pprint.pprint(process_query(sentence, index, svd) , indent=3)

def run_sample_queries(index , svd):
    queries = [
        "Moscow is the capital of Russia",
        "Linux is an operating system",
        "Barcelona club",
        "Game of thrones",
        "crime series"
    ]
    for query in queries:
        print("Query :: " , query)
        print("Suggestions :: ")
        pprint.pprint(process_query(query , index , svd) , indent=3)

if __name__ == '__main__':

    from scipy.sparse import save_npz, load_npz

    os.makedirs('./cache', exist_ok=True)

    with open(TRAINING_FILE, 'r') as f:
        training_data = [json.loads(line) for line in f.readlines()]

    try:

        _matrix = load_npz('./cache/matrix.npz')
        with open('./cache/tokens_dict', 'r') as f:
            tokens_index = json.load(f)
        print("Matrix Loaded from cache")
        print("Tokens Dictionary loaded from cache")

    except IOError:

        print("Cache not found, generating the matrix")

        _matrix = build_TDM_matrix(training_data)
        save_npz('./cache/matrix.npz', _matrix)

        with open('./cache/tokens_dict', 'w') as f:
            json.dump(tokens_index, f)

    print("Matrix shape : ", _matrix.shape)

    try:
        with open('./cache/svd.pkl', 'rb') as f:
            _svd = pickle.load(f)
        print("SVD loaded from cache")

    except FileNotFoundError:
        print("Fitting SVD")
        _svd = perform_svd(_matrix)
        with open('./cache/svd.pkl', 'wb') as f:
            pickle.dump(_svd, f)

    print("Variance kept :: " , np.sum(_svd.explained_variance_ratio_))
    _index = build_index(_svd, _matrix)
    run_sample_queries(_index , _svd)
    start_shell(_index , _svd)
