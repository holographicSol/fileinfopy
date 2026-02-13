""" Written by Benjamin Jack Cullen """
import os
import time
import datetime
import bs4
import colorama
import codecs
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import re

colorama.init()

# set master timeout
master_timeout = 86400  # 24h

# set scraper timeout/connection-issue retry time intervals
timeout_retry = 2
connection_error_retry = 10
server_disconnected_error_retry = 10

# configure options for scraping
scrape_timeout = aiohttp.ClientTimeout(
    total=None,  # default value is 5 minutes, set to `None` for unlimited timeout
    sock_connect=master_timeout,  # How long to wait before an open socket allowed to connect
    sock_read=master_timeout  # How long to wait with no data being read before timing out
)
client_args = dict(
    trust_env=True,
    timeout=scrape_timeout
)

# configure options for downloading files
download_timeout = aiohttp.ClientTimeout(
    total=None,  # default value is 5 minutes, set to `None` for unlimited timeout
    sock_connect=master_timeout,  # How long to wait before an open socket allowed to connect
    sock_read=master_timeout  # How long to wait with no data being read before timing out
)
client_args_download = dict(
    trust_env=True,
    timeout=download_timeout
)


# return headers with a random user agent
def user_agent():
    ua = UserAgent()
    return {'User-Agent': str(ua.random)}


def color(s: str, c: str) -> str:
    """ color print """
    if c == 'W':
        return colorama.Style.BRIGHT + colorama.Fore.WHITE + str(s) + colorama.Style.RESET_ALL
    elif c == 'LM':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTMAGENTA_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'M':
        return colorama.Style.BRIGHT + colorama.Fore.MAGENTA + str(s) + colorama.Style.RESET_ALL
    elif c == 'LC':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'B':
        return colorama.Style.BRIGHT + colorama.Fore.BLUE + str(s) + colorama.Style.RESET_ALL
    elif c == 'LG':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTGREEN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'G':
        return colorama.Style.BRIGHT + colorama.Fore.GREEN + str(s) + colorama.Style.RESET_ALL
    elif c == 'Y':
        return colorama.Style.BRIGHT + colorama.Fore.YELLOW + str(s) + colorama.Style.RESET_ALL
    elif c == 'R':
        return colorama.Style.BRIGHT + colorama.Fore.RED + str(s) + colorama.Style.RESET_ALL


def get_dt() -> str:
    """ formatted datetime string for tagging output """
    return color(str('[' + str(datetime.datetime.now()) + ']'), c='W')


def get_soup(_body: str) -> bs4.BeautifulSoup:
    """ return soup """
    return BeautifulSoup(_body, 'html.parser')


def parse_soup_phase_one(_soup: bs4.BeautifulSoup) -> list:
    """ parse soup from phase one (parse for book URLs) """
    _data = []
    check_0 = ['/filetypes/']
    for link in _soup.find_all('a'):
        href = str(link.get('href')).strip()
        if href != '/filetypes/':
            if href.startswith(tuple(check_0)):
                if href == '/filetypes/data':
                    _data.append(['https://fileinfo.com/' + href])
                else:
                    _data.append(['https://fileinfo.com/'+href+'-all'])
    return _data


def parse_soup_phase_two(_soup: bs4.BeautifulSoup, _title: str) -> list:
    """ parse soup from phase one (parse for book URLs) """

    _title = _title.replace('-all', '')
    # _title = make_title(_title)
    _title = _title + '_' + 'files'
    _data = [[_title]]
    try:
        htnm_migration_table = _soup.find("table", {'class':'list sortable filetypes'})
        tbody = htnm_migration_table.find('tbody')
        trs = tbody.find_all('tr')
        for tr in trs:
            _extension = [_title.replace('-all', '')]
            try:
                tds = tr.find_all('td')
                for td in tds:
                    _extension.append(td.text)
                _data.append(_extension)
            except:
                pass
    except:
        pass

    if len(_data) > 1:
        return _data
    else:
        print('came up empty:', _title)


