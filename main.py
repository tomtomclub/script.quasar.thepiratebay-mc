# coding: utf-8
__author__ = 'mancuniancol'

import common
from bs4 import BeautifulSoup
from quasar import provider

# this read the settings
settings = common.Settings()
# define the browser
browser = common.Browser()
# create the filters
filters = common.Filtering()


# using function from Steeve to add Provider's name and search torrent
def extract_torrents(data):
    try:
        filters.information()  # print filters settings
        soup = BeautifulSoup(data, 'html5lib')
        links = soup.table.tbody.findAll('tr')
        cont = 0
        results = []
        for link in links:
            try:
                columns = link.findAll('td')
                name = columns[1].div.text  # name
                magnet = columns[1].select('div + a')[0]["href"]  # magnet
                size = columns[1].font.text.split(',')[1].replace('Size', '').replace('&nbsp;', ' ')  # size
                seeds = columns[2].text  # seeds
                peers = columns[3].text  # peers
                size = common.Filtering.normalize(size)
                # info_magnet = common.Magnet(magnet)
                if filters.verify(name, size):
                    cont += 1
                    results.append({"name": name.strip(),
                                    "uri": magnet,
                                    # "info_hash": info_magnet.hash,
                                    "size": size.strip(),
                                    "seeds": int(seeds),
                                    "peers": int(peers),
                                    "language": settings.value.get("language", "en"),
                                    "provider": settings.name
                                    })  # return the torrent
                    if cont >= int(settings.value.get("max_magnets", 10)):  # limit magnets
                        break
                else:
                    provider.log.warning(filters.reason)
            except:
                continue
        provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Quasar<<<<<<<')
        return results
    except:
        provider.log.error('>>>>>>>ERROR parsing data<<<<<<<')
        provider.notify(message='ERROR parsing data', header=None, time=5000, image=settings.icon)
        return []


def search(query):
    info = {"query": query,
            "type": "general"}
    return search_general(info)


def search_general(info):
    info["extra"] = settings.value.get("extra", "")  # add the extra information
    query = filters.type_filtering(info, '+')  # check type filter and set-up filters.title
    url_search = "%s/search/%s/0/99/200" % (settings.value["url_address"], query)
    provider.log.info(url_search)
    if browser.open(url_search):
        results = extract_torrents(browser.content)
    else:
        provider.log.error('>>>>>>>%s<<<<<<<' % browser.status)
        provider.notify(message=browser.status, header=None, time=5000, image=settings.icon)
        results = []
    return results


def search_movie(info):
    info["type"] = "movie"
    if settings.value.get("language", "en") == 'en':  # Title in english
        query = info['title'].encode('utf-8')  # convert from unicode
        if len(info['title']) == len(query):  # it is a english title
            query += ' ' + str(info['year'])  # Title + year
        else:
            query = common.IMDB_title(info['imdb_id'])  # Title + year
    else:  # Title en foreign language
        query = common.translator(info['imdb_id'], settings.value["language"])  # Just title
    info["query"] = query
    return search_general(info)


def search_episode(info):
    if info['absolute_number'] == 0:
        info["type"] = "show"
        info["query"] = info['title'].encode('utf-8') + ' s%02de%02d' % (
            info['season'], info['episode'])  # define query
    else:
        info["type"] = "anime"
        info["query"] = info['title'].encode('utf-8') + ' %02d' % info['absolute_number']  # define query anime
    return search_general(info)


# This registers your module for use
provider.register(search, search_movie, search_episode)

del settings
del browser
del filters
