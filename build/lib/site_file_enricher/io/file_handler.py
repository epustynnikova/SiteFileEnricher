from abc import ABC, abstractmethod
import csv
from enum import Enum
import pandas as pd
import re

from typing_extensions import TextIO

from site_file_enricher.model.dto import InputElement, OutputElement


class FileFormat(Enum):
    TSV = 1,
    XLSX = 2


class FileHandler(ABC):

    @abstractmethod
    def read(self) -> dict[str, list[InputElement]]:
        """

        :return:
        """
        pass

    @abstractmethod
    def write(self, additional_elements: list[OutputElement]):
        """

        :param elements:
        :return:
        """
        pass


class XLXSFileHandler(FileHandler):
    def __init__(self, input_file_path: str, col_names: list[str]):
        self.input_file_path = input_file_path
        self.col_names = col_names
        self.col_names.sort()
        self.df = pd.read_excel(self.input_file_path, dtype=str, keep_default_na=False)
        for col_name in col_names:
            self.df[col_name] = pd.Series()

    def read(self) -> dict[str, list[InputElement]]:
        elements = {}
        for idx, row in self.df.iterrows():
            url = row['Ссылка на источник']
            name = row['Наименование продукта']
            raw_price = row['Цена за единицу продукции']
            okpd = row['Код ОКПД2/КТРУ продукта']
            if raw_price == '' or raw_price is None:
                continue
            price = int(float(raw_price)*100)
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

    def write(self, additional_elements: list[OutputElement]):
        if len(additional_elements) == 0:
            return

        for new_el in additional_elements:
            for file_col in new_el.new_col_datas:
                self.df.loc[new_el.index_in_input_file, file_col.name] = file_col.value

        self.df.to_excel(self.input_file_path)

class TSVFileHandler(FileHandler):
    def __init__(self, input_file: TextIO, output_file: TextIO):
        self.input_file = csv.reader(input_file, dialect='excel-tab')
        self.output_file = csv.writer(output_file, dialect='excel-tab')
        self.input_file_data = []

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
            price = int(float(''.join(i for i in lines[31] if i.isdigit() or i == ',').replace(',', '.'))*100)
            okpd = lines[46]
            element = InputElement(index, url, lines[51], price, okpd)
            if url in elements:
                elements[url].append(element)
            else:
                elements[url] = [element]
        self.input_file = input_file_line
        return elements

    def write(self, additional_elements: list[OutputElement]):
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


def get_handler(file_format: FileFormat, input_file, output_file, col_names: list[str]) -> FileHandler:
    match file_format:
        case FileFormat.TSV:
            return TSVFileHandler(input_file, output_file)
        case FileFormat.XLSX:
            return XLXSFileHandler(input_file, col_names)
        case _:
            raise Exception(f"File format {file_format} isn't implemented as FileHandler")
