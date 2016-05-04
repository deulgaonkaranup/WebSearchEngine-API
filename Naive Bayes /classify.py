"""
Assignment 3. Implement a Multinomial Naive Bayes classifier for spam filtering.

You'll only have to implement 3 methods below:

train: compute the word probabilities and class priors given a list of documents labeled as spam or ham.
classify: compute the predicted class label for a list of documents
evaluate: compute the accuracy of the predicted class labels.

"""

from collections import defaultdict
import glob
import math
import os

class Document(object):
    """ A Document. Do not modify.
    The instance variables are:

    filename....The path of the file for this document.
    label.......The true class label ('spam' or 'ham'), determined by whether the filename contains the string 'spmsg'
    tokens......A list of token strings.
    """

    def __init__(self, filename=None, label=None, tokens=None):
        """ Initialize a document either from a file, in which case the label
        comes from the file name, or from specified label and tokens, but not
        both.
        """
        if label: # specify from label/tokens, for testing.
            self.label = label
            self.tokens = tokens
        else: # specify from file.
            self.filename = filename
            self.label = 'spam' if 'spmsg' in filename else 'ham'
            self.tokenize()

    def tokenize(self):
        self.tokens = ' '.join(open(self.filename).readlines()).split()


class NaiveBayes(object):

    def get_word_probability(self, label, term):
        """
        Return Pr(term|label). This is only valid after .train has been called.

        Params:
          label: class label.
          term: the term
        Returns:
          A float representing the probability of this term for the specified class.

        >>> docs = [Document(label='spam', tokens=['a', 'b']), Document(label='spam', tokens=['b', 'c']), Document(label='ham', tokens=['c', 'd'])]
        >>> nb = NaiveBayes()
        >>> nb.train(docs)
        >>> nb.get_word_probability('spam', 'a')
        0.25
        >>> nb.get_word_probability('spam', 'b')
        0.375
        """
        if term not in self.vocabulary:
            return 1.0 / (self.ctok_cnts[label] + len(self.vocabulary))
        
        return self.label_prob[label][term]  

    def get_top_words(self, label, n):
        """ Return the top n words for the specified class, using the odds ratio.
        The score for term t in class c is: p(t|c) / p(t|c'), where c'!=c.

        Params:
          labels...Class label.
          n........Number of values to return.
        Returns:
          A list of (float, string) tuples, where each float is the odds ratio
          defined above, and the string is the corresponding term.  This list
          should be sorted in descending order of odds ratio.

        >>> docs = [Document(label='spam', tokens=['a', 'b']), Document(label='spam', tokens=['b', 'c']), Document(label='ham', tokens=['c', 'd'])]
        >>> nb = NaiveBayes()
        >>> nb.train(docs)
        >>> nb.get_top_words('spam', 2)
        [(2.25, 'b'), (1.5, 'a')]
        """
        opp_label = 'spam'
        if label == 'spam':
            opp_label = 'ham'
            
        result = []
        for key in self.label_prob[label].keys():
            value = ( ( self.label_prob[label][key] * 1.0 ) / self.label_prob[opp_label][key] )
            result.append((value,key)) 
        
        result = sorted(result,key= lambda x:x[0],reverse=True)[:n]
        return result
        
    def train(self, documents):
        """
        Given a list of labeled Document objects, compute the class priors and
        word conditional probabilities, following Figure 13.2 of your
        book. Store these as instance variables, to be used by the classify
        method subsequently.
        Params:
          documents...A list of training Documents.
        Returns:
          Nothing.
        """
        self.prob_spam = 0.0
        self.vocabulary = defaultdict(lambda: 1)
        dict = defaultdict(lambda: defaultdict(lambda: 0))
        self.ctok_cnts = defaultdict(lambda: 0)
        
        for doc in documents:
            if doc.label == 'spam':
                self.prob_spam = self.prob_spam + 1
            for token in doc.tokens:
                self.vocabulary[token]
                dict[doc.label][token] = dict[doc.label][token] + 1
                self.ctok_cnts[doc.label] = self.ctok_cnts[doc.label] + 1 
                
        self.label_prob = defaultdict(lambda: defaultdict(lambda: 0))
        
        for label in dict.keys():
            for token in dict[label].keys():
                self.label_prob[label][token] = ( ( dict[label][token] + 1 ) * 1.0 ) / ( self.ctok_cnts[label] + len(self.vocabulary) )

        for key in self.vocabulary.keys():
            if key not in dict['spam']:
                self.label_prob['spam'][key] = ( 1 * 1.0 )  / ( self.ctok_cnts['spam'] + len(self.vocabulary) )
            if key not in dict['ham']:
                 self.label_prob['ham'][key] = ( 1 * 1.0 )  / ( self.ctok_cnts['ham'] + len(self.vocabulary) )
        
        self.prob_spam = self.prob_spam * 1.0 / len(documents)
        
    def classify(self, documents):
        """ Return a list of strings, either 'spam' or 'ham', for each document.
        Params:
          documents....A list of Document objects to be classified.
        Returns:
          A list of label strings corresponding to the predictions for each document.
        """
        res = []
        for doc in documents:
            p_spam = 0.0
            p_ham = 0.0
            for token in doc.tokens:
                if token in self.vocabulary:
                    p_spam = p_spam + (math.log10(1.0*self.label_prob['spam'][token]))
                    p_ham = p_ham + (math.log10(1.0*self.label_prob['ham'][token]))
                        
            p_spam = p_spam + (math.log10(1.0*self.prob_spam)) * 1.0
            p_ham = p_ham + (math.log10(1.0*(1 - self.prob_spam))) * 1.0
            
            if p_spam > p_ham:
                res.append('spam')
            else:
                res.append('ham')
                
        return res
    
