from dataclasses import dataclass
from enum import Enum

from site_file_enricher.model.dto import FileColData, FileElement, FileElementType
import bs4
import re


class HTMLContractFormat(Enum):
    TYPE_A = 1
    TYPE_B = 2


@dataclass
class HTMLElement:
    name: str
    column_index: int
    row_index: int = 0


@dataclass
class RootTHMLElement:
    contract_format: HTMLContractFormat
    product_html_element: HTMLElement
    price_html_element: HTMLElement
    children: list[HTMLElement]
    row_step: int = 1


def __get_value__(parsed_table: list[list], row_cnt: int, html_element: HTMLElement):
    try:
        updated_row_cnt = row_cnt + html_element.row_index
        if len(parsed_table) <= updated_row_cnt:
            return None
        row = parsed_table[updated_row_cnt]
        if len(row) <= html_element.column_index:
            return None
        else:
            return re.sub(r'([ \n]+)', ' ', row[html_element.column_index])
    except Exception as ex:
        print(ex)
        return None


class HTMLParser:
    def __init__(self, type_a_root_element: RootTHMLElement, type_b_root_element: RootTHMLElement):
        self.type_a_root_element = type_a_root_element
        self.type_b_root_element = type_b_root_element
        self.col_names = []
        if type_a_root_element is not None:
            self.col_names += [xml_el.name for xml_el in type_a_root_element.children]
        if type_b_root_element is not None:
            self.col_names += [xml_el.name for xml_el in type_b_root_element.children]

    def parse(self, html_content, link: str) -> list[FileElement]:
        bs_parser = bs4.BeautifulSoup(html_content, 'html.parser')
        parsed_table = []
        table_31 = bs_parser.find_all("table", {'class': 'printFormTbl table-centred-data'})[0]

        for i, row in enumerate(table_31.find_all('tr')):
            parsed_table.append([el.text.strip() for el in row.find_all('td')])

        root_element = self.__get_root_element__(parsed_table)
        if root_element is None:
            return []

        row_cnt = 2
        if parsed_table[0][0].isnumeric():
            row_cnt = 1
        file_elements = []

        while row_cnt < len(parsed_table):
            try:
                product_name = __get_value__(parsed_table, row_cnt, root_element.product_html_element)
                raw_price = __get_value__(parsed_table, row_cnt, root_element.price_html_element)
                if product_name is None or raw_price is None:
                    row_cnt += root_element.row_step
                    continue
                for child_element in root_element.children:
                    child_value = __get_value__(parsed_table, row_cnt, child_element)
                    if child_element is None:
                        continue
                    file_elements.append(FileElement(
                    link=link,
                    price= int(float(raw_price.replace(' ', ''))*100),
                    product_name=product_name,
                    file_element_type=FileElementType.HTML,
                    col_data=FileColData(row_cnt, child_element.name, child_value)
                    ))
                row_cnt += root_element.row_step
            except Exception as ex:
                print(ex)

        return file_elements


    def __get_root_element__(self, parsed_table: list) -> RootTHMLElement | None:
        if len(parsed_table) == 0:
            return None
        else:
            match len(parsed_table[0]):
                case 10:
                    return self.type_a_root_element
                case 9:
                    return self.type_b_root_element
                case _:
                    return None
