from typing import Union

from fuzzywuzzy import fuzz, process

from site_file_enricher.model.dto import FileElement, InputElement, OutputElement


def filter_col_datas(file_el: FileElement, okpd_ktru: Union[str, None]) -> bool:
    if okpd_ktru is None:
        return True
    if file_el.okpd is None and file_el.ktru is None:
        return True
    return file_el.okpd == okpd_ktru or file_el.ktru == okpd_ktru


def search(input_elements: list[InputElement], file_elements: list[FileElement]) -> list[OutputElement]:
    output_elements = []
    price_to_name_to_file_elements = {}
    for file_element in file_elements:
        product_name = file_element.product_name
        price = file_element.price
        if price in price_to_name_to_file_elements:
            if product_name in price_to_name_to_file_elements[price]:
                price_to_name_to_file_elements[price][product_name].append(file_element)
            else:
                price_to_name_to_file_elements[price][product_name] = [file_element]
        else:
            price_to_name_to_file_elements[price] = {product_name: [file_element]}

    index = 0
    size = len(input_elements)
    for input_el in input_elements:
        print(f'Handle input element #{index + 1}/{size}')
        index += 1

        price = input_el.price

        if price in price_to_name_to_file_elements:
            fuzzy_result = process.extract(
                input_el.name,
                price_to_name_to_file_elements[price].keys(),
                limit=1)
            if len(fuzzy_result) > 0 and fuzzy_result[0][1] > 70:
                product_name = fuzzy_result[0][0]
                output_elements.append(OutputElement(
                    index_in_input_file=input_el.index_in_input_file,
                    link=input_el.link,
                    new_col_datas=[file_el.col_data for file_el in price_to_name_to_file_elements[price][product_name]
                                   if filter_col_datas(file_el, input_el.okpd_ktru)]
                ))
            # del price_to_name_to_file_elements[product_name]
    return output_elements
