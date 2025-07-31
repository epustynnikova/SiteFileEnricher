import asyncio
import ssl
import time
import warnings

import numpy
import requests
from aiohttp import ClientSession
from lxml import html as parser

from site_file_enricher.file_parser.xml_parser import XMLParser

warnings.filterwarnings('ignore')

USER_AGENT_VALUE = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
HEADERS = {'User-Agent': USER_AGENT_VALUE}
COOKIES = {'doNotAdviseToChangeLocationWhenIosReject': 'true',
           'sslCertificateChecker.timeout': '1740140953638'}
ATTACHMENTS_CSSSELECT_EXPRESSION = 'section.card-attachments .b-bottom .card-attachments-container .card-attachments__block .attachment .row .col-6 .row .col-12 .attachment__value a[href^="http"]'
ATTACHMENTS_LINKS_CSSSELECT_EXPRESSION = '.cardWrapper .wrapper .cardHeaderBlock .tabsNav__item'


async def download_xml_and_parse(contact_link: str, cert_abs_path: str, xml_parser: XMLParser):
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
                        attachment_link = ''
                        for link_element in link_elements:
                            link = link_element.get("href")
                            if 'contractInfoId' in link:
                                link_parts = link.split('?')
                                if len(link_parts) == 2:
                                    attachment_link = f'https://zakupki.gov.ru/epz/contract/contractCard/document-info.html?{link_parts[1]}'
                                    break
                        if attachment_link == '':
                            return []
                        time.sleep(1 + numpy.random.uniform(0, 1))
                        async with session.get(url=attachment_link,
                                               allow_redirects=True,
                                               ssl=context,
                                               cookies=COOKIES) as attachment_response:
                            html = await attachment_response.text()
                            contract_link = ''
                            if attachment_response.status == requests.codes.ok:
                                dom = parser.fromstring(html)
                                attachments = dom.cssselect(ATTACHMENTS_CSSSELECT_EXPRESSION)
                                for attachment in attachments:
                                    title = attachment.get('title')
                                    if 'xml' in title and 'контракт' in title:
                                        contract_link = attachment.get('href')
                            if contract_link == '':
                                return []
                            time.sleep(1 + numpy.random.uniform(0, 1))
                            async with session.get(url=contract_link,
                                                   allow_redirects=True,
                                                   ssl=context,
                                                   cookies=COOKIES) as file_response:
                                content = await file_response.content.read()

                                if file_response.status == requests.codes.ok:
                                    return xml_parser.parse(content, contact_link)
    except Exception as ex:
        print(ex)
    return []


def handle_contract_links(links: list[str], cert_abs_path: str, xml_parser: XMLParser):
    link_to_elements = {}

    for link in links:
        print(f'Download and parse xml for {link}')
        elements = asyncio.run(download_xml_and_parse(link, cert_abs_path, xml_parser))
        if len(elements) != 0:
            link_to_elements[link] = elements

    return link_to_elements
