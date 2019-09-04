# run the queries and save the results to files
import json
from index import Index, restore_index_from_file

index = Index()
index.index_html_file(r'C:\Users\Stefan\Github\Blog-Webcode\sample_post\post.md', 'sample-post')
index.index_html_file(r'C:\Users\Stefan\Github\Blog-Webcode\sample_post\post.md', 'sample-post-2')
index.index_html_file(r'C:\Users\Stefan\Github\Blog-Content\project-overview-c++-game\post.md', 'project-overview-c++-game')
index.index_html_file(r'C:\Users\Stefan\Github\Blog-Content\project-overview-spaceships\post.md', 'project-overview-spaceships')

# TODO: USE A RELATIVE PATH FROM THE DIRECTORY ROOT
index.save_to_file('instance/index.json', indent=2)
r_index = restore_index_from_file('instance/index.json')  # TODO: DOUBLE-CHECK RESTORATION SETS CORRECT VALUES
print ()
print (index.num_docs, r_index.num_docs)
print (index.num_terms, r_index.num_terms)

queries = ['game engine']

# with open('ql.trecrun') as output_file:
for i in range(len(queries)):
    query = queries[i]
    results = index.search(query)
    print()
    print (results)
    results2 = r_index.search(query)
    print (results2)
