import re
import httpx
import trio
from bs4 import BeautifulSoup
import arrow
from platform import system
import os


CURR_PERIOD, REV_START, REV_END = ['May21', "Apr20", "Apr20"] #User amends
REVISIONS = True #User amends

#Start urls for crawling
PROVCOMM_LINKS = [
    'https://www.england.nhs.uk/statistics/monthly-prov-cwt',
    'https://www.england.nhs.uk/statistics/monthly-comm-cwt'
]

BLOCK = ['timeseries', 'homepage'] #Word based exclusions from any retrieved urls.

WINDOWS = False


def get_os():
    syst = system()
    if syst.startswith('L'):
        return '~/Cwt'
    elif syst.startswith('W'):
        global WINDOWS
        WINDOWS = True
        return '~/OneDrive/Desktop/Cwt'  # Remove /OneDrive
    else:
        exit('Please Modify The Path Manually')


SYSP = get_os()
FOLDER_PATH = os.path.expanduser(SYSP) #Note make have issues for users with Onedrive on path with Windows.

def logic():
    month_list = [i.format('MMMM-YYYY').lower() for i in list(arrow.Arrow.range(
        'month',  arrow.get(REV_START, 'MMMYY'),  arrow.get(REV_END, 'MMMYY')))]

    if REVISIONS:
        return "|".join(
            [f'-{arrow.get(CURR_PERIOD, "MMMYY").format("MMMM-YYYY").lower()}.*provisional', '({}).*final'.format("|".join(month_list))])  # create the regex expression used to match urls on website.

    return f'-{arrow.get(CURR_PERIOD, "MMMYY").format("MMMM-YYYY").lower()}.*provisional'


async def get_soup(content):
    return BeautifulSoup(content, 'lxml')

DATE_BY_LINK = {}


async def downloader(url):
    async with httpx.AsyncClient(timeout=None) as client:
        period = DATE_BY_LINK[url]

        if period != CURR_PERIOD:
            suffix = ' Rev ' + arrow.utcnow().format('DDMMYYYY')
            file_name = url.rsplit('/', 1)[-1]
            file_name = f'{period} ' + f' {suffix}.'.join(
                file_name.rsplit('/', 1)[-1].rsplit('.', 1))  # Period put at front to group files for revisions
        else:
            file_name = url.rsplit('/', 1)[-1]

        r = await client.get(url)
        async with await trio.open_file(f"{FOLDER_PATH}/{file_name}", 'wb') as f:
            await f.write(r.content)
            print(f'Downloaded {file_name}')


async def get_date_from_url(link: str) -> str:
    match = re.match(r'.*-for-(?P<month>[a-z]{3,9})-(?P<year>\d{4}).*', link)
    date = arrow.get(
        ' '.join([match.group('month'), match.group('year')]), 'MMMM YYYY')
    return date.format('MMMYY')


async def get_download_links(link, nurse):
    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.get(link)
        soup = await get_soup(r.text)
        match = (x['href'] for x in soup.select('#main-content > article a')
                 if not any(i in x['href'].lower() for i in BLOCK))

        period = await get_date_from_url(link)
        if match:
            for i in match:
                DATE_BY_LINK[i] = period
                nurse.start_soon(downloader, i)

set_logic = logic()


async def get_month_links(link, nurse):
    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.get(link)
        soup = await get_soup(r.text)
        match = (x['href'] for x in soup.findAll('a', href=re.compile(set_logic, re.I))
                 if not any(i in x['href'].lower() for i in BLOCK))
        if match:
            for i in match:
                nurse.start_soon(get_download_links, i, nurse)


async def get_links(url, nurse):
    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.get(url)
        soup = await get_soup(r.text)
        for x in soup.select('h3:-soup-contains("Latest statistics") + p > a', limit=3):
            nurse.start_soon(get_month_links, x['href'], nurse)


async def main():
    async with trio.open_nursery() as nurse:
        for link in PROVCOMM_LINKS:
            nurse.start_soon(get_links, link, nurse)


if __name__ == "__main__":
    try:
        trio.run(main)
        if WINDOWS:
            os.startfile(FOLDER_PATH)
    except KeyboardInterrupt:
        exit('Bye!')
