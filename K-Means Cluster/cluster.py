"""
Assignment 5: K-Means. See the instructions to complete the methods below.
"""

from collections import Counter
from collections import defaultdict
import gzip
import math
import numpy as np

class KMeans(object):

    def __init__(self, k=2):
        """ Initialize a k-means clusterer. Should not have to change this."""
        self.k = k

    def cluster(self, documents, iters=10):
        """
        Cluster a list of unlabeled documents, using iters iterations of k-means.
        Initialize the k mean vectors to be the first k documents provided.
        After each iteration, print:
        - the number of documents in each cluster
        - the error rate (the total Euclidean distance between each document and its assigned mean vector), rounded to 2 decimal places.
        See Log.txt for expected output.
        The order of operations is:
        1) initialize means
        2) Loop
          2a) compute_clusters
          2b) compute_means
          2c) print sizes and error
        """
        self.doc_norm = defaultdict(lambda: 0.0)
        self.documents = documents
        
        self.mean_norms=[]
        self.mean_vectors = []
        for doc_id in range(len(documents)):
            self.doc_norm[doc_id] = self.sqnorm(documents[doc_id])
            if doc_id < self.k:
                self.mean_vectors.append(documents[doc_id])
                self.mean_norms.append(self.doc_norm[doc_id])
        
        for j in range(iters):
            
            self.compute_clusters(documents)
            self.compute_means()
            
            num_of_docs = []
            for i in self.k_cluster:
                num_of_docs.append(len(self.k_cluster[i]))
            
            print(num_of_docs)
            print(self.error(documents))

    def compute_means(self):
        """ Compute the mean vectors for each cluster (results stored in an
        instance variable of your choosing)."""
        self.mean_vectors = []
        for i in range(self.k):
            term_freq = Counter()
            for doc_id in self.k_cluster[i]:
                term_freq.update(self.documents[doc_id])
            if(len(self.k_cluster[i]) > 0):
                for term in term_freq:
                    term_freq[term] = 1.0 * term_freq[term] / len(self.k_cluster[i])
                self.mean_vectors.append(term_freq)
            self.mean_norms = []
            for t in self.mean_vectors:
                self.mean_norms.append(self.sqnorm(t))

    def compute_clusters(self, documents):
        """ Assign each document to a cluster. (Results stored in an instance
        variable of your choosing). """
        self.k_cluster = defaultdict(lambda: [])
        for doc_id in range(len(documents)):
            assign_cluster = -1
            min_distance = -1
            for cluster in range(self.k):
                distance = self.distance(documents[doc_id],self.mean_vectors[cluster],self.mean_norms[cluster]+self.doc_norm[doc_id])
                if ( distance < min_distance or assign_cluster == -1):
                    assign_cluster = cluster
                    min_distance = distance
            self.k_cluster[assign_cluster].append(doc_id)

    def sqnorm(self, d):
        """ Return the vector length of a dictionary d, defined as the sum of
        the squared values in this dict. """
        sqsum = 0.0
        for key in d.keys():
            sqsum += (d[key]**2)
        
        return sqsum

    def distance(self, doc, mean, mean_norm):
        """ Return the Euclidean distance between a document and a mean vector.
        See here for a more efficient way to compute:
        http://en.wikipedia.org/wiki/Cosine_similarity#Properties"""
        distance = mean_norm
        for term in doc:
            distance += - ( 2.0 * doc[term] * mean[term] )
            
        return float(math.sqrt(distance))

    def error(self, documents):
        """ Return the error of the current clustering, defined as the total
        Euclidean distance between each document and its assigned mean vector."""
        
        error = 0.0
        self.k_cluster_dist = defaultdict(lambda: [])
        for cluster in self.k_cluster.keys():
            for doc_id in self.k_cluster[cluster]:
                distance = self.distance(documents[doc_id],self.mean_vectors[cluster],self.mean_norms[cluster]+self.doc_norm[doc_id])
                error += distance
                self.k_cluster_dist[cluster].append((documents[doc_id],distance))
                
        return error

    def print_top_docs(self, n=10):
        """ Print the top n documents from each cluster. These are the
        documents that are the closest to the mean vector of each cluster.
        Since we store each document as a Counter object, just print the keys
        for each Counter (sorted alphabetically).
        Note: To make the output more interesting, only print documents with more than 3 distinct terms.
        See Log.txt for an example."""
        for cluster in self.k_cluster.keys():
            print("CLUSTER ",cluster)
            topdocs = sorted(self.k_cluster_dist[cluster],key=lambda x:x[1])
            count = 0
            for doc_id in range(len(topdocs)):
                if(len(topdocs[doc_id][0]) > 3):
                    str = ' '.join(sorted(topdocs[doc_id][0].keys())).encode('utf-8')
                    print(str.decode('utf-8'))
                    count += 1
                if count == n:
                    break

def prune_terms(docs, min_df=3):
    """ Remove terms that don't occur in at least min_df different
    documents. Return a list of Counters. Omit documents that are empty after
    pruning words.
    >>> prune_terms([{'a': 1, 'b': 10}, {'a': 1}, {'c': 1}], min_df=2)
    [Counter({'a': 1}), Counter({'a': 1})]
    """
    term_doc_freq = defaultdict(lambda: 0)
    
    for doc in docs:
        for term in doc.keys():
            term_doc_freq[term] += 1
            
    result = []
    for doc in docs:
        freq = Counter()
        for term in doc.keys():
            if term_doc_freq[term] >= min_df:
                freq[term] += doc[term]
        if freq:
            result.append(freq)
    
    return result

def read_profiles(filename):
    """ Read profiles into a list of Counter objects.
    DO NOT MODIFY"""
    profiles = []
    with gzip.open(filename, mode='rt', encoding='utf8') as infile:
        for line in infile:
            profiles.append(Counter(line.split()))
    return profiles


def main():
    profiles = read_profiles('profiles.txt.gz')
    print('read', len(profiles), 'profiles.')
    profiles = prune_terms(profiles, min_df=2)
    km = KMeans(k=10)
    km.cluster(profiles, iters=20)
    km.print_top_docs()

if __name__ == '__main__':
    main()
