""" Assignment 1

Here you will implement a search engine based on cosine similarity.

The documents are read from documents.txt.gz.

The index will store tf-idf values using the formulae from class.

The search method will sort documents by the cosine similarity between the
query and the document (normalized only by the document length, not the query
length, as in the examples in class).

The search method also supports a use_champion parameter, which will use a
champion list (with threshold 10) to perform the search.

"""
from collections import defaultdict
import codecs
import gzip
import math
import re

class Index(object):

    def __init__(self, filename=None, champion_threshold=10):
        """ DO NOT MODIFY.
        Create a new index by parsing the given file containing documents,
        one per line. You should not modify this. """
        if filename:  # filename may be None for testing purposes.
            self.documents = self.read_lines(filename)
            toked_docs = [self.tokenize(d) for d in self.documents]
            self.doc_freqs = self.count_doc_frequencies(toked_docs)
            self.index = self.create_tfidf_index(toked_docs, self.doc_freqs)
            self.doc_lengths = self.compute_doc_lengths(self.index)
            self.champion_index = self.create_champion_index(self.index, champion_threshold)

    def compute_doc_lengths(self, index):
        """
        Return a dict mapping doc_id to length, computed as sqrt(sum(w_i**2)),
        where w_i is the tf-idf weight for each term in the document.

        E.g., in the sample index below, document 0 has two terms 'a' (with
        tf-idf weight 3) and 'b' (with tf-idf weight 4). It's length is
        therefore 5 = sqrt(9 + 16).

        >>> lengths = Index().compute_doc_lengths({'a': [[0, 3],[1, 3]], 'b': [[0, 4],[1, 4]]})
        >>> lengths[1]
        5.0
        """
        
        res = defaultdict(lambda: 0)
        
        for key in list(index.keys()):
            for values in index[key]:
                res[values[0]] = float(res[values[0]] + values[1]**2 )
        
        for doc_id in list(res.keys()):
            res[doc_id] = float(math.sqrt(res[doc_id]))
        
        return res
    
    def create_champion_index(self, index, threshold=10):
        """
        Create an index mapping each term to its champion list, defined as the
        documents with the K highest tf-idf values for that term (the
        threshold parameter determines K).

        In the example below, the champion list for term 'a' contains
        documents 1 and 2; the champion list for term 'b' contains documents 0
        and 1.

        >>> champs = Index().create_champion_index({'a': [[0, 10], [1, 20], [2, 15]], 'b': [[0, 20], [1, 15], [2, 10]]}, 2)
        >>> champs['a']
        [[1, 20], [2, 15]]
        """
        res = defaultdict(list)
        for term in list(index.keys()):
            doc_list = []
            for item in index[term]:
                doc_list.append((item[0],item[1]))
            doc_list.sort(key = lambda tup: tup[1],reverse = True)
            doc_list = doc_list[:threshold]
            for items in doc_list:
                res[term].append([items[0],items[1]])
        
        return res

    def create_tfidf_index(self, docs, doc_freqs):
        """
        Create an index in which each postings list contains a list of
        [doc_id, tf-idf weight] pairs. For example:

        {'a': [[0, .5], [10, 0.2]],
         'b': [[5, .1]]}

        This entry means that the term 'a' appears in document 0 (with tf-idf
        weight .5) and in document 10 (with tf-idf weight 0.2). The term 'b'
        appears in document 5 (with tf-idf weight .1).

        Parameters:
        docs........list of lists, where each sublist contains the tokens for one document.
        doc_freqs...dict from term to document frequency (see count_doc_frequencies).

        Use math.log10 (log base 10).

        >>> index = Index().create_tfidf_index([['a', 'b', 'a'], ['a']], {'a': 2., 'b': 1., 'c': 1.})
        >>> sorted(index.keys())
        ['a', 'b']
        >>> index['a']
        [[0, 0.0], [1, 0.0]]
        >>> index['b']  # doctest:+ELLIPSIS
        [[0, 0.3010299956639812]]
        """
        
        res = defaultdict(list)
        for doc_id in range(len(docs)):
            term_count = defaultdict(lambda: 0)
            for token in docs[doc_id]:
                term_count[token] += 1
            for key in list(term_count.keys()):
                if key in term_count:
                    res[key].append([doc_id, ( ( 1 + math.log10( float((term_count[key])) ) ) * math.log10( ( float(len(docs)) / doc_freqs[key] ) ) )])
                    
        return res

    def count_doc_frequencies(self, docs):
        """ Return a dict mapping terms to document frequency.
        >>> res = Index().count_doc_frequencies([['a', 'b', 'a', 'z'], ['a', 'b', 'c'], ['a', 'z']])
        >>> res['a']
        3
        >>> res['b']
        2
        >>> res['c']
        1
        >>> res['z']
        2
        """
        
        doc_term_freq = defaultdict(lambda: {})
        for doc_id in range(len(docs)):
            for token in docs[doc_id]:       
                doc_term_freq[token][doc_id] = 1
                
        res = defaultdict(lambda: 0)
        for key in list(doc_term_freq.keys()):
            res[key] = len(list(doc_term_freq[key].keys())) 
            
        return res

    def query_to_vector(self, query_terms):
        """ Convert a list of query terms into a dict mapping term to inverse document frequency (IDF).
        Compute IDF of term T as N / log10(document frequency of T), where N is the total number of documents.
        You may need to use the instance variables of the Index object to compute this. Do not modify the method signature.

        If a query term is not in the index, simply omit it from the result.

        Parameters:
          query_terms....list of terms

        Returns:
          A dict from query term to IDF.
        """
        N = len(self.documents)
        qry_vector = defaultdict(lambda: 0)
        
        for term in query_terms:
            if term in self.index:
                freq = self.doc_freqs[term]
                qry_vector[term] =  float(math.log10( float(N) / freq ))
        
        return qry_vector

    def search_by_cosine(self, query_vector, index, doc_lengths):
        """
        Return a sorted list of doc_id, score pairs, where the score is the
        cosine similarity between the query_vector and the document. The
        document length should be used in the denominator, but not the query
        length (as discussed in class). You can use the built-in sorted method
        (rather than a priority queue) to sort the results.

        The parameters are:

        query_vector.....dict from term to weight from the query
        index............dict from term to list of doc_id, weight pairs
        doc_lengths......dict from doc_id to length (output of compute_doc_lengths)

        In the example below, the query is the term 'a' with weight
        1. Document 1 has cosine similarity of 2, while document 0 has
        similarity of 1.

        >>> Index().search_by_cosine({'a': 1}, {'a': [[0, 1], [1, 2]]}, {0: 1, 1: 1})
        [(1, 2.0), (0, 1.0)]
        """
        
        scores = defaultdict(lambda: 0)
        for qry_term, qry_weight in list(query_vector.items()):
            if qry_term in index:
                for doc_id, doc_weight in index[qry_term]:
                    scores[doc_id] += ( qry_weight * doc_weight )
        
        for doc_id in scores:
            scores[doc_id] /= float(doc_lengths[doc_id])
        
        return(sorted(list(scores.items()),key=lambda x:x[1], reverse = True))

    def search(self, query, use_champions=False):
        """ Return the document ids for documents matching the query. Assume that
        query is a single string, possible containing multiple words. Assume
        queries with multiple words are AND queries. The steps are to:

        1. Tokenize the query (calling self.tokenize)
        2. Convert the query into an idf vector (calling self.query_to_vector)
        3. Compute cosine similarity between query vector and each document (calling search_by_cosine).

        Parameters:

        query...........raw query string, possibly containing multiple terms (though boolean operators do not need to be supported)
        use_champions...If True, Step 4 above will use only the champion index to perform the search.
        """
        
        qry_terms = self.tokenize(query)
        qry_vector = self.query_to_vector(qry_terms)
        if use_champions == True:
            return self.search_by_cosine(qry_vector, self.champion_index, self.doc_lengths)
        else:
            return self.search_by_cosine(qry_vector, self.index, self.doc_lengths)

    def read_lines(self, filename):
        """ DO NOT MODIFY.
        Read a gzipped file to a list of strings.
        """
        return [l.strip() for l in gzip.open(filename, 'rt').readlines()]

    def tokenize(self, document):
        """ DO NOT MODIFY.
        Convert a string representing one document into a list of
        words. Retain hyphens and apostrophes inside words. Remove all other
        punctuation and convert to lowercase.

        >>> Index().tokenize("Hi there. What's going on? first-class")
        ['hi', 'there', "what's", 'going', 'on', 'first-class']
        """
        return [t.lower() for t in re.findall(r"\w+(?:[-']\w+)*", document)]


def main():
    """ DO NOT MODIFY.
    Main method. Constructs an Index object and runs a sample query. """
    indexer = Index('documents.txt.gz')
    for query in ['pop love song', 'chinese american','city']:
        print(('\n\nQUERY=%s' % query))
        print(('\n'.join(['%d\t%e' % (doc_id, score) for doc_id, score in indexer.search(query)[:10]])))
        print(('\n\nQUERY=%s Using Champion List' % query))
        print(('\n'.join(['%d\t%e' % (doc_id, score) for doc_id, score in indexer.search(query, True)[:10]])))

if __name__ == '__main__':
    main()
