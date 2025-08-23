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

import logging

logging.basicConfig(filename=f'site-file-enricher-site-handler.log',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SiteHandler:
    def __init__(self, xml_parser: XMLParser, html_parser: HTMLParser):
        self.parsers = {
            r'.*контракт.*\.xml': xml_parser,
            r'.*Печатная форма электронного контракта\.html.*': html_parser
        }
        self.html_parser = html_parser
        self.col_names = []
        if xml_parser is not None:
            self.col_names += xml_parser.col_names
        if html_parser is not None:
            self.col_names += html_parser.col_names

    @staticmethod
    def __try_to_find_product_name__(dom, contact_link) -> FileElement | None:
        titles = dom.cssselect(SUBJECT_TITLES_CSSSELECT_EXPRESSION)
        infos = dom.cssselect(SUBJECT_INFO_CSSSELECT_EXPRESSION)
        cnt = 0
        while cnt < len(titles) and cnt < len(infos):
            if titles[cnt].text == 'Предмет договора':
                return FileElement(
                    link=contact_link,
                    product_name='',
                    price=-1,
                    file_element_type=FileElementType.HTML,
                    col_data=FileColData(-1, 'html_product_name', infos[cnt].text)
                )
            cnt += 1
        return None

    @staticmethod
    def __try_to_find_attachments_link__(dom) -> str:
        link_elements = dom.cssselect(ATTACHMENTS_LINKS_CSSSELECT_EXPRESSION)
        attachment_link = ''
        for link_element in link_elements:
            link = link_element.get("href")
            if 'contractInfoId' in link and attachment_link == '':
                link_parts = link.split('?')
                if len(link_parts) == 2:
                    attachment_link = f'https://zakupki.gov.ru/epz/contract/contractCard/document-info.html?{link_parts[1]}'
        return attachment_link

    @staticmethod
    def __try_to_find_contract_draft_link__(dom) -> str:
        link_elements = dom.cssselect(ATTACHMENTS_LINKS_CSSSELECT_EXPRESSION)
        attachment_link = ''
        for link_element in link_elements:
            link = link_element.get("href")
            if 'contract-draft' in link and attachment_link == '':
                link_parts = link.split('?')
                if len(link_parts) == 2:
                    attachment_link = f'https://zakupki.gov.ru/epz/order/notice/rpec/contract-draft.html?{link_parts[1]}'
        return attachment_link

    @staticmethod
    def __try_to_find_script_link_to_html_contract__(dom):
        link_to_html_contract = None
        for script in dom.cssselect('script'):
            if script is None:
                continue
            text_in_script = script.text
            if text_in_script is None:
                continue
            if 'uid' in text_in_script:
                match = re.search(r'\'([^\']+)\'', script.text)
                if match is not None:
                    link_to_html_contract = match.group(1)
                    break
        return link_to_html_contract

    @staticmethod
    async def __async_download_page_and_build_dom__(session, context, link):
        dom = None

        if link is None or link == '':
            return dom

        try:
            time.sleep(1 + numpy.random.uniform(0, 1))
            async with session.get(url=link,
                                   allow_redirects=True,
                                   ssl=context,
                                   cookies=COOKIES) as response:
                html = await response.text()
                if response.status == requests.codes.ok:
                    dom = parser.fromstring(html)
        except Exception as ex:
            logger.error(f'Have a problem with downloading and building dom from {link}: {str(ex)}')

        return dom

    @staticmethod
    async def __async_download_from_link__(session, context, link):
        file_content = None

        if link is None or link == '':
            return file_content

        try:
            time.sleep(1 + numpy.random.uniform(0, 1))
            async with session.get(url=link,
                                   allow_redirects=True,
                                   ssl=context,
                                   cookies=COOKIES) as response:
                file_content = await response.content.read()
                if response.status != requests.codes.ok:
                    file_content = None
        except Exception as ex:
            logger.error(f'Have a problem with downloading from {link}: {str(ex)}')

        return file_content

    def __map_attachment_to_parser__(self, dom) -> dict[str, XMLParser | HTMLParser]:
        attachments = dom.cssselect(ATTACHMENTS_CSSSELECT_EXPRESSION)
        link_to_parser = {}
        for attachment in attachments:
            title = attachment.get('title')
            for file_pattern in self.parsers:
                if re.match(file_pattern, title):
                    link_to_parser[attachment.get('href')] = self.parsers[file_pattern]
                    break
        return link_to_parser

    async def __async_search_contract_draft__(self, session, context, contract_draft_link, contact_link) -> list[
        FileElement]:
        file_elements = []

        dom = await SiteHandler.__async_download_page_and_build_dom__(session, context, contract_draft_link)
        if dom is None or self.html_parser is None:
            return file_elements

        link_to_html_contract = SiteHandler.__try_to_find_script_link_to_html_contract__(dom)
        html_contract_content = await SiteHandler.__async_download_from_link__(session, context, link_to_html_contract)

        if html_contract_content is not None:
            try:
                return self.html_parser.parse(html_contract_content, contact_link)
            except Exception as ex:
                logger.error(f'Have a problem with html contract tab parsing from {context}: {str(ex)}')
        return file_elements

    async def __async_search_through_attachments__(self, session, context, contract_link, attachment_link):
        file_elements = []

        if attachment_link is None or attachment_link == '':
            return []

        dom = await SiteHandler.__async_download_page_and_build_dom__(session, context, attachment_link)

        if dom is not None:
            link_to_parser = self.__map_attachment_to_parser__(dom)
            for attachment_content_link in link_to_parser:
                file_parser = link_to_parser[attachment_content_link]
                if file_parser is None or attachment_content_link == '':
                    continue
                file_content = await SiteHandler.__async_download_from_link__(session, context, attachment_content_link)
                if file_content is not None:
                    try:
                        file_elements += file_parser.parse(file_content, contract_link)
                    except Exception as ex:
                        logger.error(
                            f'Have a problem with parsing attachments from {attachment_content_link} for link {contract_link}: {str(ex)}'
                        )
        return file_elements

    async def download_xml_and_parse(self, contract_link: str, cert_abs_path: str):
        try:
            if contract_link:
                async with ClientSession(headers=HEADERS) as session:
                    context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS)
                    context.load_verify_locations(cert_abs_path)

                    main_page = await SiteHandler.__async_download_page_and_build_dom__(
                        session, context, contract_link)
                    if main_page is not None:
                        # only product name
                        html_product_name = SiteHandler.__try_to_find_product_name__(main_page, contract_link)
                        if html_product_name is not None:
                            return [html_product_name]

                        # contract draft
                        contract_draft_link = SiteHandler.__try_to_find_contract_draft_link__(main_page)
                        contact_draft_elements = await self.__async_search_contract_draft__(
                            session, context, contract_draft_link, contract_link
                        )
                        if len(contact_draft_elements) != 0:
                            return contact_draft_elements

                        # attachments
                        attachment_link = SiteHandler.__try_to_find_attachments_link__(main_page)
                        attachment_elements = await self.__async_search_through_attachments__(
                            session, context, contract_link, attachment_link)
                        return attachment_elements
                    else:
                        return []
        except Exception as ex:
            logger.error(f"Something unusual happened with {contract_link}: {str(ex)}")

        return []
