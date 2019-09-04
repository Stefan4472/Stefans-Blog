# run the queries and save the results to files
import json
from index import Index, restore_index_from_file

index = Index()
index.index_html_file(r'C:\Users\Stefan\Github\Blog-Content\project-overview-c++-game\post.md', 'project-overview-c++-game')
index.index_html_file(r'C:\Users\Stefan\Github\Blog-Content\project-overview-spaceships\post.md', 'project-overview-spaceships')
'''
queries = ['game engine']

# with open('ql.trecrun') as output_file:
for i in range(len(queries)):
    query = queries[i]
    results = index.search(query)
    print (results)
'''
# TODO: USE A RELATIVE PATH FROM THE DIRECTORY ROOT
index.save_to_file('instance/index.json')
r_index = restore_index_from_file('instance/index.json')  # TODO: DOUBLE-CHECK RESTORATION SETS CORRECT VALUES
print (index.num_docs, r_index.num_docs)
print (index.num_terms, r_index.num_terms)