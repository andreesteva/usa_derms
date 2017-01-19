"""Crawls AAD site for all derms, collecting who exists at what location."""

import urllib2
import requests
import random
import os


PROXIES = [line.strip() for line in open("./proxy_list.txt").readlines()]
USER_AGENTS_FILE="user_agents.txt"
RADIUS = 5 #miles

def readfile(filename):
    return [line.strip() for line in open(filename).readlines()]


def crawl_url(zipcode):
    return "https://www.aad.org/find-a-derm?location=%s&specialty=&lastname=" % zipcode


def save_progress(filename, derm_counts):
    """Saves the derm_counts into filename"""

    with open(filename, 'w') as f:
        f.write("zipcode,derms_within_%d_miles\n" % RADIUS)
        prefix = ""
        for key, val in derm_counts.iteritems():
            f.write(prefix)
            f.write(key)
            f.write(',')
            f.write(val)
            prefix= "\n"


def LoadUserAgents(uafile=USER_AGENTS_FILE):
    """
    uafile : string
        path to text file of user agents, one per line
    """
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1-1])
    random.shuffle(uas)
    return uas


def proxy_retrieve_page(zipcode):
    save_filename = "./html_pages/%s.html" % zipcode
    if os.path.exists(save_filename):
        html = [line.strip() for line in open(save_filename).readlines()]
        return html
    proxy = {"http" : "http://" + random.choice(PROXIES)}
#   params = {"q" : "London,uk"}
    url = crawl_url(zipcode)
    ua = random.choice(USER_AGENTS)
    headers = {
            "Connection" : "close",
            "User-Agent" : ua}
#   r = requests.get(url, proxies=proxy, params=params, headers=headers)
    r = requests.get(url, proxies=proxy, headers=headers)
    html = r.text
    html = html.split("\n")
    with open(save_filename, 'w') as f:
        for line in html:
            f.write(line.encode('utf-8'))
            f.write("\n")
    return html


# def retrieve_page(zipcode):
#     save_filename = "./html_pages/%s.html" % zipcode
#     if os.path.exists(save_filename):
#         html = [line.strip() for line in open(save_filename).readlines()]
#         return html
#     url = crawl_url(zipcode)
#     response = urllib2.urlopen(url)
#     html = response.read()
#     html = html.split("\n")
#     with open(save_filename, 'w') as f:
#         for line in html:
#             f.write(line)
#             f.write("\n")
#     return html


zipcodes = readfile('./zipcodes.txt')
derm_counts = {}
USER_AGENTS=LoadUserAgents(USER_AGENTS_FILE)


for i, zipcode in enumerate(zipcodes):

    html = proxy_retrieve_page(zipcode)

    derms = []
    for j, line in enumerate(html):
        if '/find-a-derm/' in line:
            if float(html[j-4].split(">")[1].split("<")[0]) < RADIUS:
                derms.append(line)

    derm_counts[zipcode] = str(len(derms))
    print "Crawling %s, %d/%d, N_derms=%d" % (zipcode, i, len(zipcodes), len(derms))

    if i % 10 == 0:
        save_progress('./results/derm_counts_%d.txt' % i, derm_counts)

save_progress('./derm_counts.txt', derm_counts)
