from dataclasses import dataclass
from typing import Union

from bs4 import BeautifulSoup, Tag

from site_file_enricher.model.dto import FileColData, FileElement, FileElementType


@dataclass
class XMLElement:
    name: str
    field_name: str
    additional: str = None


@dataclass
class RootXMLElement:
    name: str
    field_name: str
    product_xml_element: XMLElement
    price_xml_element: XMLElement
    okpd_xml_element: XMLElement
    ktru_xml_element: XMLElement
    children: list[XMLElement]


def __get_value__(tag: Tag, xml_element: XMLElement) -> Union[str, None]:
    if tag is None:
        return None
    if xml_element.additional is not None:
        tag = tag.find(xml_element.additional)
        if tag is None:
            return None
    value = tag.find(xml_element.field_name)
    return value.text if value is not None else None


class XMLParser:
    def __init__(self, root_xml_element: RootXMLElement, additional_data: list[XMLElement] = []):
        self.additional_data = additional_data
        self.root_xml_element = root_xml_element
        self.col_names = [xml_el.name for xml_el in root_xml_element.children]
        for add_xml_el in additional_data:
            self.col_names.append(add_xml_el.name)

    def parse(self, file, link: str) -> list[FileElement]:
        file_elements = []
        bs_data = BeautifulSoup(file, "xml")

        for child in bs_data.find_all(self.root_xml_element.field_name):
            product_name = __get_value__(child, self.root_xml_element.product_xml_element)
            price_product = __get_value__(child, self.root_xml_element.price_xml_element)
            okpd = __get_value__(child, self.root_xml_element.okpd_xml_element)
            ktru = __get_value__(child, self.root_xml_element.ktru_xml_element)
            index_num = child.find('indexNum')
            if index_num is not None:
                index_num = int(index_num.text)
            else:
                index_num = -1
            if product_name is None:
                continue
            for xml_element_child in self.root_xml_element.children:
                xml_element_child_value = __get_value__(child, xml_element_child)
                if xml_element_child_value is None:
                    continue
                file_elements.append(
                    FileElement(
                        link=link,
                        product_name=product_name,
                        price=int(float(price_product) * 100),
                        okpd=okpd,
                        ktru=ktru,
                        file_element_type=FileElementType.XML,
                        col_data=FileColData(
                            index_num=index_num,
                            name=xml_element_child.name,
                            value=xml_element_child_value)
                    )
                )

        for additional_xml_element_child in self.additional_data:
            xml_element_child_value = __get_value__(bs_data, additional_xml_element_child)
            if xml_element_child_value is None:
                continue
            file_elements.append(
                FileElement(
                    link=link,
                    product_name='',
                    price=-1,
                    file_element_type=FileElementType.XML,
                    col_data=FileColData(
                        index_num=-1,
                        name=additional_xml_element_child.name,
                        value=xml_element_child_value)
                )
            )

        return file_elements
