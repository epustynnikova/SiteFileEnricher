import os
import shutil
import unittest
import pandas as pd

from site_file_enricher.model.dto import OutputElement, FileColData
from site_file_enricher.io.file_handler import XLXSFileHandler


class TestXLSXFileHandler(unittest.TestCase):
    def test_read(self):
        # given:
        path = 'sources/xlsx/short_example.xlsx'
        output_file_path = 'sources/xlsx'
        output_file_name = 'short_example.xlsx'
        handler = XLXSFileHandler(path, [], output_file_path, output_file_name)
        test_data = {
            0: 1,
            1: 1,
            2: 1,
            3: 49,
            4: 2,
            5: 1
        }

        # when:
        result = handler.read()

        # then:
        print(result)
        self.assertEqual(6, len(result))
        index = 0
        for key in result:
            elements = result[key]
            self.assertEqual(test_data[index], len(elements))
            index += 1

    def test_read_ktru(self):
        # given:
        path = 'sources/xlsx/testold.xlsx'
        output_file_path = 'sources/xlsx'
        output_file_name = 'testold.xlsx'
        handler = XLXSFileHandler(path, ['field_a'], output_file_path, output_file_name)

        # when:
        result = handler.read()

        # then:
        print(result[
                  'https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=2320300308025000015'])

    def test_write(self):
        # given:
        path = 'sources/xlsx/short_example.xlsx'
        output_file_path = 'sources/xlsx'
        output_file_name = 'short_example.xlsx'
        handler = XLXSFileHandler(path, ['field_a', 'field_b'], output_file_path, output_file_name)
        additional_elements = [
            OutputElement(0,
                          "https://zakupki.gov.ru/epz/contractfz223/card/contract-info.html?id=21013248",
                          [FileColData(1, 'field_a', 'a_1'), FileColData(2, 'field_b', 'b_1')]),
            OutputElement(1,
                          "https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=2760602879024000424",
                          [FileColData(1, 'field_a', 'a_2'), FileColData(2, 'field_b', 'b_2')]),
            OutputElement(2,
                          "https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=2760602879024000397",
                          [FileColData(1, 'field_a', 'a_2'), FileColData(2, 'field_b', 'b_2')]),
            OutputElement(52,
                          "https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=1781308525024000662",
                          [FileColData(1, 'field_a', 'a_52')]),
            OutputElement(53,
                          "https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=1781308525024000662",
                          [FileColData(1, 'field_b', 'a_53')]),
            OutputElement(54,
                          "'https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=2032311510424000040'",
                          [FileColData(1, 'field_a', 'a_54')])
        ]
        data = dict(
            [(add_el.index_in_input_file,
              dict([(cdt.name, cdt.value) for cdt in add_el.new_col_datas]))
             for add_el in additional_elements])
        result_path = os.path.join(output_file_path, '0_' + output_file_name)

        # when:
        handler.write(
            additional_elements[:1],
            link="https://zakupki.gov.ru/epz/contractfz223/card/contract-info.html?id=21013248"
        )
        handler.write(
            additional_elements[1:2],
            link="https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=2760602879024000424"
        )
        handler.write(
            additional_elements[2:3],
            link="https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=2760602879024000397"
        )
        handler.write(
            additional_elements[3:4],
            link="https://zakupki.gov.ru/epz/contractfz223/card/contract-info.html?id=20879249"
        )
        handler.write(
            additional_elements[4:],
            link="https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=1781308525024000662"
        )

        # then:
        result = pd.read_excel(result_path)
        for idx, row in result.iterrows():
            if idx in data:
                col_datas = data[idx]
                for col_name in col_datas:
                    self.assertEqual(row[col_name], col_datas[col_name])

        os.remove(result_path)


if __name__ == '__main__':
    unittest.main()
