import os

def get_file_source_path(file_name) -> str:
    current_path = os.getcwd()
    file_path_in_sources = os.path.join('sources', file_name)
    if 'test' not in current_path:
        file_path_in_sources = os.path.join('test', file_path_in_sources)
    return os.path.join(current_path, file_path_in_sources)

def get_cert_abs_path() -> str:
    cert_path = get_file_source_path(os.path.join('russiantrustedca', 'russiantrustedca.pem'))
    return os.path.abspath(cert_path)