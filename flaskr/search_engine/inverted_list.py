import json 

# ONLY ITERATES FORWARD (for now). You can call reset()
# Stores the indexes of postings for a certain doc_id.
# This is used to record the indexes at which a certain token shows up 
# in the document with the given doc_id.
class PostingList:
    def __init__(self, doc_id, postings=None):  # postings is a list of integer term indexes
        self.doc_id = doc_id
        self.postings = postings if postings else []

    def append(self, term_index):
        self.postings.append(term_index)

    # Serializes to a dict which can be JSON-ified
    def to_json(self):
        return { 'doc_id': self.doc_id, 'postings': self.postings }

    def __repr__(self):
        return str(self.postings)

# Deserializes a JSON-ified PostingList
def posting_list_from_json(json_dict):
    return PostingList(json_dict['doc_id'], postings=json_dict['postings'])

class InvertedList:
    def __init__(self, term, list=None):
        self.term = term
        self.list = list if list else []  # list of PostingLists
        self.num_docs = len(self.list)
        self.num_postings = sum([len(posting_list.postings) for posting_list in self.list])
        self.curr_index = 0

    def reset_pointer(self):
        self.curr_index = 0

    def add_posting(self, doc_id, term_index):
        # print ('{}: Adding posting at {} to doc {}'.format(self.term, term_index, doc_id))
        self.num_postings += 1
        if not self.list:
            self.list.append(PostingList(doc_id))
            self.list[0].append(term_index)
            self.num_docs = 1
            return
        if self.list[self.curr_index].doc_id == doc_id:
            self.list[self.curr_index].append(term_index)
        else:
            self.list.append(PostingList(doc_id))
            self.list[-1].append(term_index)
            self.curr_index += 1
            self.num_docs += 1

    def finished(self):
        return self.curr_index >= self.num_docs

    def curr_doc_id(self):
        return self.list[self.curr_index].doc_id if self.curr_index < self.num_docs else None

    # iterate forward through the list until reaching doc_id >= the given doc_id
    # returns whether the doc_id was found in the list
    def move_to(self, doc_id):
        while self.curr_index < self.num_docs and \
              self.list[self.curr_index].doc_id < doc_id:
            self.curr_index += 1
        return self.curr_index < self.num_docs and \
               self.list[self.curr_index].doc_id == doc_id

    # iterate through the list until the next doc_id
    def move_to_next(self):
        self.curr_index += 1
        return self.curr_index < self.num_docs

    def move_past(self, doc_id):
        while self.curr_index < self.num_docs and \
              self.list[self.curr_index].doc_id <= doc_id:
            self.curr_index += 1

    # get number of term occurrences in the current doc_id
    def get_term_freq(self):
        return len(self.list[self.curr_index].postings) if self.curr_index < self.num_docs else 0

    def __repr__(self):
        return '{}: curr_index {} / {}, curr_id {}' \
            .format(self.term, self.curr_index, self.num_docs - 1, self.list[self.curr_index].doc_id if self.curr_index < self.num_docs else None)

    # Serializes to a dict which can be JSON-ified
    def to_json(self):
        return { 'term': self.term,
                 'posting_list': [posting_list.to_json() for posting_list in self.list] }

def inverted_list_from_json(json_data):
    return InvertedList(term=json_data['term'], list=[posting_list_from_json(p_list) for p_list in json_data['posting_list']])
