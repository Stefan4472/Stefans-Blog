# run the queries and save the results to files
import json
from index import Index

index = Index()
index.index_html_file(r'C:\Users\Stefan\Github\Blog-Content\project-overview-c++-game\post.md', 'project-overview-c++-game')
index.index_html_file(r'C:\Users\Stefan\Github\Blog-Content\project-overview-spaceships\post.md', 'project-overview-spaceships')

queries = ['game']

# with open('ql.trecrun') as output_file:
for i in range(len(queries)):
    query = queries[i]
    results = index.search(query)
    print (results)
