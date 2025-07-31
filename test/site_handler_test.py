import asyncio
import os
import unittest
import warnings

from site_file_enricher.file_parser.xml_parser import XMLParser, RootXMLElement, XMLElement
from site_file_enricher.file_parser.html_parser import HTMLParser, HTMLElement, HTMLContractFormat, RootTHMLElement
from site_file_enricher.io.site_handler import SiteHandler

warnings.filterwarnings('ignore')


class TestSiteHandler(unittest.TestCase):
    def test_download_xml(self):
        # given:
        warnings.filterwarnings('ignore')
        root_xml_element = RootXMLElement(
            name="product_info",
            field_name="productInfo",
            product_xml_element=XMLElement("product_name", "name"),
            price_xml_element=XMLElement('price', 'price'),
            okpd_xml_element=XMLElement('OKPDCode', 'OKPDCode'),
            ktru_xml_element=XMLElement('KTRUInfo_code', 'code', 'KTRUInfo'),
            children=[XMLElement('trademark', 'trademark')]
        )
        site_handler = SiteHandler(xml_parser=XMLParser(root_xml_element), html_parser=None)
        link = 'https://zakupki.gov.ru/epz/contract/contractCard/document-info.html?reestrNumber=2616410011824000637'

        # when:
        result = asyncio.run(site_handler.download_xml_and_parse(
            contact_link=link,
            cert_abs_path=os.path.abspath('sources/russiantrustedca/russiantrustedca.pem')
        ))

        # then:
        self.assertEqual(43, len(result))
        for file_element in result:
            self.assertEqual(link, file_element.link)
            self.assertEqual('trademark', file_element.col_data.name)
            self.assertEqual('ABBOTT', file_element.col_data.value)

    def test_download_html(self):
        # given:
        warnings.filterwarnings('ignore')
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
                HTMLElement(name="html_characteristics", row_index=2, column_index=0),
            ],
            row_step=3
        )
        htmp_parser = HTMLParser(type_a_root_element, type_b_root_element)
        site_handler = SiteHandler(xml_parser=None, html_parser=htmp_parser)
        link = 'https://zakupki.gov.ru/epz/contract/contractCard/document-info.html?reestrNumber=2616410011824000637'

        # when:
        result = asyncio.run(site_handler.download_xml_and_parse(
            contact_link=link,
            cert_abs_path=os.path.abspath('sources/russiantrustedca/russiantrustedca.pem')
        ))

        # then:
        self.assertEqual(45, len(result))
        for file_element in result:
            self.assertEqual(link, file_element.link)
            self.assertEqual('html_characteristics', file_element.col_data.name)

    def test_example(self):
        warnings.filterwarnings('ignore')
        root_xml_element = RootXMLElement(
            name="product_info",
            field_name="productInfo",
            product_xml_element=XMLElement("product_name", "name"),
            price_xml_element=XMLElement('price', 'price'),
            okpd_xml_element=XMLElement('OKPDCode', 'OKPDCode'),
            ktru_xml_element=XMLElement('KTRUInfo_code', 'code', 'KTRUInfo'),
            children=[XMLElement('trademark', 'trademark')]
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
                HTMLElement(name="html_characteristics", row_index=2, column_index=0),
            ],
            row_step=3
        )
        htmp_parser = HTMLParser(type_a_root_element, type_b_root_element)
        site_handler = SiteHandler(xml_parser=XMLParser(root_xml_element), html_parser=htmp_parser)
        # link = 'https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=2772401520524001885'
        link = 'https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=1623401336625000004'

        # when:
        result =  asyncio.run(site_handler.download_xml_and_parse(
            contact_link=link,
            cert_abs_path=os.path.abspath('sources/russiantrustedca/russiantrustedca.pem')
        ))
        print(result)

    def test_get_contract_subject(self):
        # given:
        warnings.filterwarnings('ignore')
        site_handler = SiteHandler(xml_parser=None, html_parser=None)
        link = 'https://zakupki.gov.ru/epz/contractfz223/card/contract-info.html?id=20289734'

        # when:
        result = asyncio.run(site_handler.download_xml_and_parse(
            contact_link=link,
            cert_abs_path=os.path.abspath('sources/russiantrustedca/russiantrustedca.pem')
        ))

        # then:
        self.assertEqual(1, len(result))
        self.assertEqual('html_product_name', result[0].col_data.name)
        self.assertEqual('ЛОТ №12 < Медицинские изделия_12 >', result[0].col_data.value)


if __name__ == '__main__':
    unittest.main()
