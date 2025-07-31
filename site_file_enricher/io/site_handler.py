import ssl
import time
import warnings
import re

import numpy
import requests
from aiohttp import ClientSession
from lxml import html as parser

from site_file_enricher.file_parser.xml_parser import XMLParser
from site_file_enricher.file_parser.html_parser import HTMLParser
from site_file_enricher.model.dto import FileColData, FileElement, FileElementType

warnings.filterwarnings('ignore')

USER_AGENT_VALUE = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
HEADERS = {'User-Agent': USER_AGENT_VALUE}
COOKIES = {'doNotAdviseToChangeLocationWhenIosReject': 'true',
           'sslCertificateChecker.timeout': '1740140953638'}
ATTACHMENTS_CSSSELECT_EXPRESSION = 'section.card-attachments .b-bottom .card-attachments-container .card-attachments__block .attachment .row .col-6 .row .col-12 .attachment__value a[href^="http"]'
ATTACHMENTS_LINKS_CSSSELECT_EXPRESSION = '.cardWrapper .wrapper .cardHeaderBlock .tabsNav__item'
SUBJECT_TITLES_CSSSELECT_EXPRESSION = '.cardWrapper .wrapper .container .row .col .blockInfo__section .section__title'
SUBJECT_INFO_CSSSELECT_EXPRESSION = '.cardWrapper .wrapper .container .row .col .blockInfo__section .section__info'


class SiteHandler:
    def __init__(self, xml_parser: XMLParser, html_parser: HTMLParser):
        self.parsers = {
            r'.*контракт.*\.xml': xml_parser,
            r'.*Печатная форма электронного контракта\.html.*' : html_parser
        }
        self.col_names = []
        if xml_parser is not None:
            self.col_names += xml_parser.col_names
        if html_parser is not None:
            self.col_names += html_parser.col_names


    async def download_xml_and_parse(self, contact_link: str, cert_abs_path: str):
        try:
            if contact_link:
                async with ClientSession(headers=HEADERS) as session:
                    context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS)
                    context.load_verify_locations(cert_abs_path)
                    time.sleep(1 + numpy.random.uniform(0, 1))
                    async with session.get(url=contact_link,
                                           allow_redirects=True,
                                           ssl=context,
                                           cookies=COOKIES) as response:
                        html = await response.text()
                        if response.status == requests.codes.ok:
                            dom = parser.fromstring(html)
                            link_elements = dom.cssselect(ATTACHMENTS_LINKS_CSSSELECT_EXPRESSION)
                            file_elements = []

                            titles = dom.cssselect(SUBJECT_TITLES_CSSSELECT_EXPRESSION)
                            infos = dom.cssselect(SUBJECT_INFO_CSSSELECT_EXPRESSION)

                            cnt = 0
                            while cnt < len(titles) and cnt < len(infos):
                                if titles[cnt].text == 'Предмет договора':
                                    file_elements.append(FileElement(
                                    link=contact_link,
                                        product_name='',
                                        price=-1,
                                    file_element_type=FileElementType.HTML,
                                    col_data=FileColData(-1, 'html_product_name', infos[cnt].text)
                                ))
                                cnt += 1


                            attachment_link = ''
                            for link_element in link_elements:
                                link = link_element.get("href")
                                if 'contractInfoId' in link and attachment_link ==  '':
                                    link_parts = link.split('?')
                                    if len(link_parts) == 2:
                                        attachment_link = f'https://zakupki.gov.ru/epz/contract/contractCard/document-info.html?{link_parts[1]}'

                            if attachment_link == '':
                                return file_elements

                            time.sleep(1 + numpy.random.uniform(0, 1))
                            async with session.get(url=attachment_link,
                                                   allow_redirects=True,
                                                   ssl=context,
                                                   cookies=COOKIES) as attachment_response:
                                html = await attachment_response.text()
                                link_to_parser = {}
                                if attachment_response.status == requests.codes.ok:
                                    dom = parser.fromstring(html)
                                    attachments = dom.cssselect(ATTACHMENTS_CSSSELECT_EXPRESSION)
                                    for attachment in attachments:
                                        title = attachment.get('title')
                                        for file_pattern in self.parsers:
                                            if re.match(file_pattern, title):
                                                link_to_parser[attachment.get('href')] = self.parsers[file_pattern]
                                                break
                                for contract_link in link_to_parser:
                                    file_parser = link_to_parser[contract_link]
                                    if file_parser is None or contract_link == '':
                                        continue
                                    time.sleep(1 + numpy.random.uniform(0, 1))
                                    async with session.get(url=contract_link,
                                                       allow_redirects=True,
                                                       ssl=context,
                                                       cookies=COOKIES) as file_response:
                                        content = await file_response.content.read()

                                    if file_response.status == requests.codes.ok :
                                        try:
                                            file_elements += file_parser.parse(content, contact_link)
                                        except Exception as ex:
                                            print(ex)
                                return file_elements
        except Exception as ex:
            print(ex)
            return []
