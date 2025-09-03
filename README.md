# Парсинг госзакупок
## Текущая версия проекта: 1.1.0
### Эта программа парсит сайт госзакупок для обогащения информации о контрактах.
#### Поиск ведется:
- Для 223фз - раздел "Информация о договоре" / "Предмет договора";
- Для 44фз - раздел "Контракт" либо "Вложения" / html-файл контракта в части описания товаров и их характеристик;
- Для 44фз - раздел "Вложения" / xml-файл контракта в т.ч. в части торговой марки, НКМИ, названия НКМИ, описания товара из РУ.
            
#### Особенности работы:
В файле должны присутствовать столбцы 
- "Ссылка на источник"
- "Цена за единицу продукции"
- "Код ОКПД2/КТРУ продукта" либо "Код товара, работы или услуги (ОКПД2)", г) "Наименование продукта" либо "Название продукта".
                
#### Использованные библиотеки: 
- setuptools~=75.8.2
- typing_extensions~=4.12.2
- beautifulsoup4~=4.13.3
- lxml~=5.3.1
- aiofiles~=24.1.0
- pandas~=2.2.3
- numpy~=2.2.3
- requests~=2.32.3
- ipywidgets~=8.1.5
- aiohttp~=3.11.13
- cssselect~=1.2.0
- fuzzywuzzy~=0.18.0
- openpyxl~=3.1.5
- toga~=0.5.1
- pyinstaller~=6.13.0

# Сборка
Инструкции для сборки. 
Запускать из директории SiteFileEnricher.

## Сборка в исполняемый файл

```commandline
pyinstaller -F --windowed --noconfirm --clean -n file_enricher site_file_enricher/gui.py
```

## Сборка в файл пакета
```commandline
python setup.py bdist_wheel --universal
```
### Использование
```python
import os
from site_file_enricher.script import enrich_file_with_default_settings
cert_path = os.path.abspath('russiantrustedca/russiantrustedca.pem')
path_to_file = os.path.abspath('files/my_example.xlsx')
enrich_file_with_default_settings(
    abs_path_to_file=path_to_file, 
    cert_abs_path=cert_path,
    out_path=os.path.abspath('files'),
    out_file_name="enriched_my_example.xlsx"
)
```

# Тесты

Запускать из директории SiteFileEnricher.

## Запуск юнит-тестов

```commandline
python -m unittest test/test_unit*
```

## Запуск интеграционных тестов

```commandline
python -m unittest test/test_integration*
```
(Проходят достаточно медленно, тк делают запросы непосредственно в госзакупки)
