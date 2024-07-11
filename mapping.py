import json
from mapping_helper import MappingDetails


def csv_details_writer(file_name, data):
    json_string = json.dumps(data, indent=4)

    with open(file_name, 'w') as json_file:
        json_file.write(json_string)


mapping_file_path = 'fixtures/mapping.csv'
company_file_path = 'fixtures/company_cars.csv'
mapping_object = MappingDetails(
    mapping_file_path, company_file_path
)

general_result_path = 'results/mapping_general_results.json'
general_data = mapping_object.general_results()
csv_details_writer(
    general_result_path, general_data
)

no_matched_path = 'results/mapping_no_matched_results.json'
no_matched_data = mapping_object.no_matched_results()
csv_details_writer(
    no_matched_path, no_matched_data
)
