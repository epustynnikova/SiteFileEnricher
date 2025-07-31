from dataclasses import dataclass


@dataclass(eq=True, order=True, unsafe_hash=True)
class InputElement:
    index_in_input_file: int
    link: str
    name: str

@dataclass(eq=True, order=True, unsafe_hash=True)
class FileColData:
    name: str
    value: str

@dataclass(eq=True, order=True, unsafe_hash=True)
class FileElement:
    link: str
    name: str
    col_data: FileColData

@dataclass(eq=True, order=True, unsafe_hash=True)
class OutputElement:
    index_in_input_file: int
    link: str
    new_col_datas: list[FileColData]