def parse_soup_phase_three(_soup: bs4.BeautifulSoup, _data_list: list) -> list:
    """ parse soup from phase one (parse for book URLs) """

    _desc = ''
    for row in _soup.find_all('p'):
        text = row.getText()
        if 'FileInfo.com' not in text:
            text = str(text).strip().replace('If you would like to suggest any additions or updates to this page, please let us know.', '')
            _desc += text.strip('\r\n')
    if _desc not in _data_list:
        _data_list.append(_desc)
        # print(_data_list)

    return _data_list


async def scrape(url: str, parse_soup: int, _title='', _data_list=[]) -> list:
    """ scrape for book URLs """
    _data = []
    tm = 5
    try:
        _headers = user_agent()
        async with aiohttp.ClientSession(headers=_headers, **client_args) as session:
            async with session.get(url) as resp:
                _body = await resp.text(encoding='utf8', errors='ignore')
                _soup = await asyncio.to_thread(get_soup, _body=_body)
                if parse_soup == int(0):
                    _data = await asyncio.to_thread(parse_soup_phase_one, _soup=_soup)
                elif parse_soup == int(1):
                    _data = await asyncio.to_thread(parse_soup_phase_two, _soup=_soup, _title=_title)
                elif parse_soup == int(2):
                    _data = await asyncio.to_thread(parse_soup_phase_three, _soup=_soup, _data_list=_data_list)

                    if _data is not None:
                        print(_data)
                        if len(_data) == 4:
                            print(f'{get_dt()} ' + color(f'[COMPLETE]', c='G'))
                            return _data
                        else:
                            print(f'{get_dt()} ' + color(f'[EMPTY DESCRIPTION] Retrying in {tm} seconds.', c='Y'))
                            await asyncio.sleep(tm)
                            await scrape(url=url, parse_soup=parse_soup, _title=_title, _data_list=_data_list)
                    else:
                        print(f'{get_dt()} ' + color(f'[NONE] Retrying in {tm} seconds.', c='Y'))
                        await asyncio.sleep(tm)
                        await scrape(url=url, parse_soup=parse_soup, _title=_title, _data_list=_data_list)

    except asyncio.exceptions.TimeoutError:
        print(f'{get_dt()} ' + color(f'[TIMEOUT] Retrying in {tm} seconds.', c='Y'))
        await asyncio.sleep(tm)
        await scrape(url=url, parse_soup=parse_soup, _title=_title, _data_list=_data_list)

    except aiohttp.ClientConnectorError:
        print(f'{get_dt()} ' + color(f'[CONNECTION ERROR] Retrying in {tm} seconds.', c='Y'))
        await asyncio.sleep(tm)
        await scrape(url=url, parse_soup=parse_soup, _title=_title, _data_list=_data_list)

    except aiohttp.ServerDisconnectedError:
        print(f'{get_dt()} ' + color(f'[SERVER DISCONNECTED ERROR] Retrying in {tm} seconds.', c='Y'))
        await asyncio.sleep(tm)
        await scrape(url=url, parse_soup=parse_soup, _title=_title, _data_list=_data_list)

    except aiohttp.ClientOSError:
        print(f'{get_dt()} ' + color(f'[CLIENT OS ERROR] Retrying in {tm} seconds.', c='Y'))
        await asyncio.sleep(tm)
        await scrape(url=url, parse_soup=parse_soup, _title=_title, _data_list=_data_list)

    except aiohttp.ClientPayloadError:
        print(f'{get_dt()} ' + color(f'[CLIENT PAYLOAD ERROR] Retrying in {tm} seconds.', c='Y'))
        await asyncio.sleep(tm)
        await scrape(url=url, parse_soup=parse_soup, _title=_title, _data_list=_data_list)

    return _data


