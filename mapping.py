import json
from mapping_helper import MappingDetails
from mapping_intelligence import run_intelligence


def csv_detail_writer(file_name, data):
    json_string = json.dumps(data, indent=4)

    with open(file_name, 'w') as json_file:
        json_file.write(json_string)


mapping_file_path = 'fixtures/mapping.csv'
company_file_path = 'fixtures/company_cars.csv'
mapping_object = MappingDetails(
    mapping_file_path, company_file_path
)

base_catalog_path = 'results/info/mapping_base_catalog.json'
base_catalog_data = mapping_object.get_base_catalog()
csv_detail_writer(
    base_catalog_path, base_catalog_data
)

general_result_path = 'results/development/mapping_general_results.json'
general_data = mapping_object.general_result()
csv_detail_writer(
    general_result_path, general_data
)

no_matched_path = 'results/info/mapping_no_matched_results.json'
no_matched_data = mapping_object.no_matched_result()
csv_detail_writer(
    no_matched_path, no_matched_data
)
no_matched_brand_path = 'results/development/mapping_no_matched_brand.json'
no_matched_brand_data = no_matched_data['no_matched_brand']
csv_detail_writer(
    no_matched_brand_path, no_matched_brand_data
)
ranking_path = 'results/info/mapping_ranking_no_matched_results.json'
ranking_no_matched_results = mapping_object.get_ranking_no_matched_result(
    no_matched_path
)
csv_detail_writer(
    ranking_path, ranking_no_matched_results
)

no_model_matched_path = 'results/development/mapping_no_matched_model.json'
no_model_matched_data = mapping_object.get_no_matched_model_list()
csv_detail_writer(
    no_model_matched_path, no_model_matched_data
)

python_output_file = "results/development/mapping_intelligence_output.py"
run_intelligence(
    no_matched_brand_path, no_model_matched_path, python_output_file
)
