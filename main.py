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


def extract_torrents(data):
    filters.information()  # print filters settings
    sint = common.ignore_exception(ValueError)(int)
    results = []
    cont = 0
    if data is not None:
        soup = BeautifulSoup(data, 'html5lib')
        try:
            links = soup.table.tbody.findAll('tr')
        except:
            links = []
        for link in links:
            columns = link.findAll('td')
            if len(columns) == 4:
                name = columns[1].div.text.strip()  # name
                magnet = columns[1].select('div + a')[0]["href"]  # magnet
                size = columns[1].font.text.split(',')[1].replace('Size', '').replace('&nbsp;', ' ')  # size
                size = common.Filtering.normalize(size).strip()
                seeds = columns[2].text  # seeds
                peers = columns[3].text  # peers
                # info_magnet = common.Magnet(magnet)
                if filters.verify(name, size):
                    cont += 1
                    # magnet = common.getlinks(magnet)
                    results.append({"name": name,
                                    "uri": magnet,
                                    # "info_hash": info_magnet.hash,
                                    "size": size,
                                    "seeds": sint(seeds),
                                    "peers": sint(peers),
                                    "language": settings.value.get("language", "en"),
                                    "provider": settings.name,
                                    "icon": settings.icon,
                                    })  # return the torrent
                    if cont >= int(settings.value.get("max_magnets", 10)):  # limit magnets
                        break
                else:
                    provider.log.warning(filters.reason)
    provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Quasar<<<<<<<')
    return results


def search(query):
    info = {"query": query,
            "type": "general"}
    return search_general(info)


def search_general(info):
    info["extra"] = settings.value.get("extra", "")  # add the extra information
    query = filters.type_filtering(info, '+')  # check type filter and set-up filters.title
    url_search = "%s/search/%s/0/99/200" % (settings.value["url_address"], query)
    provider.log.info(url_search)
    browser.open(url_search)
    return extract_torrents(browser.content)


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


def search_season(info):
    provider.log.info(info)
    info["type"] = "show"
    info["query"] = info['title'].encode('utf-8') + ' %s %s' % (
        common.season_names[settings.value.get("language", "en")], info['season'])  # define query
    return search_general(info)


# This registers your module for use
if "false" == settings.value.get("episodes", "false"):
    provider.register(search, search_movie, search_episode, search_season)
else:
    provider.register(search, search_movie, search_season, search_season)

del settings
del browser
del filters
