from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/api/metadata/genome/<genome_uuid>/stats', methods=["GET"])
def get_statistics(genome_uuid):
	metadata_request = 'https://staging-2020.ensembl.org/api/metadata/genome/{}/stats'.format(genome_uuid)
	response_json = requests.get(metadata_request)
	response = app.response_class(response=response_json,
									status=response_json.status_code,
									mimetype='application/json')

	return response

@app.route('/api/graphql/variation', methods=["POST"])
def post_variation_data():
	metadata_request = 'https://staging-2020.ensembl.org/api/graphql/variation'
	payload = request.get_json()
	response_json = requests.post(metadata_request,json=payload)
	response = app.response_class(response=response_json,
									status=response_json.status_code,
									mimetype='application/json')

	return response

@app.route('/api/graphql/variation', methods=["GET"])
def get_variation_data():
	metadata_request = 'https://staging-2020.ensembl.org/api/graphql/variation'
	response_json = requests.get(metadata_request)
	response = app.response_class(response=response_json,
									status=response_json.status_code)

	return response

@app.route('/api/metadata/genome/<genome_uuid>/karyotype', methods=["GET"])
def get_karyotype(genome_uuid):
	metadata_request = 'https://staging-2020.ensembl.org/api/metadata/genome/{}/karyotype'.format(genome_uuid)
	response_json = requests.get(metadata_request)
	response = app.response_class(response=response_json,
									status=response_json.status_code,
									mimetype='application/json')

	return response

@app.route('/api/metadata/popular_species', methods=["GET"])
def get_popular_speces():
	metadata_request = 'https://staging-2020.ensembl.org/api/metadata/popular_species'
	response_json = requests.get(metadata_request)
	response = app.response_class(response=response_json,
									status=response_json.status_code,
									mimetype='application/json')

	return response

@app.route('/api/metadata/validate_region', methods=["GET"])
def get_validate_region():
	genome_id = request.args.get("genome_id")
	region = request.args.get("region")
	metadata_request = 'https://staging-2020.ensembl.org/api/metadata/validate_region?genome_id={}&region={}'.format(genome_id,region)
	response_json = requests.get(metadata_request)
	response = app.response_class(response=response_json,
									status=response_json.status_code,
									mimetype='application/json')
	return response

@app.route('/api/metadata/validate_location', methods=["GET"])
def get_validate_location():
	genome_id = request.args.get("genome_id")
	location = request.args.get("location")
	metadata_request = 'https://staging-2020.ensembl.org/api/metadata/validate_location?genome_id={}&location={}'.format(genome_id,location)
	response_json = requests.get(metadata_request)
	response = app.response_class(response=response_json,
									status=response_json.status_code,
									mimetype='application/json')
	return response

@app.route('/api/metadata/genome/<genome_uuid>/example_objects', methods=["GET"])
def get_example_objects(genome_uuid):
	metadata_request = 'https://staging-2020.ensembl.org/api/metadata/genome/{}/example_objects'.format(genome_uuid)
	response_json = requests.get(metadata_request)
	response = app.response_class(response=response_json,
									status=response_json.status_code,
									mimetype='application/json')

	return response

@app.route('/api/metadata/genome/<genome_uuid>/details', methods=["GET"])
def get_genome_details(genome_uuid):
	metadata_request = 'https://staging-2020.ensembl.org/api/metadata/genome/{}/details'.format(genome_uuid)
	response_json = requests.get(metadata_request)
	response = app.response_class(response=response_json,
									status=response_json.status_code,
									mimetype='application/json')

	return response

@app.route('/api/metadata/genome/<slug>/explain', methods=["GET"])
def explain_slug(slug):
	metadata_request = 'https://staging-2020.ensembl.org/api/metadata/genome/{}/explain'.format(slug)
	response_json = requests.get(metadata_request)
	response = app.response_class(response=response_json,
									status=response_json.status_code,
									mimetype='application/json')

	return response

if __name__ == "__main__":
    app.run(debug=True)