def evaluate(predictions, documents):
    """ Evaluate the accuracy of a set of predictions.
    Return a tuple of three values (X, Y, Z) where
    X = percent of documents classified correctly
    Y = number of ham documents incorrectly classified as spam
    X = number of spam documents incorrectly classified as ham

    Params:
      predictions....list of document labels predicted by a classifier.
      documents......list of Document objects, with known labels.
    Returns:
      Tuple of three floats, defined above.
    """
    no_of_inc_ham = 0
    no_of_inc_spam = 0
    no_of_correct = 0
    for (pred,act) in zip(predictions,documents):
        if pred != act.label:
            if act.label == 'ham':
                no_of_inc_ham = no_of_inc_ham + 1
            else:
                no_of_inc_spam = no_of_inc_spam + 1
        else:
            no_of_correct = no_of_correct + 1
    
    accuracy = ( no_of_correct * 1.0 ) / len(documents)
    
    return (accuracy,no_of_inc_ham,no_of_inc_spam)
    
def main():
    """ Do not modify. """
    if not os.path.exists('train'):  # download data
       from urllib.request import urlretrieve
       import tarfile
       urlretrieve('http://cs.iit.edu/~culotta/cs429/lingspam.tgz', 'lingspam.tgz')
       tar = tarfile.open('lingspam.tgz')
       tar.extractall()
       tar.close()
    train_docs = [Document(filename=f) for f in glob.glob("train/*.txt")]
    print('read', len(train_docs), 'training documents.')
    nb = NaiveBayes()
    nb.train(train_docs)
    test_docs = [Document(filename=f) for f in glob.glob("test/*.txt")]
    print('read', len(test_docs), 'testing documents.')
    predictions = nb.classify(test_docs)
    results = evaluate(predictions, test_docs)
    print('accuracy=%.3f, %d false spam, %d missed spam' % (results[0], results[1], results[2]))
    print('top ham terms: %s' % ' '.join('%.2f/%s' % (v,t) for v, t in nb.get_top_words('ham', 10)))
    print('top spam terms: %s' % ' '.join('%.2f/%s' % (v,t) for v, t in nb.get_top_words('spam', 10)))

if __name__ == '__main__':
    main()