def synchro_scrape(url, sub_result, title, i_sub_result, _len_result):
    tm = 5
    try:
        # synchronous scrape
        print(f'[SCANNING] [{str(title)}] {str(url)} ({str(i_sub_result)}/{str(_len_result)})')

        rHead = requests.get(url)
        data = rHead.text
        _soup = BeautifulSoup(data, "html.parser")
        _desc = ''
        _software = ''
        _formats = ''

        for row in _soup.find_all('div', {'class': 'infoBox'}):

            # uncomment to see all rows and text
            # print(f'row: {row}')
            # print(f'text: {row.getText()}')

            # eliminate related software
            if '<li> <a href="/software/' in str(row):
                pass

            # parse for related software to convert to other formats
            if '<li> <a href="/extension/' in str(row):
                text = row.getText()
                text = re.sub('\s+', ' ', text)
                _formats += text.strip('\r\n').strip('\n').strip('\r')
            else:
                # parse for description
                text = row.getText()
                text = re.sub('\s+', ' ', text)
                _desc += text.strip('\r\n').strip('\n').strip('\r')

        # parse for related software
        for row in _soup.find_all('div', {'class': 'programs'}):
            text = row.getText()
            text = re.sub('\s+', ' ', text)
            _software += text.strip('\r\n').strip('\n').strip('\r')

        # clean up description text
        if _desc not in sub_result:
            if not _desc.endswith('.') and _desc != '':
                if _desc.endswith(' '):
                    _desc = _desc[1:]
                _desc += '.'
                _desc = _desc.replace('  ', '. ')
                _desc = _desc.replace(' .', '.')
                _desc = _desc.replace('DiscontinuedPaid', ' (Discontinued).')
                _desc = _desc.replace('DiscontinuedFree', ' (Discontinued).')
                _desc = _desc.replace('DiscontinuedIncluded', ' (Discontinued) Included')
                _desc = _desc.replace('Included with OS', ' Included with OS.')
                _desc = _desc.replace('Free+', '.')
                _desc = _desc.replace('Free Trial', '.')
                _desc = _desc.replace('Free ', '. ')
                _software = _software.replace('Free.', '.')
                _desc = _desc.replace('Paid', '.')
                _desc = _desc.replace(' .', '.')
                _desc = _desc.replace('..', '.')
            elif _desc == '':
                _desc = '?'
            sub_result.append(_desc)

        # clean up software text
        if _software not in sub_result:
            if not _software.endswith('.') and _software != '':
                if _software.endswith(' '):
                    _software = _software[1:]
                _software += '.'
                _software = _software.replace('  ', '. ')
                _software = _software.replace(' .', '.')
                _software = _software.replace('DiscontinuedPaid', ' (Discontinued).')
                _software = _software.replace('DiscontinuedFree', ' (Discontinued).')
                _software = _software.replace('DiscontinuedIncluded', ' (Discontinued) Included')
                _software = _software.replace('Included with OS', ' Included with OS.')
                _software = _software.replace('Free+', '.')
                _software = _software.replace('Free Trial', '.')
                _software = _software.replace('Free ', '. ')
                _software = _software.replace('Free.', '.')
                _software = _software.replace('Paid', '.')
                _software = _software.replace(' .', '.')
                _software = _software.replace('..', '.')
            elif _software == '':
                _software = '?'
            sub_result.append(_software)

        # clean up convert to other formats text
        if _formats not in sub_result:
            if not _formats.endswith('.') and _formats != '':
                if _formats.endswith(' '):
                    _formats = _formats[1:]
                _formats += '.'
                _formats = _formats.replace('  ', '. ')
                _formats = _formats.replace(' .', '.')
                _formats = _formats.replace('DiscontinuedPaid', ' (Discontinued).')
                _formats = _formats.replace('DiscontinuedFree', ' (Discontinued).')
                _formats = _formats.replace('DiscontinuedIncluded', ' (Discontinued) Included')
                _formats = _formats.replace('Included with OS', ' Included with OS.')
                _formats = _formats.replace('Free+', '.')
                _formats = _formats.replace('Free Trial', '.')
                _formats = _formats.replace('Free ', '. ')
                _formats = _formats.replace('Free.', '.')
                _formats = _formats.replace('Paid', '.')
                _formats = _formats.replace(' .', '.')
                _formats = _formats.replace('..', '.')
            elif _formats == '':
                _formats = '?'
            sub_result.append(_formats)

        return sub_result

    except requests.ConnectTimeout:
        print(f'{get_dt()} ' + color(f'[ConnectTimeout] Retrying in {tm} seconds.', c='Y'))
        time.sleep(tm)
        synchro_scrape(url, sub_result, title, i_sub_result, _len_result)

    except requests.ConnectionError:
        print(f'{get_dt()} ' + color(f'[ConnectionError] Retrying in {tm} seconds.', c='Y'))
        time.sleep(tm)
        synchro_scrape(url, sub_result, title, i_sub_result, _len_result)

    except requests.ReadTimeout:
        print(f'{get_dt()} ' + color(f'[ReadTimeout] Retrying in {tm} seconds.', c='Y'))
        time.sleep(tm)
        synchro_scrape(url, sub_result, title, i_sub_result, _len_result)


