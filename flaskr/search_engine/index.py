import json
import math
from queue import PriorityQueue
from collections import namedtuple
from inverted_list import InvertedList, inverted_list_from_json
import result as r
import query as q
import tokenizer as t

Result = namedtuple('result', 'doc_id score')

class Index:  # TODO: RENAME SEARCHENGINE?
    def __init__(self, index=None, doc_data=None):
        self.index = index if index else {}
        self.doc_data = doc_data if doc_data else {}
        self.num_docs = len(doc_data) if index else 0
        self.num_terms = len(index) if index else 0
        self.tokenizer = t.Tokenizer()  # TODO: USE STOPWORDS?

    def index_html_file(self, filepath, slug):  # TODO: WORK ON HTML FILES. RETRIEVE TEXT
        file_text = ''

        doc_id = self.num_docs + 1   # TODO: NEED TO RUN TOKENIZER
        position = 0
        for token in self.tokenizer.tokenize_file(filepath):
            if token not in self.index:
                self.index[token] = InvertedList(token)
            self.index[token].add_posting(doc_id, position)
            position += 1

        # update number of terms in the index and add entry to doc_data
        self.num_terms += position
        self.doc_data[doc_id] = \
            { 'slug': slug,
              'numTerms': position }

        self.num_docs += 1
        #print (self.index.keys())

    def search(self, query, score_func='ql'):
        # process the query so it can be understood
        processed_query = q.process_query(query, self.tokenizer)
        print ('Query terms: {}'.format(processed_query.terms))
        results = self._run_query(processed_query, score_func)
        return self._format_results(results, processed_query)

    def _run_query(self, processed_query, score_func):
        results = PriorityQueue()
        # retrieve the InvertedLists in the same order as the query terms
        inv_lists = {word: self.index[word] if word in self.index else InvertedList(word) for word in processed_query.terms}

        for list in inv_lists.values():
            list.reset_pointer()

        # iterate over all documents that contain at least one of the terms
        while True:
            has_next, doc_id = self.find_next_doc(inv_lists)
            if not has_next:
                break

            score = 0.0
            for term, list in inv_lists.items():
                if score_func == 'bm25':
                    qf = processed_query.term_counts[term]
                    f = list.get_term_freq() if list.curr_doc_id() == doc_id else 0
                    n = list.num_docs
                    N = self.num_docs
                    dl = self.doc_data[doc_id]['numTerms']
                    avdl = self.num_terms / self.num_docs
                    # print (qf, f, n, N, dl, avdl)
                    score += score_bm25(qf, f, n, N, dl, avdl)
                elif score_func == 'ql':
                    fqd = list.get_term_freq() if list.curr_doc_id() == doc_id else 0
                    dl = self.doc_data[doc_id]['numTerms']
                    cq = list.num_postings
                    C = self.num_terms
                    # print (fqd, dl, cq, C)
                    score += score_ql(fqd, dl, cq, C)

            # put result in list using negative score as priority
            # this way, higher score is prioritized
            results.put((-score, doc_id))

            # make sure all lists are moved to the next doc_id
            for list in inv_lists.values():
                list.move_to(doc_id + 1)

        return results

    # inv_lists: dict mapping term->InvertedList
    # searches the lists for the next doc_id with at least one of the terms
    # returns whether a term was found, and the doc_id
    def find_next_doc(self, inv_lists):
        in_progress = [list for list in inv_lists.values() if not list.finished()]
        if not in_progress:
            return False, -1
        next_doc_id = min([list.curr_doc_id() for list in in_progress])
        return True, next_doc_id

    # returns list of (scene_id, score) ordered decreasing
    def _format_results(self, results, processed_query):
        formatted_results = []
        while not results.empty():
            next = results.get()
            formatted_results.append((self.doc_data[next[1]]['slug'], -next[0]))
        return formatted_results

    def to_json(self):
        # TODO: SAVE STOPWORD FILE PATH?
        return {
            'index': [inverted_index.to_json() for inverted_index in self.index.values()],
            'doc_data': self.doc_data
        }

    def save_to_file(self, filepath, indent=0):
        if not filepath.endswith('.json'):
            raise ValueError('Must save to a .json file')

        with open(filepath, 'w') as outfile:
            json.dump(self.to_json(), outfile, indent=indent)

def index_from_json(json_data):
    index = {}
    doc_data = json_data['doc_data']
    serialized_inv_lists = json_data['index']

    # Iterate through the list of serialized InvertedLists.
    # Deserialize each one and add it to the index dict under its term.
    for serialized_inv_list in serialized_inv_lists:
        inv_list = inverted_list_from_json(serialized_inv_list)
        index[inv_list.term] = inv_list

    return Index(index=index, doc_data=doc_data)

def restore_index_from_file(filepath):
    json_data = {}
    with open(filepath, encoding='utf8') as json_file:
        json_data = json.load(json_file)
    return index_from_json(json_data)

# scores a single document for a single query term
# qf: frequency of the term in the query
# f: frequency of the term in the doc
# n: number of docs that contain the term
# N: number of docs in the collection
# dl: number of terms in the document
# avdl: average number of terms in a document
# k1, k2, b: parameters for the formula
def score_bm25(qf, f, n, N, dl, avdl, k1=1.2, k2=100, b=0.75):  # TODO: MOVE TO A DIFFERENT PLACE
    K = k1 * ((1 - b) + b * dl / avdl)
    return math.log10(1 / ((n + 0.5) / (N - n + 0.5))) * \
           (((k1 + 1) * f) / (K + f)) * \
           (((k2 + 1) * qf) / (k2 + qf))

# scores a single document for a single query term
# fqd: number of occurrences in the document
# dl: number of terms in the doc
# cq: number of times the term appears in the corpus
# C: total number of term occurrences in the corpus
def score_ql(fqd, dl, cq, C, mu=1500):
    print (fqd, dl, cq, C, mu)
    print ((fqd + mu * (cq / C)) / (dl + mu))
    # TODO: GUARD AGAINST CQ = 0, C = 0, DL = 0, FQD = 0
    return math.log10((fqd + mu * (cq / C)) / (dl + mu))
