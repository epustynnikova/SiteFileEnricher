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
        handler = XLXSFileHandler(path, [])
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
        handler = XLXSFileHandler(path, ['field_a'])

        # when:
        result = handler.read()

        # then:
        print(result['https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=2320300308025000015'])

    def test_write(self):
        # given:
        path = 'sources/xlsx/short_example_1.xlsx'
        shutil.copy('sources/xlsx/short_example.xlsx', path)
        handler = XLXSFileHandler(path, ['field_a', 'field_b'], output_file_path=path)
        additional_elements = [
            OutputElement(1, "", [FileColData(1, 'field_a', 'a_1'), FileColData(2, 'field_b', 'b_1')]),
            OutputElement(2, "", [FileColData(1, 'field_a', 'a_2'), FileColData(2, 'field_b', 'b_2')]),
            OutputElement(52, "", [FileColData(1, 'field_a', 'a_52')]),
            OutputElement(53, "", [FileColData(1, 'field_a', 'a_53')]),
            OutputElement(54, "", [FileColData(1, 'field_b', 'a_54')])
        ]
        data = dict(
            [(add_el.index_in_input_file,
              dict([(cdt.name, cdt.value) for cdt in add_el.new_col_datas]))
             for add_el in additional_elements])

        # when:
        handler.write(additional_elements)

        # then:
        result = pd.read_excel(path)
        for idx, row in result.iterrows():
            if idx in data:
                col_datas = data[idx]
                for col_name in col_datas:
                    self.assertEqual(row[col_name], col_datas[col_name])

        os.remove(path)


if __name__ == '__main__':
    unittest.main()
