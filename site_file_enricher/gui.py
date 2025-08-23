import datetime
import os
from pyexpat.errors import messages

import toga
from numpy.f2py.auxfuncs import throw_error
from openpyxl.styles.builtins import title
from toga.app import App
from toga.style import Pack
from toga.constants import COLUMN

from site_file_enricher.io.file_handler import FileFormat, get_handler
from site_file_enricher.io.site_handler import SiteHandler
from site_file_enricher.file_parser.xml_parser import XMLParser, RootXMLElement, XMLElement
from site_file_enricher.file_parser.html_parser import HTMLParser, HTMLElement, HTMLContractFormat, RootTHMLElement
from site_file_enricher.search.fuzzy import search
from site_file_enricher.model.dto import FileElementType, OutputElement

import logging

logging.basicConfig(filename=f'site-file-enricher.log',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GuiApplication(toga.App):

    def __init__(self, formal_name, app_id):
        super().__init__(formal_name=formal_name, app_id=app_id)
        logger.info('dhysfgtyue')
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
        htmp_parser = HTMLParser(type_a_root_element, type_b_root_element)
        self.site_handler = SiteHandler(
            xml_parser=XMLParser(
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
            ),
            html_parser=htmp_parser)

    async def exit_handler(self, app):
        App.exit(self)

    def startup(self):
        self.file_name = None
        self.cert_path = None

        self.main_window = toga.MainWindow()
        self.on_exit = self.exit_handler

        self.info_box = toga.MultilineTextInput(readonly=True, style=Pack(flex=1, margin_top=20))

        self.label = toga.Label("Приложение запущено.", style=Pack(margin_top=20))

        # Buttons
        btn_style = Pack(flex=1)
        btn_app_open_xslx = toga.Button(
            "Открыть xslx-файл",
            on_press=self.action_open_file_xslx,
            style=btn_style,
        )

        btn_app_open_cert = toga.Button(
            "Открыть файл с сертификатом",
            on_press=self.action_open_file_cert,
            style=btn_style,
        )

        btn_start = toga.Button(
            "Запустить обработку",
            on_press=self.action_start_script,
            style=btn_style
        )

        btn_app_info = toga.Button(
            "Информация о приложении", on_press=self.action_app_info_dialog, style=btn_style
        )

        switch_check_okpd = toga.Switch(
            text="Проверять ОКПД при сопоставлении строк",
            on_change=self.check_okpd,
            value=True,
            style=btn_style,
        )

        switch_check_other_column = toga.Switch(
            text="Сопоставлять строки по остаточному принципу",
            on_change=self.check_other_column,
            value=False,
            style=btn_style,
        )

        self.progress_bar = toga.ProgressBar(max=100, value=0)

        # Outermost box
        box = toga.Box(
            children=[
                btn_app_open_xslx,
                btn_app_open_cert,
                switch_check_okpd,
                switch_check_other_column,
                self.progress_bar,
                btn_start,
                self.info_box,
                self.label,
                btn_app_info
            ],
            style=Pack(flex=1, direction=COLUMN, margin=10),
        )

        # Add the content on the main window
        self.main_window.content = box

        # Show the main window
        self.main_window.show()

    async def check_okpd(self, widget):
        if self.check_okpd.value:
            self.check_okpd.value = False
        else:
            self.check_okpd.value = True


    async def check_other_column(self, widget):
        if self.check_other_column.value:
            self.check_other_column.value = False
        else:
            self.check_other_column.value = True

    async def action_app_info_dialog(self, widget):
        await self.dialog(toga.InfoDialog(
            title="Информация о приложении",
            message="""
        Эта программа парсит xml-файлы, соответствующие ссылкам на государственные контракты, перечисленные в исходном файле, и подгружает сведения о товарах в конец таблицы.
        
        - В файле должны присутствовать столбцы а) "Ссылка на источник", б) "Цена за единицу продукции", в) "Код ОКПД2/КТРУ продукта" либо "Код товара, работы или услуги (ОКПД2)", г) "Наименование продукта" либо "Название продукта".
        
        - Позиции в xml-файле и строки исходного файла сопоставляются сначала по цене, затем по кодам ОКПД/КТРУ, затем по описанию товара.
        
        - Если обрабатываемый файл содержит не все позиции контракта, информация будет добавлена только по присутствующим, исходя из максимального соответствия.
        
        - Дополнительно переименовывать столбцы или сортировать строки в обрабатываемом файле не требуется. Даже если позиции одного контракта разнесены по строкам в разные части файла, один контракт парсится один раз, т.к. в начале обработки создается словарь ссылок.
        
        - Для удобства в процессе обработки сбрасывается графическое оформление. Результат сохраняется в отдельный файл.
        
        - Сохранение происходит каждые найденные 100 элементов и в конце файла.
        
        Версия Python 3.13.1 или выше.
        
        Использованные библиотеки: 
        setuptools~=75.8.2
        typing_extensions~=4.12.2
        beautifulsoup4~=4.13.3
        lxml~=5.3.1
        aiofiles~=24.1.0
        pandas~=2.2.3
        numpy~=2.2.3
        requests~=2.32.3
        ipywidgets~=8.1.5
        aiohttp~=3.11.13
        cssselect
        fuzzywuzzy~=0.18.0
        openpyxl
        toga
        pyinstaller
        """))
        self.label.text = "Была предоставлена информация о приложении"

    async def action_open_file_cert(self, widget):
        if self.progress_bar.value in [0, 100]:
            cert_path = await self.dialog(toga.OpenFileDialog("Открыть файл с сертификатом"))
            if cert_path is not None:
                self.cert_path = cert_path
                self.label.text = f"Открыт файл с сертификатом: {cert_path}"
            else:
                self.label.text = "Ни один файл с сертификатом не выбран"
                self.cert_path = None
        else:
            await self.dialog(toga.InfoDialog(
                "Внимание",
                f"Приложение в данный момент обрабатывает файл {self.file_name}, нельзя изменить файл с сертификатом"))
            self.label.text = "Предупреждение: нельзя изменить файл с сертификатом, тк не закончен предыдущий"

    async def action_open_file_xslx(self, widget):
        if self.progress_bar.value in [0, 100]:
            fname = await self.dialog(toga.OpenFileDialog("Открыть xlsx-файл"))
            if fname is not None:
                self.file_name = fname
                self.label.text = f"Открыт xslx-файл: {fname}"
                self.progress_bar.value = 0
                self.file_handler = get_handler(
                    file_format=FileFormat.XLSX,
                    input_file=self.file_name,
                    output_file_path=self.file_name.parent,
                    output_file_name=self.file_name.name,
                    file_row_count=300,
                    col_names=self.site_handler.col_names
                )
            else:
                self.label.text = "Ни один xslx-файл не выбран"
        else:
            await self.dialog(toga.InfoDialog(
                "Внимание",
                f"Приложение в данный момент обрабатывает файл {self.file_name}, новый процесс обработки не может быть начат"))
            self.label.text = "Предупреждение: не может быть начат новый цикл обработки, тк не закончен предыдущий"

    async def action_start_script(self, widget):
        if self.progress_bar.value in [0, 100]:
            if self.file_name is None:
                await self.dialog(toga.InfoDialog("Внимание", "Не выбран xlsx-файл"))
                self.label.text = "Предупреждение: не выбран xlsx-файл"
            elif self.cert_path is None:
                await self.dialog(toga.InfoDialog("Внимание", "Не выбран файл c сертификатом"))
                self.label.text = "Предупреждение: не выбран файл с сертификатом"
            else:
                self.label.text = f"Начата обработка файла {self.file_name}"
                self.progress_bar.value = 0
                self.info_box.value = ""

                link_to_input_elements = self.file_handler.read()

                new_elements = []

                all_count = self.file_handler.read_elements_count()
                handled_count = 0

                for link in link_to_input_elements:
                    input_elements = link_to_input_elements[link]
                    saved = False
                    try:
                        logger.info(f'Download and parse xml for {link}')
                        start = datetime.datetime.now()

                        file_elements = await self.site_handler.download_xml_and_parse(link, self.cert_path)
                        xml_product_info_els = [file_el for file_el in file_elements
                                                if
                                                file_el.product_name != '' and file_el.file_element_type == FileElementType.XML]
                        html_product_info_els = [file_el for file_el in file_elements if
                                                file_el.product_name != '' and file_el.file_element_type == FileElementType.HTML]
                        universal_col_datas = [file_el.col_data for file_el in file_elements if file_el.product_name == '']

                        end = datetime.datetime.now()
                        logger.info(f'Downloaded and parse xml for {link} -- {end - start}')

                        logger.info(f'Fuzzy search started for link: {link} for xml elements')
                        start = datetime.datetime.now()

                        searched_output_elements = search(input_elements, xml_product_info_els)
                        for searched_output_element in searched_output_elements:
                            searched_output_element.new_col_datas += universal_col_datas
                        new_elements += searched_output_elements

                        end = datetime.datetime.now()
                        logger.info(f'Fuzzy search ended for link: {link} for xml elements -- {end - start}')

                        logger.info(f'Fuzzy search stared for link: {link} for html elements')
                        start = datetime.datetime.now()

                        searched_output_elements = search(input_elements, html_product_info_els)
                        for searched_output_element in searched_output_elements:
                            searched_output_element.new_col_datas += universal_col_datas
                        new_elements += searched_output_elements

                        end = datetime.datetime.now()
                        logger.info(f'Fuzzy search ended for link: {link} for html elements -- {end - start}')

                        if len(xml_product_info_els) == len(html_product_info_els) == 0 and len(universal_col_datas) != 0:
                            for input_el in input_elements:
                                new_elements.append(OutputElement(
                                    index_in_input_file=input_el.index_in_input_file,
                                    link=input_el.link,
                                    new_col_datas=universal_col_datas
                                ))

                        logger.info(f'Save {len(new_elements)} for {link}')
                        start = datetime.datetime.now()

                        self.file_handler.write(new_elements, link=link)
                        saved = True

                        end = datetime.datetime.now()
                        logger.info(f'Saved {len(new_elements)} for {link} -- {end - start}')

                        new_elements.clear()
                    except Exception as ex:
                        logger.error(f'Something happened with {link}: {str(ex)}')
                        if not saved:
                            logger.info(f'Save {len(input_elements)} for {link}')
                            start = datetime.datetime.now()

                            self.file_handler.write([], link=link)

                            end = datetime.datetime.now()
                            logger.info(f'Saved {len(input_elements)} for {link} -- {end - start}')

                    handled_count += len(link_to_input_elements[link])
                    self.progress_bar.value = round(100 * (handled_count / all_count))
                    print(self.progress_bar.value)

                    self.info_box.value = f"Обработано {len(link_to_input_elements[link])} элементов для ссылки = {link}\n\n" + self.info_box.value

                self.label.text = f"Закончена обработка файла {self.file_name}"
                self.file_name = None
                self.progress_bar.value = 100
        else:
            await self.dialog(toga.InfoDialog("Внимание", f"Не закончена обработка файла {self.file_name}"))
            self.label.text = "Предупреждение: не закончена обработка предыдущего файла"

    def exit(self, source_widget):
        App.exit(self)


app = GuiApplication(formal_name="Парсим госзакупки", app_id="site.file.enricher")
app.main_loop()
