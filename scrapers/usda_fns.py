from bs4 import BeautifulSoup
import requests
import json

def get_page(i=0):
    headers = {
        'authority': 'www.fns.usda.gov',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'sec-fetch-dest': 'document',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'referer': 'https://www.fns.usda.gov/contacts',
        'accept-language': 'en-US,en;q=0.9',
    }

    params = {'keywords':''}
    if i > 0:
        params.update({'page': i})

    r = requests.get('https://www.fns.usda.gov/contacts', headers=headers, params=params)
    r.raise_for_status()
    return r


def extract_info_from_cards(cards):
    data = []
    for card in cards:
        d = {}
        dept = card.find("div", {"class": "card__title"})
        d['department'] = dept.text.strip()

        dept_a = card.find("a", {"class": "card__title"})
        d['departmentLink'] = dept_a.get('href') if dept_a else None

        address1 = card.find("span", {"class": "address-line1"})
        d['addressLine1'] = address1.text if address1 is not None else None

        address2 = card.find("span", {"class": "address-line2"})
        d['addressLine2'] = address2.text if address2 is not None else None

        city = card.find("span", {"class": "locality"})
        d['city'] = city.text if city else None

        zipcode = card.find("span", {"class": "postal-code"})
        d['zipcode'] = zipcode.text if zipcode else None

        state = card.find("span", {"class": "administrative-area"})
        d['state'] = state.text if state else None

        d['contacts'] = extract_contacts_from(card)

        d['programs'] = extract_programs_from_card(card)
        data.append(d)
    return data


def extract_programs_from_card(card):
    programs = []
    program = card.find("div", {"class": "card__program"})
    if program:
        for div in program.findAll("div", {"class": "field__item"}):
            p = {}
            p['programName'] = div.text
            a = div.find("a")
            if a:
                url = a.get('href')
                if not url.startswith("http"):
                    url = "https://www.fns.usda.gov" + url
                p['programURL'] = url
            programs.append(p)
    return programs


def extract_contacts_from(card):
    contacts = []
    c = {}
    div = card.findAll("div", {"class": "card__column"})[1]
    for d in div.findAll("div"):
        cls = d.get('class')
        if not cls:
            continue
        # new contact
        if cls == ['card__other-contact']:
            contacts.append(c)
            c = {}
        elif cls == ['card__phone']:
            phones = d.findAll("div", {"class": "field__item"})
            if phones:
                if 'phoneNumbers' in c:
                    c['phoneNumbers'].extend([p.text.strip() for p in phones])
                else:
                    c['phoneNumbers'] = [p.text.strip() for p in phones]
        elif cls[0].startswith("card__"):
            key = cls[0].replace("card__", "")
            value = d.text.strip()
            if value:
                c[key] = value

    if c:
        contacts.append(c)

    return contacts


def scrape_and_save(filename):
    has_next = True
    i = 0
    data = []

    while has_next:
        print(i)
        r = get_page(i)
        soup = BeautifulSoup(r.text)
        cards = soup.find_all("div", {"class": "card card--contact"})
        d = extract_info_from_cards(cards)
        data.extend(d)
        has_next = soup.find("a", {"rel": "next"})
        i += 1

    with open(filename, "w") as f:
        json.dump(data, f)


