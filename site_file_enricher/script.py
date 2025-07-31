import asyncio
import os

from site_file_enricher.io.file_handler import FileFormat, get_handler
from site_file_enricher.io.site_handler import SiteHandler
from site_file_enricher.file_parser.xml_parser import XMLParser, RootXMLElement, XMLElement
from site_file_enricher.search.fuzzy import search
from site_file_enricher.file_parser.html_parser import HTMLParser, HTMLElement, HTMLContractFormat, RootTHMLElement
from site_file_enricher.model.dto import FileElementType, OutputElement


def enrich_file(
        abs_path_to_file: str,
        out_path_to_file: str,
        out_file_name: str,
        site_handler: SiteHandler,
        cert_abs_path: str):
    file_handler = get_handler(
        FileFormat.XLSX,
        input_file=abs_path_to_file,
        output_file_path=out_path_to_file,
        output_file_name=out_file_name,
        col_names=site_handler.col_names,
        file_row_count=300
    )

    link_to_input_elements = file_handler.read()

    new_elements = []

    for link in link_to_input_elements:
        input_elements = link_to_input_elements[link]
        print(f'Download and parse xml/html for {link}')
        file_elements = asyncio.run(site_handler.download_xml_and_parse(link, cert_abs_path))

        xml_product_info_els = [file_el for file_el in file_elements
                                if file_el.product_name != '' and file_el.file_element_type == FileElementType.XML]
        html_product_info_els = [file_el for file_el in file_elements if
                                 file_el.product_name != '' and file_el.file_element_type == FileElementType.HTML]
        universal_col_datas = [file_el.col_data for file_el in file_elements if
                               file_el.product_name == '']

        print(f'Fuzzy search for link: {link}')
        searched_output_elements = search(input_elements, xml_product_info_els)
        for searched_output_element in searched_output_elements:
            searched_output_element.new_col_datas += universal_col_datas
        new_elements += searched_output_elements

        searched_output_elements = search(input_elements, html_product_info_els)
        for searched_output_element in searched_output_elements:
            searched_output_element.new_col_datas += universal_col_datas
        new_elements += searched_output_elements

        if len(xml_product_info_els) == len(html_product_info_els) == 0 and len(universal_col_datas) != 0:
            for input_el in input_elements:
                new_elements.append(OutputElement(
                    index_in_input_file=input_el.index_in_input_file,
                    link=input_el.link,
                    new_col_datas=universal_col_datas
                ))

        file_handler.write(new_elements, link=link)


def enrich_file_with_default_settings(
        abs_path_to_file: str,
        out_path: str,
        out_file_name: str,
        cert_abs_path: str):
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
    type_a_root_element = RootTHMLElement(
        contract_format=HTMLContractFormat.TYPE_A,
        product_html_element=HTMLElement(name="html_product_name", column_index=1),
        price_html_element=HTMLElement(name="html_price", column_index=6),
        children=[
            HTMLElement(name="html_product_name", column_index=1),
            HTMLElement(name="html_ktru", column_index=3),
            HTMLElement(name="html_characteristics", column_index=5),
        ]
    )
    type_b_root_element = RootTHMLElement(
        contract_format=HTMLContractFormat.TYPE_B,
        product_html_element=HTMLElement(name="html_product_name", column_index=1),
        price_html_element=HTMLElement(name="html_price", column_index=5),
        children=[
            HTMLElement(name="html_product_name", column_index=1),
            HTMLElement(name="html_ktru", column_index=3),
            HTMLElement(name="html_characteristics", row_index=2, column_index=0),
        ],
        row_step=3
    )
    default_htmp_parser = HTMLParser(type_a_root_element, type_b_root_element)
    site_handler = SiteHandler(xml_parser=default_xml_parser, html_parser=default_htmp_parser)
    enrich_file(
        abs_path_to_file=abs_path_to_file,
        out_path_to_file=out_path,
        out_file_name=out_file_name,
        site_handler=site_handler,
        cert_abs_path=cert_abs_path
    )


if __name__ == "__main__":
    try:
        enrich_file_with_default_settings(
        abs_path_to_file=os.path.abspath('10_apr_deleted500.xlsx'),
        cert_abs_path=os.path.abspath('russiantrustedca/russiantrustedca.pem'),
        out_path=os.path.dirname(os.path.abspath('result.xlsx')),
        out_file_name="enriched_10_apr_deleted500.xlsx"
        )
    except Exception as ex:
        print(ex)
# import os
# >>> from site_file_enricher.script import enrich_file_with_default_settings
# >>> cert_path = os.path.abspath('russiantrustedca/russiantrustedca.pem')
# >>> path = os.path.abspath('my_example.txt')
# >>> enrich_file_with_default_settings(path, cert_path)
