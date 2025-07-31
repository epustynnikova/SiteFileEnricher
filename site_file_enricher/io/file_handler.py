import os
from abc import ABC, abstractmethod
import csv
from enum import Enum
import pandas as pd
import datetime
from typing_extensions import TextIO
from openpyxl import Workbook

from site_file_enricher.model.dto import InputElement, OutputElement


class FileFormat(Enum):
    TSV = 1,
    XLSX = 2


class FileHandler(ABC):

    @abstractmethod
    def read_elements_count(self) -> int:
        """

        :return:
        """
        pass

    @abstractmethod
    def read(self) -> dict[str, list[InputElement]]:
        """

        :return:
        """
        pass

    @abstractmethod
    def write(self, additional_elements: list[OutputElement], link):
        """

        :param elements:
        :return:
        """
        pass


class XLXSFileHandler(FileHandler):

    def __init__(self,
                 input_file_path: str,
                 col_names: list[str],
                 output_file_path: str,
                 output_file_name: str,
                 file_row_count: int = 300,
                 ):
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.output_file_name = output_file_name
        self.col_names = col_names
        self.col_names.sort()
        self.df = pd.read_excel(self.input_file_path, dtype=str, keep_default_na=False, engine='openpyxl')
        self.df.drop(self.df.columns[self.df.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)
        for col_name in col_names:
            self.df[col_name] = pd.Series()
        self.count_saved_rows = 0
        self.file_number = 0
        self.file_row_count = file_row_count

    def read_elements_count(self) -> int:
        return len(self.df.index)

    def read(self) -> dict[str, list[InputElement]]:
        elements = {}
        for idx, row in self.df.iterrows():
            url = self.read_row_value(row, ['Ссылка на источник'])
            name = self.read_row_value(row, ['Название продукта', 'Наименование продукта'])
            raw_price = self.read_row_value(row, ['Цена за единицу продукции'])
            okpd = self.read_row_value(row, ['Код товара, работы или услуги (ОКПД2)', 'Код ОКПД2/КТРУ продукта'])
            if raw_price == '' or raw_price is None:
                continue
            price = int(float(raw_price) * 100)
            element = InputElement(
                index_in_input_file=idx,
                link=url,
                name=name,
                price=price,
                okpd_ktru=okpd
            )
            if url in elements:
                elements[url].append(element)
            else:
                elements[url] = [element]
        return elements

    @staticmethod
    def read_row_value(row, names: list[str]) -> str:
        for name in names:
            if name in row:
                return row[name]
        return ''

    def write(self, additional_elements: list[OutputElement], link = None):
        print(f'Link: {link}:, current rows count: {self.count_saved_rows}')
        for new_el in additional_elements:
            for file_col in new_el.new_col_datas:
                self.df.loc[new_el.index_in_input_file, file_col.name] = file_col.value

        start = datetime.datetime.now()

        saved_data = self.df[self.df['Ссылка на источник'] == link]
        print(f'TEST: Link: {link}: {len(saved_data)}, current rows count: {self.count_saved_rows}')

        saved_len = len(saved_data)
        saved_data_idx = 0
        while saved_len > 0:
            if self.count_saved_rows == self.file_row_count:
                self.count_saved_rows = 0
                self.file_number += 1

            current_saved_data = saved_data[saved_data_idx:(self.file_row_count - self.count_saved_rows + saved_data_idx)]
            file_path = os.path.join(self.output_file_path, f'{str(self.file_number)}_{self.output_file_name}')

            print(f'Saved to {file_path}')
            if self.count_saved_rows == 0:
                with pd.ExcelWriter(file_path) as writer:
                    current_saved_data.to_excel(writer, engine='openpyxl')
            else:
                with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
                    current_saved_data.to_excel(writer, startrow=self.count_saved_rows + 1, header=False)

            saved_data_idx += len(current_saved_data)
            self.count_saved_rows += len(current_saved_data)
            print(f"Current saved row: {self.count_saved_rows}")
            saved_len -= len(current_saved_data)

        end = datetime.datetime.now()

        print(f"SAVED TIME: {end - start}")
        print(f'TEST: Link: {link}: {len(saved_data)}, current rows count: {self.count_saved_rows}')


class TSVFileHandler(FileHandler):

    def __init__(self, input_file: TextIO, output_file):
        self.input_file = csv.reader(input_file, dialect='excel-tab')
        self.output_file = csv.writer(output_file, dialect='excel-tab')
        self.input_file_data = []

    def read_elements_count(self) -> int:
        return len(self.input_file_data)

    def read(self) -> dict[str, list[InputElement]]:
        index = -1
        elements = {}
        input_file_line = []
        for lines in self.input_file:
            index += 1
            self.input_file_data.append(lines)
            if index == 0:
                continue
            url = lines[4]
            if url == '':
                continue
            price = int(float(''.join(i for i in lines[31] if i.isdigit() or i == ',').replace(',', '.')) * 100)
            okpd = lines[46]
            element = InputElement(index, url, lines[51], price, okpd)
            if url in elements:
                elements[url].append(element)
            else:
                elements[url] = [element]
        self.input_file = input_file_line
        return elements

    def write(self, additional_elements: list[OutputElement], link = None):
        col_data_names = list(
            set([col_data.name for element in additional_elements for col_data in element.new_col_datas]))
        col_data_names.sort()

        header = self.input_file_data[0]
        self.output_file.writerow(header + col_data_names)

        new_info_by_line = {}
        for element in additional_elements:
            new_info = []
            added_info = dict({(ncd.name, ncd.value) for ncd in element.new_col_datas})
            for col_data_name in col_data_names:
                if col_data_name in added_info:
                    new_info.append(added_info[col_data_name])
                else:
                    new_info.append(None)
            new_info_by_line[element.index_in_input_file] = new_info

        for idx, row in enumerate(self.input_file_data):
            if idx == 0:
                continue
            if idx in new_info_by_line:
                self.output_file.writerow(row + new_info_by_line[idx])
            else:
                self.output_file.writerow(row)


def get_handler(file_format: FileFormat, input_file, output_file_path, output_file_name,
                col_names: list[str],
                file_row_count: int = 300) -> FileHandler:
    match file_format:
        case FileFormat.TSV:
            return TSVFileHandler(input_file, os.path.join(output_file_path, output_file_name))
        case FileFormat.XLSX:
            return XLXSFileHandler(input_file,
                                   col_names,
                                   output_file_path=output_file_path,
                                   output_file_name=output_file_name,
                                   file_row_count=file_row_count)
        case _:
            raise Exception(f"File format {file_format} isn't implemented as FileHandler")
