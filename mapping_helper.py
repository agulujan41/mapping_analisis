import csv
import const
import json
from mappings_utils import create_enum


class MappingDetails():
    def __init__(self, mapping_file_name, company_file_name):
        self.result_no_match = None
        self.car_list_mount = None
        self.car_list_no_match_mount = None
        self.rating_match_mount = None
        self.base_catalog = None
        self.company_base_catalog_car_list = None
        self.company_car_list = None
        self.company_matched_catalog_car_list = None
        self.company_no_matched_catalog_car_list = None
        self.company_car_list = None

        self.mapping_file_name = mapping_file_name
        self.company_file_name = company_file_name

        self.general_base = self._base_general_result()
        self.general_company = self._company_general_result()
        self.general = self._general_result()
        self.no_matched_brand_list_result = self._get_no_matched_brand_list()

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
        HEADER_LIST = create_enum('HEADER_LIST', csv_header_list)
        base_catalog = {}

        for row in csv_content:
            brand = row[HEADER_LIST.base_brand.value]
            if brand not in base_catalog:
                new_brand = {
                    'matched': True,
                    'model_catalog': {}
                }
                base_catalog[brand] = new_brand
            model = row[HEADER_LIST.base_model.value]
            if model not in base_catalog[brand]['model_catalog']:
                new_model = {
                    'matched': False,
                    'version_list': [],
                }
                base_catalog[brand]['model_catalog'][model] = new_model
            version = row[HEADER_LIST.base_version.value]
            base_catalog[brand][
                'model_catalog'][
                    model]['version_list'].append(version)
        return base_catalog

    def _get_base_detail_list(self, csv_header_list, csv_content):
        result_no_match = {}
        HEADER_LIST = create_enum('HEADER_LIST', csv_header_list)
        car_list_mount = 0
        car_list_no_match_mount = 0
        rating_match_mount = 0
        company_base_catalog_car_list = []
        for row in csv_content:
            brand_is_matched = True
            model_is_matched = True
            if not row[HEADER_LIST.base_brand.value] in result_no_match:
                result_no_match[row[HEADER_LIST.base_brand.value]] = {
                    'absolute_no_match': 0,
                    'model_no_match': 0,
                    'car_list_model': 0
                }
            if row[HEADER_LIST.company_brand.value] == const.NO_MATCH:
                result_no_match[
                    row[
                        HEADER_LIST.base_brand.value]][
                            'absolute_no_match'] += 1
                brand_is_matched = False

            if row[HEADER_LIST.company_model.value] == const.NO_MATCH:
                result_no_match[
                    row[
                        HEADER_LIST.base_brand.value]]['model_no_match'] += 1
                model_is_matched = False

            base_brand = row[HEADER_LIST.base_brand.value]
            base_model = row[HEADER_LIST.base_model.value]
            current_car = self.base_catalog[
                base_brand]['model_catalog'][base_model]
            if brand_is_matched and not model_is_matched and \
                    not current_car['matched']:
                current_car['matched'] = False
            if brand_is_matched and model_is_matched:
                current_car['matched'] = True

            if int(row[HEADER_LIST.match_rating.value]) > 0:
                rating_match_mount += 1
            else:
                car_list_no_match_mount += 1
            company_car_id = row[HEADER_LIST.company_car_id.value]
            company_base_catalog_car_list.append(company_car_id)
            result_no_match[
                row[
                    HEADER_LIST.base_brand.value]]['car_list_model'] += 1

            car_list_mount += 1

            self.result_no_match = result_no_match
            self.car_list_mount = car_list_mount
            self.car_list_no_match_mount = car_list_no_match_mount
            self.rating_match_mount = rating_match_mount
            self.company_base_catalog_car_list = company_base_catalog_car_list

    def _base_general_result(self):
        csv_header_list, csv_content = self._read_csv(
            self.mapping_file_name
        )
        self.base_catalog = self._get_base_catalog(
            csv_header_list, csv_content
        )
        self._get_base_detail_list(
            csv_header_list, csv_content
        )

        base = {}
        mounts = {}
        base['mounts'] = mounts
        mounts['car_list_total'] = self.car_list_mount
        mounts[
            'car_list_model_match_total'
            ] = self.car_list_mount - self.car_list_no_match_mount
        mounts['car_list_model_no_match_total'] = self.car_list_no_match_mount
        matches_model_total_base_percent = round(
            (100-(self.car_list_no_match_mount/self.car_list_mount)*100), 1)
        mounts[
            'matches_model_total_base_percent'
            ] = f'{matches_model_total_base_percent} %'

        rating = {}
        base['rating'] = rating
        rating['rating_match_total'] = self.rating_match_mount
        r_no_match_total = self.car_list_mount - self.rating_match_mount
        rating['rating_no_match_total'] = r_no_match_total
        rating[
            'rating_math_total_base_percent'
            ] = f'{round(100-(r_no_match_total/self.car_list_mount)*100, 1)} %'

        return base

    def _get_company_detail_list(self, csv_header_list, csv_content):
        HEADER_LIST = create_enum('HEADER_LIST', csv_header_list)
        company_matched_catalog_car_list = []
        company_no_matched_catalog_car_list = []
        company_car_list = []
        for row in csv_content:
            company_car_id = row[HEADER_LIST.CVE.value]
            if company_car_id in self.company_base_catalog_car_list:
                company_matched_catalog_car_list.append(
                    company_car_id
                )
            else:
                company_no_matched_catalog_car_list.append(
                    company_car_id
                )
            company_car_list.append(company_car_id)

        self.company_matched_catalog_car_list = (
            company_matched_catalog_car_list
        )
        self.company_no_matched_catalog_car_list = (
            company_no_matched_catalog_car_list
        )
        self.company_car_list = company_car_list

    def _company_general_result(self):
        csv_header_list, csv_content = self._read_csv(
            self.company_file_name
        )
        self._get_company_detail_list(
            csv_header_list, csv_content
        )
        company = {}
        company['company_car_list_amount'] = len(
            self.company_car_list
        )
        company['company_matched_car_list_amount'] = len(
            self.company_matched_catalog_car_list
        )
        company['company_no_matched_car_list_amount'] = len(
            self.company_no_matched_catalog_car_list
        )
        return company

    def _general_result(self):
        general = {}
        general['base'] = self.general_base_result()
        general['company'] = self.general_company_result()
        return general

    def _get_model_list(self, brand):
        model_list = []
        for model in self.base_catalog[brand]['model_catalog'].keys():
            model_list.append(model)
        return model_list

    def _get_no_matched_brand_list(self):
        result = {}
        result['result'] = self.result_no_match

        no_matched_brand_list = []
        result['no_matched_brand'] = no_matched_brand_list
        for brand, info in self.result_no_match.items():
            if info['absolute_no_match'] == \
                    info['car_list_model'] == info['model_no_match']:
                info['matched'] = False
                model_list = self._get_model_list(brand)
                self.base_catalog[brand]['matched'] = False
                no_matched_brand_list.append({
                    'brand': brand,
                    'car_mount': info['car_list_model'],
                    'model_list': model_list
                })
            else:
                info['matched'] = True
        return result

    def _get_top_no_matches_brand(self, file_name):
        data = self._read_json(file_name)
        no_matched_brand_list = [
            item["brand"] for item in data["no_matched_brand"]]

        result = data["result"]
        filtered_result = {
            k: v[
                "model_no_match"
                ]for k, v in result.items() if k not in no_matched_brand_list}
        sorted_result = sorted(
            filtered_result.items(), key=lambda x: x[1], reverse=True)

        top_10_keys = [k for k, v in sorted_result]
        return top_10_keys, data

    def _get_ranking_no_matched(self, file_name):
        top_ranking_list, data = self._get_top_no_matches_brand(file_name)

        result = {}
        ranking = {}
        result['no_matched_model_ranking'] = ranking
        result['ranking_brand_list'] = top_ranking_list
        for brand in top_ranking_list:
            ranking[brand] = data['result'][brand]

        return result

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

    def general_base_result(self):
        return self.general_base

    def general_company_result(self):
        return self.general_company

    def general_result(self):
        return self.general

    def no_matched_result(self):
        return self.no_matched_brand_list_result

    def get_ranking_brand_no_model_matched(self, file_name):
        return self._get_top_no_matches_brand(file_name)[0]

    def get_ranking_no_matched_result(self, file_name):
        return self._get_ranking_no_matched(file_name)

    def get_base_catalog(self):
        return self.base_catalog

    def get_no_matched_model_list(self):
        return self._get_no_matched_model_list()
