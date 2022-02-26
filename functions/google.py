import aiohttp
from bs4 import BeautifulSoup


async def search(request,
           num_results=10,
           date_from=None,
           date_to=None,
           lang=None):

    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/61.0.3163.100 Safari/537.36'}

    async def fetch_results(search_term, number_results, date_from, date_to, language_code):

        escaped_search_term = search_term.replace(' ', '+')
        search_settings = []

        if date_from is not None:
            search_settings.append('cd_min:' + date_from)
        if date_to is not None:
            search_settings.append('cd_max:' + date_to)
        search_settings = ','.join(search_settings)

        google_url = 'https://www.google.com/search?{}&q={}&num={}'.format(search_settings, escaped_search_term,
                                                                           number_results)
        if language_code is not None:
            google_url += '&hl={}'.format(language_code)

        async with aiohttp.ClientSession() as session:
            async with session.get(google_url, headers=usr_agent) as resp:
                text = await resp.read()
        
                return text

    def parse_results(raw_html):
        soup = BeautifulSoup(raw_html, 'html.parser')
        result_block = soup.find_all('div', attrs={'class': 'g'})
        for result in result_block:
            desc = str(result.find('em').parent).replace("<span>", "").replace("</span>", "").replace("<em>", "").replace("</em>", "") if result.find('em') != None else None

            link = result.find('a', href=True)
            try:
                title = result.find('h3').text
            except Exception as e:
                title = None
            if link and title:
                yield ReturnValue(url=link['href'], description=desc, title=title)

    html = await fetch_results(request, num_results, date_from, date_to, lang)
    parsed = parse_results(html)
    return list(parsed)

class ReturnValue:
    def __init__(self, url, description, title):
        self.url = url
        self.description = description
        self.title = title