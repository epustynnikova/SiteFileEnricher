import csv
import os
import unittest
from site_file_enricher import OutputElement, FileColData
from site_file_enricher.io.file_handler import TSVFileHandler, FileFormat, get_handler
from test.test_utils import get_file_source_path

class TestTSVFileHandler(unittest.TestCase):
    def test_read(self):
        # given:
        file_path = get_file_source_path(os.path.join('in', 'test_in.tsv'))
        with open(file_path, mode='r') as in_f:
            handler = TSVFileHandler(in_f, None)
            test_data = {
                1: 1,
                2: 3,
                3: 3,
                4: 1,
                5: 1,
                6: 1,
                7: 45
            }

            # when:
            result = handler.read()

            # then:
            print(result[
                      'https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=1772801635124000615'])
            print(result[
                      'https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=2616410011824000637'])
            self.assertEqual(7, len(result))
            index = 1
            for key in result:
                elements = result[key]
                self.assertEqual(test_data[index], len(elements))
                index += 1

    def test_write(self):
        # given:
        in_file_path = get_file_source_path(os.path.join('out', 'test_in.tsv'))
        out_file_path = get_file_source_path(os.path.join('out', 'test_out.tsv'))
        with open(in_file_path, mode='r') as in_f:
            handler = TSVFileHandler(in_f, out_file_path)
            handler.read()

            # when:
            handler.write(
                [
                    OutputElement(1, "test", [FileColData(1, "field_a", "a"), FileColData(1, "field_b", "b")]),
                    OutputElement(2, "test_2", [FileColData(1, "field_c", "c"), FileColData(1, "field_b", "b")])
                ]
            )

        # then:
        with open(out_file_path, mode='r') as out_f:
            file = csv.reader(out_f, dialect='excel-tab')
            header = next(file)
            self.assertIn('field_a', header)
            self.assertIn('field_b', header)
            self.assertIn('field_c', header)

            first_line = next(file)
            self.assertEqual('a', first_line[len(first_line) - 3])
            self.assertEqual('b', first_line[len(first_line) - 2])
            self.assertEqual('', first_line[len(first_line) - 1])

            second_line = next(file)
            self.assertEqual('', second_line[len(second_line) - 3])
            self.assertEqual('b', second_line[len(second_line) - 2])
            self.assertEqual('c', second_line[len(second_line) - 1])


class TestGetReader(unittest.TestCase):
    def test_get_reader(self):
        # given:
        file_format = FileFormat.TSV
        file_path = get_file_source_path(os.path.join('in', 'test_in.tsv'))

        # when:
        with open(file_path, mode='r') as in_f:
            reader = get_handler(
                file_format=file_format,
                input_file=in_f,
                output_file_path='sources/in/',
                output_file_name='test_out.tsv',
                col_names=[]
            )

            # then:
            self.assertTrue(type(reader) is TSVFileHandler)


if __name__ == '__main__':
    unittest.main()
