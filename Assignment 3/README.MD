# Facts Search

## General Notes:

* It's recommended if you download the whole folder along with the cache
* cache folder basically contains the tokens dictionary and the fitted svd (which will save you time while running the code)
* Caching the svd would probably save time and prevent a possible crash due to high memory consumption
* I generated the requirements through conda on ubuntu (didn't test on windows)

## What I am doing?

### Sentence Normalization:
* Common processing pipeline for both queries and training data
* Tokenize sentences, remove stopwords and punctuation, lowercase all words, and generate the stemming
* I chose stemming over lemmatization because we already have a very sparse matrix, stemming would shrink the sparse nature more than lemmatization for example

### Generating the matrix
* Each doc here is basically a sentence or a fact
* I am constructing a sparse matrix where rows are the documents and columns basically are the normalized tokens.
* Each cell in the normalized matrix corresponds to the token count in a doc
* Running SVD on the sparse matrix and keeping only 75% of the variance

I set the number of components to 1600 which kept around 75% of the variance

We need almost double the components to have a +8% it means that we included enough principal
components, the variance curve is getting flat around the 1500-1600 point (something similar to the elbow rule)
    
I think using svd in this particular case isn't ideal at all.

The high number of principal components to keep such an average variance suggests that the matrix is sparse,
    in a way that if we assuem that every principal component is a topic, the topics are mostly single or 2 tokens at
    most, which also means that probably implementing a normal inverted index would have yielded the same or similar results.
    
### Building the index

Building AnnoyIndex as suggested in the hw description. Didn't dive into much detail about tuning it the best.

### Answering queries:
* Run the normalization process on the query sentence
* Get the corresponding frequency doc/vector
* Embed the vector using SVD
* Call the annoy-index api and get the relevant results

# Babel Echo

## General Notes:
* Basically you could just run the code
* You may need to wait few seconds after seeing the statement `start recording` because it seems like the python interpreter takes few seconds to setup the socket (or connection not sure) then you could start recording
* I added the credentials file
* I submitted the video to moodle
