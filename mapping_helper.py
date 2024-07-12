import csv
import const
import json
from mappings_utils import create_enum


class MappingDetails():
    def __init__(self, mapping_file_name, company_file_name):
        self.result_no_match = None
        self.cars_mount = None
        self.cars_no_match_mount = None
        self.rating_match_mount = None
        self.base_catalog = None
        self.company_base_catalog_cars = None
        self.company_cars = None
        self.company_matched_catalog_cars = None
        self.company_no_matched_catalog_cars = None
        self.company_cars = None

        self.mapping_file_name = mapping_file_name
        self.company_file_name = company_file_name

        self.general_base = self._base_general_results()
        self.general_company = self._company_general_results()
        self.general = self._general_results()
        self.no_matched_brands_results = self._get_no_matched_brands()

    def _read_csv(self, file_name):
        csv_file = None
        csv_header_list = None
        csv_content = None
        with open(file_name, 'r', newline='', encoding='utf-8') as csv_file:
            csv_file = csv.reader(csv_file)
            csv_file = list(csv_file)
            csv_header_list = csv_file[0]
            csv_content = csv_file[1:len(csv_file)]

        return csv_header_list, csv_content

    def _read_json(self, file_name):
        with open(file_name, 'r') as file:
            data = json.load(file)
        return data

    def _get_base_catalog(self, csv_header_list, csv_content):
        Headers = create_enum('Headers', csv_header_list)
        base_catalog = {}

        for row in csv_content:
            brand = row[Headers.base_brand.value]
            if brand not in base_catalog:
                new_brand = {
                    'matched': True,
                    'model_catalog': {}
                }
                base_catalog[brand] = new_brand
            model = row[Headers.base_model.value]
            if model not in base_catalog[brand]['model_catalog']:
                new_model = {
                    'matched': False,
                    'version_list': [],
                }
                base_catalog[brand]['model_catalog'][model] = new_model
            version = row[Headers.base_version.value]
            base_catalog[brand][
                'model_catalog'][
                    model]['version_list'].append(version)
        return base_catalog

    def _get_base_details(self, csv_header_list, csv_content):
        results_no_match = {}
        Headers = create_enum('Headers', csv_header_list)
        cars_mount = 0
        cars_no_match_mount = 0
        rating_match_mount = 0
        company_base_catalog_cars = []
        for row in csv_content:
            brand_is_matched = True
            model_is_matched = True
            if not row[Headers.base_brand.value] in results_no_match:
                results_no_match[row[Headers.base_brand.value]] = {
                    'absolute_no_match': 0,
                    'model_no_match': 0,
                    'cars_model': 0
                }
            if row[Headers.company_brand.value] == const.NO_MATCH:
                results_no_match[
                    row[
                        Headers.base_brand.value]]['absolute_no_match'] += 1
                brand_is_matched = False

            if row[Headers.company_model.value] == const.NO_MATCH:
                results_no_match[
                    row[
                        Headers.base_brand.value]]['model_no_match'] += 1
                model_is_matched = False

            base_brand = row[Headers.base_brand.value]
            base_model = row[Headers.base_model.value]
            current_car = self.base_catalog[
                base_brand]['model_catalog'][base_model]
            if brand_is_matched and not model_is_matched and \
                    not current_car['matched']:
                current_car['matched'] = False
            if brand_is_matched and model_is_matched:
                current_car['matched'] = True

            if int(row[Headers.match_rating.value]) > 0:
                rating_match_mount += 1
            else:
                cars_no_match_mount += 1
            company_car_id = row[Headers.company_car_id.value]
            company_base_catalog_cars.append(company_car_id)
            results_no_match[
                row[
                    Headers.base_brand.value]]['cars_model'] += 1

            cars_mount += 1

            self.results_no_match = results_no_match
            self.cars_mount = cars_mount
            self.cars_no_match_mount = cars_no_match_mount
            self.rating_match_mount = rating_match_mount
            self.company_base_catalog_cars = company_base_catalog_cars

    def _base_general_results(self):
        csv_header_list, csv_content = self._read_csv(
            self.mapping_file_name
        )
        self.base_catalog = self._get_base_catalog(
            csv_header_list, csv_content
        )
        self._get_base_details(
            csv_header_list, csv_content
        )

        base = {}
        mounts = {}
        base['mounts'] = mounts
        mounts['cars_total'] = self.cars_mount
        mounts[
            'cars_model_match_total'
            ] = self.cars_mount - self.cars_no_match_mount
        mounts['cars_model_no_match_total'] = self.cars_no_match_mount
        matches_model_total_base_percent = round(
            (100-(self.cars_no_match_mount/self.cars_mount)*100), 1)
        mounts[
            'matches_model_total_base_percent'
            ] = f'{matches_model_total_base_percent} %'

        rating = {}
        base['rating'] = rating
        rating['rating_match_total'] = self.rating_match_mount
        r_no_match_total = self.cars_mount - self.rating_match_mount
        rating['rating_no_match_total'] = r_no_match_total
        rating[
            'rating_math_total_base_percent'
            ] = f'{round(100-(r_no_match_total/self.cars_mount)*100, 1)} %'

        return base

    def _get_company_details(self, csv_header_list, csv_content):
        Headers = create_enum('Headers', csv_header_list)
        company_matched_catalog_cars = []
        company_no_matched_catalog_cars = []
        company_cars = []
        for row in csv_content:
            company_car_id = row[Headers.CVE.value]
            if company_car_id in self.company_base_catalog_cars:
                company_matched_catalog_cars.append(
                    company_car_id
                )
            else:
                company_no_matched_catalog_cars.append(
                    company_car_id
                )
            company_cars.append(company_car_id)

        self.company_matched_catalog_cars = company_matched_catalog_cars
        self.company_no_matched_catalog_cars = company_no_matched_catalog_cars
        self.company_cars = company_cars

    def _company_general_results(self):
        csv_header_list, csv_content = self._read_csv(
            self.company_file_name
        )
        self._get_company_details(
            csv_header_list, csv_content
        )
        company = {}
        company['company_cars_amount'] = len(
            self.company_cars
        )
        company['company_matched_cars_amount'] = len(
            self.company_matched_catalog_cars
        )
        company['company_no_matched_cars_amount'] = len(
            self.company_no_matched_catalog_cars
        )
        return company

    def _general_results(self):
        general = {}
        general['base'] = self.general_base_results()
        general['company'] = self.general_company_results()
        return general

    def _get_model_list(self, brand):
        model_list = []
        for model in self.base_catalog[brand]['model_catalog'].keys():
            model_list.append(model)
        return model_list

    def _get_no_matched_brands(self):
        results = {}
        results['results'] = self.results_no_match

        no_matched_brands = []
        results['no_matched_brand'] = no_matched_brands
        for brand, info in self.results_no_match.items():
            if info['absolute_no_match'] == \
                    info['cars_model'] == info['model_no_match']:
                info['matched'] = False
                model_list = self._get_model_list(brand)
                self.base_catalog[brand]['matched'] = False
                no_matched_brands.append({
                    'brand': brand,
                    'car_mount': info['cars_model'],
                    'model_list': model_list
                })
            else:
                info['matched'] = True
        return results

    def _get_top_no_matches_brand(self, file_name):
        data = self._read_json(file_name)
        no_matched_brands = [
            item["brand"] for item in data["no_matched_brand"]]

        results = data["results"]
        filtered_results = {
            k: v[
                "model_no_match"
                ]for k, v in results.items() if k not in no_matched_brands}
        sorted_results = sorted(
            filtered_results.items(), key=lambda x: x[1], reverse=True)

        top_10_keys = [k for k, v in sorted_results]
        return top_10_keys, data

    def _get_ranking_no_matched(self, file_name):
        top_ranking_list, data = self._get_top_no_matches_brand(file_name)

        results = {}
        ranking = {}
        results['no_matched_model_ranking'] = ranking
        results['ranking_brand_list'] = top_ranking_list
        for brand in top_ranking_list:
            ranking[brand] = data['results'][brand]

        return results

    def _get_no_matched_model_list(self):
        no_model_matched = {}
        for brand_name, brand_value in self.base_catalog.items():
            if brand_value['matched']:
                brand_info = {}
                no_model_matched[brand_name] = brand_info
                model_list = []
                brand_info['model_list'] = model_list
                for model, model_value in brand_value['model_catalog'].items():
                    if not model_value['matched']:
                        model_list.append(model)

        return no_model_matched

    def general_base_results(self):
        return self.general_base

    def general_company_results(self):
        return self.general_company

    def general_results(self):
        return self.general

    def no_matched_results(self):
        return self.no_matched_brands_results

    def get_ranking_brand_no_model_matched(self, file_name):
        return self._get_top_no_matches_brand(file_name)[0]

    def get_ranking_no_matched_results(self, file_name):
        return self._get_ranking_no_matched(file_name)

    def get_base_catalog(self):
        return self.base_catalog

    def get_no_matched_model_list(self):
        return self._get_no_matched_model_list()