async def main():

    # create URL to scrape
    url = 'https://fileinfo.com/filetypes/common'
    print(f'{get_dt()} ' + color('[Scanning] ', c='LC') + color(f'{url}', c='W'))
    print(f'{get_dt()} ' + color('[Phase One] ', c='LC') + f'Gathering initial links...')

    # get links
    tasks = []
    t0 = time.perf_counter()
    task = asyncio.create_task(scrape(url, parse_soup=int(0)))
    tasks.append(task)
    results_0 = await asyncio.gather(*tasks)
    print(f'{get_dt()} ' + color('[Results] ', c='Y') + color(str(results_0), c='LC'))
    for result in results_0:
        if result is None:
            del result
    results_0[:] = [item for sublist in results_0 for item in sublist if item is not None]
    print(f'{get_dt()} ' + color('[Results Formatted] ', c='Y') + color(str(results_0), c='LC'))
    print(f'{get_dt()} ' + color('[Results] ', c='Y') + f'{len(results_0)}')
    print(f'{get_dt()} ' + color('[Phase One Time] ', c='LC') + f'{time.perf_counter() - t0}')

    # scrape data
    tasks = []
    t0 = time.perf_counter()
    for result in results_0:
        idx_result = result[0].rfind('/')
        title = result[0][idx_result+1:]
        task = asyncio.create_task(scrape(result[0], parse_soup=int(1), _title=title))
        tasks.append(task)
    results_1 = await asyncio.gather(*tasks)
    print(f'{get_dt()} ' + color('[Results] ', c='Y') + color(str(results_1), c='LC'))
    for result in results_1:
        if result is None:
            del result
    print(f'{get_dt()} ' + color('[Results Formatted] ', c='Y') + color(str(results_1), c='LC'))
    print(f'{get_dt()} ' + color('[Results] ', c='Y') + f'{len(results_1)}')
    print(f'{get_dt()} ' + color('[Phase Two Time] ', c='LC') + f'{time.perf_counter() - t0}')

    _USER_PROMPT = False

    # scrape description
    for result in results_1:

        # skip title in list
        if len(result) > 1:

            title = result[0][0].replace(".", "")

            if _USER_PROMPT is True:
                inpt = input(f'create module: {title} (existing module will be overwritten if it exists)? ')
            else:
                inpt = 'Y'

            if inpt == 'y' or inpt == 'Y':

                # create module entry: read the module
                _import_list = []
                _other_list = []
                with codecs.open('./fileinfopy.py', 'r+', encoding='utf8') as fo:
                    for line in fo:
                        line = line.strip()
                        if line.startswith('import'):
                            if line not in _import_list:
                                _import_list.append(line)
                        else:
                            if line not in _other_list:
                                _other_list.append(line)
                fo.close()

                # create module entry: check line existence
                write_bool = False
                if f'import fileinfopy_{title}' not in _import_list:
                    _import_list.append(f'import fileinfopy_{title}')
                    write_bool = True

                # create module entry: check line existence
                if f'{title} = fileinfopy_{title}.{title}' not in _other_list:
                    _other_list.append(f'{title} = fileinfopy_{title}.{title}')
                    if title == '3d_image_files':
                        _other_list.append(f'three_d_image_files = fileinfopy_{title}.three_d_image_files')
                    else:
                        _other_list.append(f'{title} = fileinfopy_{title}.{title}')
                    write_bool = True

                # create module entry: write new module
                if write_bool is True:
                    # create module entry: display
                    print(f'{str(get_dt())} ' + str(color(f'[ADDING NEW MODULE IMPORTS AND PLUGS]', c='G')))
                    _import_list.sort(reverse=False)
                    _other_list.sort(reverse=False)
                    with codecs.open('./fileinfopy.py', 'w+', encoding='utf8') as fo:
                        fo.write('""" Written programmatically by Benjamin Jack Cullen """\n\n')
                        for _line in _import_list:
                            fo.write(_line+'\n')
                        fo.write('\n')
                        for _line in _other_list:
                            fo.write(_line+'\n')
                    fo.close()

                # create data module: make filename
                _filename = f'./fileinfopy_{title}.py'

                # create data module: initiate python list
                print(f'{str(get_dt())} ' + str(color(f'[CREATING PYTHONIC LIST]', c='G')))
                with codecs.open(_filename, 'w+', encoding='utf8') as fo:
                    fo.write('""" Written programmatically by Benjamin Jack Cullen """\n\n')
                    fo.write('""" Source and credits to: https://fileinfo.com/ """\n\n')
                    # variable name
                    if title == '3d_image_files':
                        fo.write('three_d_image_files = [\n')
                    else:
                        fo.write(f'{title} = [\n')
                fo.close()

                # create data module: synchronously scrape for descriptions
                i_sub_result = 0
                _len_result = len(result)
                for sub_result in result:
                    if len(sub_result) > 2:
                        i_sub_result += 1

                        url = 'https://fileinfo.com/extension/' + sub_result[1].replace('.', '')
                        synchro_scrape(url, sub_result, result[0][0], i_sub_result, _len_result)

                        # create data module: append list to list
                        try:
                            with codecs.open(_filename, 'a+', encoding='utf8') as fo:
                                if len(sub_result) == 7:
                                    fo.write(f'    ["'+sub_result[0].replace(".", "") + '",\n')
                                    # item 1
                                    fo.write('    "'+str(sub_result[1].replace("'", "").replace('"', '').replace('\r\n', ' ').replace('\n', ' ').replace('\\', '/'))+'",\n')
                                    # item 2
                                    fo.write('    "'+str(sub_result[2].replace("'", "").replace('"', '').replace('\r\n', ' ').replace('\n', ' ').replace('\\', '/'))+'",\n')
                                    # item 3
                                    fo.write('    "'+str(sub_result[3].replace("'", "").replace('"', '').replace('\r\n', ' ').replace('\n', ' ').replace('\\', '/'))+'",\n')                         # item 3
                                    # item 4
                                    fo.write('    "'+str(sub_result[4].replace("'", "").replace('"', '').replace('\r\n', ' ').replace('\n', ' ').replace('\\', '/'))+'",\n')
                                    # item 5
                                    fo.write('    "'+str(sub_result[5].replace("'", "").replace('"', '').replace('\r\n', ' ').replace('\n', ' ').replace('\\', '/'))+'",\n')                         # item 3
                                    # item 6
                                    fo.write('    "'+str(sub_result[6].replace("'", "").replace('"', '').replace('\r\n', ' ').replace('\n', ' ').replace('\\', '/'))+'"],\n')
                            fo.close()

                        except Exception as e:
                            print(e)

                # create data module: close the type list
                with codecs.open(_filename, 'a+', encoding='utf8') as fo:
                    fo.write(']\n\n')
                fo.close()

            # create data module: skip this module
            else:
                print(f'skipping: {title}')

asyncio.run(main())
