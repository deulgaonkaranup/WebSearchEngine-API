""" Assignment 2
"""
import abc
from collections import defaultdict
import math

import index

def idf(term, index):
    """ Compute the inverse document frequency of a term according to the
    index. IDF(T) = log10(N / df_t), where N is the total number of documents
    in the index and df_t is the total number of documents that contain term
    t.

    Params:
      terms....A string representing a term.
      index....A Index object.
    Returns:
      The idf value.

    >>> idx = index.Index(['a b c a', 'c d e', 'c e f'])
    >>> idf('a', idx) # doctest:+ELLIPSIS
    0.477...
    >>> idf('d', idx) # doctest:+ELLIPSIS
    0.477...
    >>> idf('e', idx) # doctest:+ELLIPSIS
    0.176...
    """
    if term in index.index:
        return math.log10( len(index.documents) / index.doc_freqs[term] )
    
    return 0.0


class ScoringFunction:
    """ An Abstract Base Class for ranking documents by relevance to a
    query. """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def score(self, query_vector, index):
        """
        Do not modify.

        Params:
          query_vector...dict mapping query term to weight.
          index..........Index object.
        """
        return


class RSV(ScoringFunction):
    """
    See lecture notes for definition of RSV.

    idf(a) = log10(3/1)
    idf(d) = log10(3/1)
    idf(e) = log10(3/2)
    >>> idx = index.Index(['a b c', 'c d e', 'c e f'])
    >>> rsv = RSV()
    >>> rsv.score({'a': 1.}, idx)[1]  # doctest:+ELLIPSIS
    0.4771...
    """

    def score(self, query_vector, index):
        res = defaultdict(lambda: 0)
        N = len(index.documents)
        for term in query_vector:
            if term in index.index:
                for doclist in index.index[term]:
                        res[doclist[0]] += idf(term, index)
        return res

    def __repr__(self):
        return 'RSV'


class BM25(ScoringFunction):
    """
    See lecture notes for definition of BM25.

    log10(3) * (2*2) / (1(.5 + .5(4/3.333)) + 2) = log10(3) * 4 / 3.1 = .6156...
    >>> idx = index.Index(['a a b c', 'c d e', 'c e f'])
    >>> bm = BM25(k=1, b=.5)
    >>> bm.score({'a': 1.}, idx)[1]  # doctest:+ELLIPSIS
    0.61564032...
    """
    def __init__(self, k=1, b=.5):
        self.k = k
        self.b = b

    def score(self, query_vector, index):
        
        res = defaultdict(lambda: 0)
        N = len(index.documents)
        K = self.k
        B = self.b
        for term in query_vector:
            if term in index.index:
                term_idf = idf(term, index)
                for doc_id,term_freq in index.index[term]:
                    res[doc_id] += term_idf*(K+1)*term_freq/(K*((1-B)+(1.*B*index.doc_lengths[doc_id]/index.mean_doc_length))+term_freq)
        return res

    def __repr__(self):
        return 'BM25 k=%d b=%.2f' % (self.k, self.b)


class Cosine(ScoringFunction):
    """
    See lecture notes for definition of Cosine similarity.  Be sure to use the
    precomputed document norms (in index), rather than recomputing them for
    each query.

    >>> idx = index.Index(['a a b c', 'c d e', 'c e f'])
    >>> cos = Cosine()
    >>> cos.score({'a': 1.}, idx)[1]  # doctest:+ELLIPSIS
    0.792857...
    """
    def score(self, query_vector, index):
        
        scores = defaultdict(lambda: 0)
        for qry_term, qry_weight in query_vector.items():
            if qry_term in index.index:
                for doc_id, doc_weight in index.index[qry_term]:
                    scores[doc_id] += ( qry_weight * ((1 + math.log10(doc_weight)) * idf(qry_term, index) ))
        
        for doc_id in scores:
            scores[doc_id] /= float(index.doc_norms[doc_id])
        
        return scores

    def __repr__(self):
        return 'Cosine'
    
