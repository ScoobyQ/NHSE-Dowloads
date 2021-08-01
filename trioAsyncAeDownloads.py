# Authors:
# 1) qharr          https://stackoverflow.com/users/6241235


import re
import httpx
import trio
from bs4 import BeautifulSoup
import arrow
from platform import system
import os


REVISIONS = True # User amends

CURR_PERIOD, REV_START, REV_END = ['Apr21', "Apr20", "Mar21"] # User amends


BLOCK = ['timeseries']
WINDOWS = False

PROVCOMM_LINKS = [
    'https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/']


def get_os() -> str:
    syst = system()
    if syst.startswith('L'):
        return '~/Ae'
    elif syst.startswith('W'):
        global WINDOWS
        WINDOWS = True
        return '~/Desktop/Ae'  # Assume no Onedrive on path
    else:
        exit('Please Modify The Path Manually')


SYSP = get_os()
FOLDER_PATH = os.path.expanduser(SYSP)

def logic() -> str:
    month_list = [i.format('MMMM-YYYY') for i in list(arrow.Arrow.range(
        'month',  arrow.get(REV_START, 'MMMYY'),  arrow.get(REV_END, 'MMMYY')))]

    prefix = arrow.get(CURR_PERIOD, "MMMYY").shift(
        months=+1).format("YYYY/MM")

    suffix = '.*(?:-revised-)'

    if REVISIONS:
        # revision files should have the year month of CURR_PERIOD ( + 1 month due to delay between data for and reporting date) in the url as an assumption e.g. 2021/06

        return "|".join(
            [f'{prefix}/(?:Quarter-)?.*-AE-.*(?:-{arrow.get(CURR_PERIOD, "MMMYY").format("MMMM-YYYY")})?', '{}/.*({}){}'.format(prefix, "|".join(month_list), suffix)])  # create the regex expression used to match urls on website.

    return f'{prefix}/(?:Quarter-)?.*-AE-.*(?:-{arrow.get(CURR_PERIOD, "MMMYY").format("MMMM-YYYY")})?'


async def get_soup(content):
    return BeautifulSoup(content, 'lxml')


async def downloader(url):
    async with httpx.AsyncClient(http2=True, timeout=None) as client:

        curr = (arrow.get(CURR_PERIOD, "MMMYY").format("MMMM-YYYY") in url)

        if curr:
            file_name = url.rsplit('/', 1)[-1]

        else:
            suffix = 'Rev ' + arrow.utcnow().format('DDMMYYYY')
            file_name = f' {suffix}.'.join(url.rsplit('/', 1)[-1].rsplit('.'))

        r = await client.get(url)

        # print(url)
        # print(f"{FOLDER_PATH}/{file_name}")

        async with await trio.open_file(f"{FOLDER_PATH}/{file_name}", 'wb') as f:
            await f.write(r.content)
            print(f'Downloaded {file_name}')


async def get_download_links(link, nurse):
    async with httpx.AsyncClient(http2=True, timeout=None) as client:
        r = await client.get(link)
        soup = await get_soup(r.text)
        match = (x['href'] for x in soup.findAll('a', href=re.compile(set_logic, re.I))
                 if not any(i in x['href'].lower() for i in BLOCK))

        if match:
            for i in match:
                nurse.start_soon(downloader, i)

set_logic = logic()


async def get_links(url, nurse):
    async with httpx.AsyncClient(http2=True, timeout=None) as client:
        r = await client.get(url)
        soup = await get_soup(r.text)
        # Currently limit restricts to last 3 financial years.
        for x in soup.select('p > [href*=ae-attendances-and-emergency-admissions-]', limit=3):
            nurse.start_soon(get_download_links, x['href'], nurse)


async def main():
    async with trio.open_nursery() as nurse:
        for link in PROVCOMM_LINKS:
            nurse.start_soon(get_links, link, nurse)


if __name__ == "__main__":

    if not os.path.exists(FOLDER_PATH):
        os.makedirs(FOLDER_PATH)

    try:
        trio.run(main)
        if WINDOWS:
            os.startfile(FOLDER_PATH)
    except KeyboardInterrupt:
        exit('Bye!')
