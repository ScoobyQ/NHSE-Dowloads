## Authors: 
## 1) αԋɱҽԃ-αмєяιcαη https://stackoverflow.com/users/7658985
## 2) qharr          https://stackoverflow.com/users/6241235

import trio
import httpx
from bs4 import BeautifulSoup
import re
import arrow
from platform import system
import os

curr_period, rev_start, rev_end = ['May21', "Apr19", "Aug19"]  # user amend

revisions = True  # user amend

FOLDER_PATH = ''

month_list = [i.format('MMMYY') for i in list(arrow.Arrow.range(
    'month',  arrow.get(rev_start, 'MMMYY'),  arrow.get(rev_end, 'MMMYY')))]

main_url = "https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/"

if revisions:
    lookup = "|".join(
        ['-' + curr_period, '({}).*revised'.format("|".join(month_list))])  # create the regex expression used to match urls on website.
else:
    lookup = '-' + curr_period

# list of words to use for filtering out urls retrieved in all_links
block = ['timeseries', 'waiting']


def get_os():
    syst = system()
    if syst.startswith('L'):
        return '~/Rtt'
    elif syst.startswith('W'):
        return '~/Desktop/Rtt'  # May experience issues for Windows users with OneDrive on path
    else:
        exit('Please Modify The Path Manually')


sysp = get_os()


async def get_soup(content):
    return BeautifulSoup(content, 'lxml')


async def get_links(client):
    r = await client.get(main_url)
    soup = await get_soup(r.text)
    # Alter 3 to change the number of years to consider.
    return [x['href'] for x in soup.select('a[href*=rtt-data]', limit=3)]

all_links = []


async def get_download_links(client, link):
    r = await client.get(link)
    soup = await get_soup(r.text)
    match = (x['href'] for x in soup.findAll('a', href=re.compile(lookup, re.I))
             if not any(i in x['href'].lower() for i in block))

    if match:
        all_links.extend(match)


async def downloader(channel, folder_path):
    async with channel:
        async for client, target in channel:
            file_name = target.rsplit('/', 1)[-1]
            r = await client.get(target)

            async with await trio.open_file(f"{folder_path}/{file_name}", 'wb') as f:
                await f.write(r.content)
                print(f'Downloaded {file_name}')


async def main():
    async with httpx.AsyncClient(timeout=None) as client, trio.open_nursery() as nurse:
        links = await get_links(client)

        for link in links:
            nurse.start_soon(get_download_links, client, link)

    async with httpx.AsyncClient(timeout=None) as client2, trio.open_nursery() as nurse2:
        sender, receiver = trio.open_memory_channel(0)

        folder_path = await trio.Path(sysp).expanduser()

        global FOLDER_PATH
        FOLDER_PATH = folder_path

        await folder_path.mkdir(exist_ok=True)

        async with receiver:
            # alter n in range for speed. Up to 100 if network speed is very good.
            for _ in range(100):
                nurse2.start_soon(downloader, receiver.clone(), folder_path)

            async with sender:
                for i in all_links:
                    await sender.send([client2, i])


if __name__ == "__main__":
    try:
        trio.run(main)
        os.startfile(FOLDER_PATH)
    except KeyboardInterrupt:
        exit('Bye')
