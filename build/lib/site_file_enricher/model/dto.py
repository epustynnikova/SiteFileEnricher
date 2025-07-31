from dataclasses import dataclass
from typing import Union


@dataclass(eq=True, order=True, unsafe_hash=True)
class InputElement:
    index_in_input_file: int
    link: str
    name: str
    price: int = None
    okpd_ktru: str = None

@dataclass(eq=True, order=True, unsafe_hash=True)
class FileColData:
    index_num: int
    name: str
    value: str

@dataclass(eq=True, order=True, unsafe_hash=True)
class FileElement:
    link: str
    product_name: str
    price: int
    col_data: FileColData
    ktru: Union[str, None] = None
    okpd: Union[str, None] = None

@dataclass(eq=True, order=True, unsafe_hash=True)
class OutputElement:
    index_in_input_file: int
    link: str
    new_col_datas: list[FileColData]