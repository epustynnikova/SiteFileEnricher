import asyncio
import csv
import os

from site_file_enricher.io.file_handler import FileFormat, get_handler
from site_file_enricher.io.site_handler import download_xml_and_parse
from site_file_enricher.file_parser.xml_parser import XMLParser, RootXMLElement, XMLElement
from site_file_enricher.search.fuzzy import search


def enrich_file(abs_path_to_file: str, xml_parser: XMLParser, cert_abs_path: str):
    file_handler = get_handler(
        FileFormat.XLSX,
        abs_path_to_file,
        '',
        xml_parser.col_names
    )

    link_to_input_elements = file_handler.read()

    new_elements = []

    for link in link_to_input_elements:
        input_elements = link_to_input_elements[link]
        print(f'Download and parse xml for {link}')
        file_elements = asyncio.run(download_xml_and_parse(link, cert_abs_path, xml_parser))

        product_info_els = [file_el for file_el in file_elements if file_el.product_name != '']
        universal_col_datas = [file_el.col_data for file_el in file_elements if file_el.product_name == '']

        print(f'Fuzzy search for link: {link}')
        searched_output_elements = search(input_elements, product_info_els)
        for searched_output_element in searched_output_elements:
            searched_output_element.new_col_datas += universal_col_datas

        new_elements += searched_output_elements
        if len(new_elements) > 100:
            file_handler.write(new_elements, link)
            new_elements = []

    file_handler.write(new_elements, link)


def enrich_file_with_default_settings(abs_path_to_file: str, cert_abs_path: str):
    product_info_root_xml_element = RootXMLElement(
        name="product_info",
        field_name="productInfo",
        product_xml_element=XMLElement("product_name", "name"),
        price_xml_element=XMLElement('price', 'price'),
        okpd_xml_element=XMLElement('OKPDCode', 'OKPDCode'),
        ktru_xml_element=XMLElement('KTRUInfo_code', 'code', 'KTRUInfo'),
        children=[
            XMLElement('price', 'price'),
            XMLElement('indexNum', 'indexNum'),
            XMLElement('isDuplicated', 'isDuplicated'),
            XMLElement('OKPDCode', 'OKPDCode'),
            XMLElement('OKPDName', 'OKPDName'),
            XMLElement('trademark', 'trademark'),
            XMLElement('isMedicalProductInfo', 'isMedicalProductInfo'),
            XMLElement('medicalProductCode', 'medicalProductCode'),
            XMLElement('medicalProductName', 'medicalProductName'),
            XMLElement('certificateNameMedicalProduct', 'certificateNameMedicalProduct'),
            XMLElement('nationalCode', 'nationalCode', 'OKEIInfo'),
            XMLElement('OKEIInfo_name', 'name', 'OKEIInfo'),
            XMLElement('OKEIInfo_code', 'code', 'OKEIInfo'),
            XMLElement('countryCode', 'countryCode'),
            XMLElement('countryFullName', 'countryFullName'),
            XMLElement('VATCode', 'VATCode'),
            XMLElement('VATName', 'VATName'),
            XMLElement('KTRUInfo_name', 'name', 'KTRUInfo'),
            XMLElement('KTRUInfo_code', 'code', 'KTRUInfo')
        ]
    )
    default_xml_parser = XMLParser(
        root_xml_element=product_info_root_xml_element,
        additional_data=[
            XMLElement('quantityUndefined', 'quantityUndefined'),
            XMLElement('regNum', 'regNum', 'customerInfo'),
            XMLElement('consRegistryNum', 'consRegistryNum', 'customerInfo'),
            XMLElement('singularName', 'singularName', 'customerInfo'),
            XMLElement('contractorRegistryNum', 'contractorRegistryNum', 'participantInfo'),
            XMLElement('contractSubject', 'contractSubject', 'contractSubjectInfo'),
            XMLElement('contractSubjectInfo_sid', 'sid', 'contractSubjectInfo')
        ]
    )
    enrich_file(abs_path_to_file=abs_path_to_file, xml_parser=default_xml_parser, cert_abs_path=cert_abs_path)


if __name__ == "__main__":
    enrich_file_with_default_settings(
        abs_path_to_file=os.path.abspath('short_example.xlsx'),
        cert_abs_path=os.path.abspath('russiantrustedca/russiantrustedca.pem')
    )
# import os
# >>> from site_file_enricher.script import enrich_file_with_default_settings
# >>> cert_path = os.path.abspath('russiantrustedca/russiantrustedca.pem')
# >>> path = os.path.abspath('my_example.txt')
# >>> enrich_file_with_default_settings(path, cert_path)
