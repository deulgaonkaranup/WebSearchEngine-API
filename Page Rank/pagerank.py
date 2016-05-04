""" Assignment 6: PageRank. """
from bs4 import BeautifulSoup
from sortedcontainers import SortedList, SortedSet, SortedDict
from collections import Counter
from collections import defaultdict
import glob
import os

def compute_pagerank(urls, inlinks, outlinks, b=.85, iters=20):
    """ Return a dictionary mapping each url to its PageRank.
    The formula is R(u) = (1/N)(1-b) + b * (sum_{w in B_u} R(w) / (|F_w|)

    Initialize all scores to 1.0.

    Params:
      urls.......SortedList of urls (names)
      inlinks....SortedDict mapping url to list of in links (backlinks)
      outlinks...Sorteddict mapping url to list of outlinks
    Returns:
      A SortedDict mapping url to its final PageRank value (float)

    >>> urls = SortedList(['a', 'b', 'c'])
    >>> inlinks = SortedDict({'a': ['c'], 'b': set(['a']), 'c': set(['a', 'b'])})
    >>> outlinks = SortedDict({'a': ['b', 'c'], 'b': set(['c']), 'c': set(['a'])})
    >>> sorted(compute_pagerank(urls, inlinks, outlinks, b=.5, iters=0).items())
    [('a', 1.0), ('b', 1.0), ('c', 1.0)]
    >>> iter1 = compute_pagerank(urls, inlinks, outlinks, b=.5, iters=1)
    >>> iter1['a']  # doctest:+ELLIPSIS
    0.6666...
    >>> iter1['b']  # doctest:+ELLIPSIS
    0.333...
    """
    
    R_w = defaultdict(lambda: 1.0)
    for u in urls:
        R_w[u] = 1.0
    
    for i in range(iters):
        for u in urls:
            sum_ = 0.0
            for w in inlinks[u]:
                sum_ += ( 1.0 * R_w[w] ) / (len(outlinks[w]))
            R_w[u] = (( 1.0 - b ) / len(urls) ) + ( 1.0 * b * sum_)
            
    return R_w

def get_top_pageranks(inlinks, outlinks, b, n=50, iters=20):
    """
    >>> inlinks = SortedDict({'a': ['c'], 'b': set(['a']), 'c': set(['a', 'b'])})
    >>> outlinks = SortedDict({'a': ['b', 'c'], 'b': set(['c']), 'c': set(['a'])})
    >>> res = get_top_pageranks(inlinks, outlinks, b=.5, n=2, iters=1)
    >>> len(res)
    2
    >>> res[0]  # doctest:+ELLIPSIS
    ('a', 0.6666...
    """
    urls = SortedSet()
    
    for value in inlinks:
        urls.add(value)
    
    for value in outlinks:
        urls.add(value)
    
    Score = compute_pagerank(urls, inlinks, outlinks, b, iters)
    
    return sorted(Score.items(),key=lambda x:x[1],reverse=True)[:n]

def read_names(path):
    """ Do not mofify. Returns a SortedSet of names in the data directory. """
    return SortedSet([os.path.basename(n) for n in glob.glob(path + os.sep + '*')])

def myfilter(tag):
    """ Find <a> tags like [ <li><a href='/wiki/' ]that are inside of A-Z headings.
    """
    def tryparent(tag):
        try:
            return re.match('[A-Z]', tag.parent.parent.previous_sibling.previous_sibling.span.text)
        except:
            False
    return tag and tag.name == 'a' and tag.parent.name == 'li' and tag.get('href').startswith('/wiki/') and not tag.previous_sibling and tryparent(tag)

def get_links(names, html):
    """
    Return a SortedSet of computer scientist names that are linked from this
    html page. The return set is restricted to those people in the provided
    set of names.  The returned list should contain no duplicates.

    Params:
      names....A SortedSet of computer scientist names, one per filename.
      html.....A string representing one html page.
    Returns:
      A SortedSet of names of linked computer scientists on this html page, restricted to
      elements of the set of provided names.

    >>> get_links({'Gerald_Jay_Sussman'},
    ... '''<a href="/wiki/Gerald_Jay_Sussman">xx</a> and <a href="/wiki/Not_Me">xx</a>''')
    SortedSet(['Gerald_Jay_Sussman'], key=None, load=1000)
    """
    soup = BeautifulSoup(html,"html.parser")
    list = [l['href'] for l in soup.find_all('a') if l.get('href')]
    res = SortedSet()
    for l in list:
        if l.startswith('/wiki/'):
            tokens = l.split('/')
            if tokens[2] in names:
                res.add(tokens[2])
    
    return res

def read_links(path):
    """
    Read the html pages in the data folder. Create and return two SortedDicts:
      inlinks: maps from a name to a SortedSet of names that link to it.
      outlinks: maps from a name to a SortedSet of names that it links to.
    For example:
    inlinks['Ada_Lovelace'] = SortedSet(['Charles_Babbage', 'David_Gelernter'], key=None, load=1000)
    outlinks['Ada_Lovelace'] = SortedSet(['Alan_Turing', 'Charles_Babbage'], key=None, load=1000)

    You should use the read_names and get_links function above.

    Params:
      path...the name of the data directory ('data')
    Returns:
      A (inlinks, outlinks) tuple, as defined above (i.e., two SortedDicts)
    """
    outlinks = SortedDict()
    inlinks = SortedDict()
    
    names = read_names(path)
    path = os.path.join(os.getcwd(),path)
    
    for name in sorted(os.listdir(path=path)):
        inlinks[name] = SortedSet()
    
    for name in sorted(os.listdir(path=path)):
        html = open(os.path.join(path,name)).read()
        olinks = get_links(names, html)
        if name in olinks:
            olinks.remove(name)
            
        outlinks[name] = olinks
        for link in olinks:
            inlinks[link].add(name)
    
    return (inlinks,outlinks)
        
def print_top_pageranks(topn):
    """ Do not modify. Print a list of name/pagerank tuples. """
    print('Top page ranks:\n%s' % ('\n'.join('%s\t%.5f' % (u, v) for u, v in topn)))

def main():
    """ Do not modify. """
    if not os.path.exists('data'):  # download and unzip data
       from urllib.request import urlretrieve
       import tarfile
       urlretrieve('http://cs.iit.edu/~culotta/cs429/pagerank.tgz', 'pagerank.tgz')
       tar = tarfile.open('pagerank.tgz')
       tar.extractall()
       tar.close()

    inlinks, outlinks = read_links('data')
    print('read %d people with a total of %d inlinks' % (len(inlinks), sum(len(v) for v in inlinks.values())))
    print('read %d people with a total of %d outlinks' % (len(outlinks), sum(len(v) for v in outlinks.values())))
    topn = get_top_pageranks(inlinks, outlinks, b=.8, n=20, iters=10)
    print_top_pageranks(topn)

if __name__ == '__main__':
    main()
