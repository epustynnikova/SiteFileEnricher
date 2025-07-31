import unittest
from site_file_enricher.file_parser.html_parser import HTMLParser, HTMLElement, HTMLContractFormat, RootTHMLElement


class TestHTMLParser(unittest.TestCase):
    def test_parse_html_type_a(self):
        # given:
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
        parser = HTMLParser(type_a_root_element, None)

        # when:
        with open('sources/html/type_a.html', 'r') as file:
            results = parser.parse(file.read(), 'test')

        # then:
        self.assertEqual(3, len(results))
        for file_element in results:
            self.assertEqual('test', file_element.link)
            self.assertEqual('Контейнер для сбора образца калаNS-PRIME', file_element.product_name)
            self.assertEqual(13127400, file_element.price)
            match file_element.col_data.name:
                case 'html_product_name':
                    self.assertEqual('Контейнер для сбора образца калаNS-PRIME', file_element.col_data.value)
                case 'html_ktru':
                    self.assertEqual(
                        'Изделия медицинские, в том числе хирургические, прочие, не включенные в другие группировки (32.50.50.190)',
                        file_element.col_data.value)
                case 'html_characteristics':
                    self.assertEqual(
                        'Назначение : Для сбора кала при проведении анализа на колоректальный рак; Содержание буферного раствора, мл: 1.9 ; количество контейнеров: 400 Штука; Метод: Однодневный; Совместимость: С анализатором NS-PRIME;',
                        file_element.col_data.value)

    def test_parse_html_type_b(self):
        # given:
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
        parser = HTMLParser(None, type_b_root_element)
        expected = {
            (0, 'html_product_name', 'Калибраторы концентрации гемоглобина в упаковке FIT Hemoglobin NS-PRIME Calibrator Товарный знак: Набор реагентов для калибровки концентрации гемоглобина в упаковке для анализаторов NS-Prime и NS-Prime AA01 - FIT Hemoglobin NS-Prime Calibrator (ФИТ Гемоглобин NS-Prime калибратор) в составе: 1. Калибратор (лиофилизированный) - 4 шт. (Содержание человеческого гемоглобина 1000-1400 нг/флакон). 2. Растворитель калибратора (12 мл) - 1 шт., РУ №РЗН 2019/9052 от 14.04.2022г.'),
            (1, 'html_ktru', 'Препараты диагностические (21.20.23.111)'),
            (2, 'html_characteristics', 'Состав упаковки: 4 флакона по 1 мл, 1 флакон по 12 мл; Специализированный калибратор для набора FIT Гемоглобин для определения концентрации гемоглобина в кале для дискретного анализатора клинической химии на системе NS- PRIME: Соответствие;'),
            (3, 'html_product_name', 'Калибратор концентрации трансферрина в упаковке -FIT Transferrin NS-RIME Calibrator Товарный знак: Набор реагентов для калибровки концентрации трансферрина в упаковке для анализаторов NS-Prime и NS-Prime AA01 - FIT Transferrin NS-Prime Calibrator (ФИТ Трансферрин NS-Prime Калибратор) в составе: 1. Флакон с калибратором (лиофилизированным) - 4 шт. (содержание человеческого трансферрина 400-600 нг/флакон). 2. Флакон с растворителем калибратора (12 мл) - 1 шт., РУ №РЗН 2019/8842 от 14.04.2022г.'),
            (4, 'html_ktru', 'Препараты диагностические (21.20.23.111)'),
            (5, 'html_characteristics', 'Специализированный калибратор для набора FIT Трансферрин для определения концентрации трансферрина в кале для дискретного анализатора клинической химии на системе NS-PRIME: Соответствие; Состав упаковки: 4 флакона по 1 мл, 1 флакон по 12 мл;'),
            (6, 'html_product_name', 'Контроли концентрации гемоглобина и/или трансферрина для системы NS-PRIME в упаковке - FIT NS-PRIME Control Товарный знак: Набор контролей концентрации гемоглобина и/или трансферрина в упаковке для анализаторов NS-Prime и NS-Prime АА01 - FIT NS-PRIME CONTROL (ФИТ NS-Prime Контроль), РУ №РЗН 2019/9053 от 29.12.2021г.'),
            (7, 'html_ktru', 'Препараты диагностические (21.20.23.111)'),
            (8, 'html_characteristics', 'Состав упаковки: 1) 1 флакон 30 мл, 3) 5 флаконов по 2 мл, 2) 5 флаконов по 2 мл; Контроль для наборов FIT Гемоглобин и FIT Трансферрин для определения концентрации гемоглобина и трансферрина в кале для дискретного анализатора клинической химии на системе NS- PRIME: Соответствие;'),
        }

        # when:
        with open('sources/html/type_b.html', 'r') as file:
            results = parser.parse(file.read(), 'test')

        # then:
        self.assertEqual(9, len(results))

        for expected_item in expected:
            self.assertEqual(
                expected_item[1],
                results[expected_item[0]].col_data.name
            )
            self.assertEqual(
                expected_item[2],
                results[expected_item[0]].col_data.value
            )

    def test_both(self):
        # given:
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
        parser = HTMLParser(type_a_root_element, type_b_root_element)

        # when:
        with open('sources/html/row_9.html', 'r') as file:
            results = parser.parse(file.read(), 'test')

        # then:
        self.assertEqual(6, len(results))

    def test_contract_layer(self):
        # given:
        url = 'https://zakupki.gov.ru/epz/order/notice/rpec/contract-draft.html?regNumber=01015000003250001460011'


    def test_(self):
        # given:
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
        parser = HTMLParser(type_a_root_element, type_b_root_element)

        # when:
        with open('sources/html/test.html', 'r') as file:
            results = parser.parse(file.read(), 'test')

        # then:
        self.assertEqual(3, len(results))
