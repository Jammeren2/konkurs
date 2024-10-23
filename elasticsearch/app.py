from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from elasticsearch import Elasticsearch

app = Flask(__name__)
api = Api(app, doc='/swagger', title='Elasticsearch Search API')
es = Elasticsearch('http://localhost:9200')

search_model = api.model('Search', {
    'query': fields.String(required=True, description='Search query')
})

@api.route('/search')
class Search(Resource):
    @api.expect(search_model)
    def post(self):
        data = request.json
        query = data.get('query')
        
        # Define the search query for Elasticsearch
        search_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title", "content"]  # Replace with your fields
                }
            }
        }
        result = es.search(index='your_index_name', body=search_query)
        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8085)
