# run the queries and save the results to files
import json
from index import Index

index = Index()
index.create_index('shakespeare-scenes.json')

queries = ['the king queen royalty',
           'servant guard soldier',
           'hope dream sleep',
           'ghost spirit',
           'fool jester player',
           'to be or not to be']

# with open('ql.trecrun') as output_file:
for score_func in ['bm25', 'ql']:
    with open('{}.trecrun'.format(score_func), 'w') as output:
        for i in range(len(queries)):
            query = queries[i]
            results = index.search(query, score_func=score_func)
            print (results)
            for j in range(len(results)):
                result = results[j]
                output.write('Q{} skip {} {} {} skussmaul-{}\n'.format( \
                    i + 1, result[0], j + 1, result[1], score_func))
