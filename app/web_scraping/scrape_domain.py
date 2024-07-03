from web_scraping.dns_resolver import find_all_subdomains
from web_scraping.apify_page_count import get_content

from settings.settings import Settings
settings = Settings()

URL_DOMAIN = "ucf.edu"

exclusion_list = [
"events",
"sciences",
"www",
"guides",
"library",
"business",
"nursing",
"provost",
"compliance",
"www.research",
"it",
"physics",
"registrar",
"jobs",
"global",
"stem",
"honors",
"hr",
"parking",
"police",
"www.police",
"communication",
"access",
"cdl",
"stars.library",
"libanswers",
"risk",
"caps.sdes",
"publications.energyresearch",
"calendar",
"richesmi.cah",
"cah",
"smokefree.sdes",
"go.giving",
"bot",
"arts.cah",
"www.emergency",
"www.ilrc",
"www.nursing",
"art",
"announcements.cm",
"ccie",
"communityrelations",
"foundation",
"knowledgebase",
"healthprofessions",
"federation.net",
"facultysenate",
"ilrc",
"energyresearch",
"airforce",
"lead.sdes",
"osi",
"energy",
"mcnair",
"med",
"my",
"my.intl",
"digitallearning",
"www.sdes",
"video",
"wireless",
"training",
"news",
"tv",
"sales",
"web",
"planet",
"commencement",
"environment",
"art",
"sandbox",
"students",
]

url_list = find_all_subdomains(URL_DOMAIN)

for item in exclusion_list:
    for url in url_list:
        if item in url["url"]:
            url_list.remove(url)
            break

results = []
for url in url_list:
    results.append(get_content(url["url"]))

print(results)