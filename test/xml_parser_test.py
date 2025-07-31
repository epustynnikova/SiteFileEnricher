import unittest

from site_file_enricher import XMLParser, RootXMLElement, XMLElement


class TestXmlParser(unittest.TestCase):
    def test_parse_xml(self):
        # given:
        root_xml_element = RootXMLElement(
            name="product_info",
            field_name="productInfo",
            product_xml_element=XMLElement("product_name", "name"),
            price_xml_element=XMLElement('price', 'price'),
            okpd_xml_element=XMLElement('OKPDCode', 'OKPDCode'),
            ktru_xml_element=XMLElement('KTRUInfo_code', 'code', 'KTRUInfo'),
            children=[
                XMLElement('trademark', 'trademark'),
                XMLElement('medicalProductCode', 'medicalProductCode')
            ]
        )
        parser = XMLParser(root_xml_element)

        # when:
        with open('sources/xml/test.xml', 'r') as file:
            result = parser.parse(file.read(), 'test')

        # then:
        print(result)
        self.assertEqual(69, len(result))
        for file_element in result:
            self.assertEqual('test', file_element.link)
            if file_element.col_data.name == 'trademark':
                self.assertEqual('ABBOTT', file_element.col_data.value)
            elif file_element.col_data.name == 'medicalProductCode':
                self.assertIsNotNone(file_element.col_data.value)

    def test_parse_ktru_xml(self):
        # given:
        product_info_root_xml_element = RootXMLElement(
            name="product_info",
            field_name="productInfo",
            product_xml_element=XMLElement("product_name", "name"),
            price_xml_element=XMLElement('price', 'price'),
            okpd_xml_element=XMLElement('OKPDCode', 'OKPDCode'),
            ktru_xml_element=XMLElement('KTRUInfo_code', 'code', 'KTRUInfo'),
            children=[
                XMLElement('price', 'price'),
                XMLElement('trademark', 'trademark'),
                XMLElement('KTRUInfo_name', 'name', 'KTRUInfo'),
                XMLElement('KTRUInfo_code', 'code', 'KTRUInfo')
            ]
        )
        parser = XMLParser(product_info_root_xml_element)

        # when:
        with open('sources/xml/ktru_problem.xml', 'r') as file:
            result = parser.parse(
                file.read(),
                'https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=2320300308025000015')

        # then:
        print(result)
        self.assertEqual(12, len(result))

    def test_parse_small_xml(self):
        # given:
        product_info_root_xml_element = RootXMLElement(
            name="product_info",
            field_name="productInfo",
            product_xml_element=XMLElement("product_name", "name"),
            price_xml_element=XMLElement('price', 'price'),
            okpd_xml_element=XMLElement('OKPDCode', 'OKPDCode'),
            ktru_xml_element=XMLElement('KTRUInfo_code', 'code', 'KTRUInfo'),
            children=[
                XMLElement('price', 'price'),
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
        parser = XMLParser(
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

        # when:
        with open('sources/xml/el_contract_small.xml', 'r') as file:
            result = parser.parse(file.read(), 'test')

        # then:
        print(result)

    def test_parse_duplicated_name_xml(self):
        # given:
        product_info_root_xml_element = RootXMLElement(
            name="product_info",
            field_name="productInfo",
            product_xml_element=XMLElement("product_name", "name"),
            price_xml_element=XMLElement('price', 'price'),
            okpd_xml_element=XMLElement('OKPDCode', 'OKPDCode'),
            ktru_xml_element=XMLElement('KTRUInfo_code', 'code', 'KTRUInfo'),
            children=[XMLElement('trademark', 'trademark')]
        )
        parser = XMLParser(
            root_xml_element=product_info_root_xml_element,
            additional_data=[]
        )

        # when:
        with open('sources/xml/duplicated_name.xml', 'r') as file:
            result = parser.parse(
                file.read(),
                'https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=1772801635124000615'
            )

        # then:
        print(result)

    def test_ligand(self):
        # given:
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
        parser = XMLParser(
            root_xml_element=product_info_root_xml_element,
            additional_data=[]
        )

        # when:
        with open('sources/xml/ligand.xml', 'r') as file:
            result = parser.parse(
                file.read(),
                'https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=1772801635124000615'
            )

        # then:
        print(result)


if __name__ == '__main__':
    unittest.main()
