from abc import ABC, abstractmethod
import csv
from enum import Enum
from site_file_enricher.model.dto import InputElement


class FileFormat(Enum):
    TSV = 1


class Reader(ABC):

    @abstractmethod
    def read(self, file_data_as_bytes) -> list[InputElement]:
        """

        :param file_data_as_bytes: file content
        :return:
        """
        pass


class TSVReader(Reader):

    def read(self, file_data_as_bytes) -> dict[str, list[InputElement]]:
        tsv_file = csv.reader(file_data_as_bytes, dialect='excel-tab')
        index = -1
        elements = {}
        for lines in tsv_file:
            index += 1
            if index == 0:
                continue
            url = lines[4]
            if url == '':
                continue
            element = InputElement(index, url, lines[51])
            if url in elements:
                elements[url].append(element)
            else:
                elements[url] = [element]
        return elements


def get_reader(file_format: FileFormat) -> Reader:
    match file_format:
        case FileFormat.TSV:
            return TSVReader()
        case _:
            raise Exception(f"File format {file_format} isn't implemented as Reader!")



if __name__ == "__main__":
    with open('test_in.tsv', mode='r') as file:
        elements = TSVReader().read(file)
        print(elements)
