import csv
import unittest
from site_file_enricher import OutputElement, FileColData
from site_file_enricher.io.file_handler import TSVFileHandler, FileFormat, get_handler


class TestTSVFileHandler(unittest.TestCase):
    def test_read(self):
        # given:
        with open('sources/in/test_in.tsv', mode='r') as in_f, open('sources/in/test_out.tsv', mode='w') as out_f:
            handler = TSVFileHandler(in_f, out_f)
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
            print(result['https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=1772801635124000615'])
            print(result['https://zakupki.gov.ru/epz/contract/contractCard/common-info.html?reestrNumber=2616410011824000637'])
            self.assertEqual(7, len(result))
            index = 1
            for key in result:
                elements = result[key]
                self.assertEqual(test_data[index], len(elements))
                index += 1

    def test_write(self):
        # given:
        with open('sources/out/test_in.tsv', mode='r') as in_f, open('sources/out/test_out.tsv', mode='w') as out_f:
            handler = TSVFileHandler(in_f, out_f)
            handler.read()

            # when:
            handler.write(
                [
                    OutputElement(1, "test", [FileColData(1, "field_a", "a"), FileColData(1, "field_b", "b")]),
                    OutputElement(2, "test_2", [FileColData(1, "field_c", "c"), FileColData(1, "field_b", "b")])
                ]
            )

        # then:
        with open('sources/out/test_out.tsv', mode='r') as out_f:
            file = csv.reader(out_f, dialect='excel-tab')
            header = next(file)
            self.assertIn('field_a', header)
            self.assertIn('field_b', header)
            self.assertIn('field_c', header)

            first_line = next(file)
            self.assertEqual('a', first_line[len(first_line) - 3])
            self.assertEqual('b', first_line[len(first_line) - 2])
            self.assertEqual('',  first_line[len(first_line) - 1])

            second_line = next(file)
            self.assertEqual('', second_line[len(second_line) - 3])
            self.assertEqual('b', second_line[len(second_line) - 2])
            self.assertEqual('c', second_line[len(second_line) - 1])


class TestGetReader(unittest.TestCase):
    def test_get_reader(self):
        # given:
        file_format = FileFormat.TSV

        # when:
        with open('sources/in/test_in.tsv', mode='r') as in_f, open('sources/in/test_out.tsv', mode='w') as out_f:
            reader = get_handler(file_format, in_f, out_f, [], [])

            # then:
            self.assertTrue(type(reader) is TSVFileHandler)


if __name__ == '__main__':
    unittest.main()
