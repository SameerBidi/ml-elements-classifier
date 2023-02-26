import requests
from bs4 import BeautifulSoup
import json

headers = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36 Edg/83.0.478.45",
  "Accept-Encoding": "*"
}

def req_source(url):
    return requests.get(url, headers=headers)


def get_elements():
    source = req_source("https://www.cs.mcgill.ca/~rwest/wikispeedia/wpcd/wp/p/Periodic_table.htm")
    soup = BeautifulSoup(source.text, "lxml")

    trs = soup.select("#bodyContent table:nth-of-type(1) > tr:not(:nth-child(1)):not(:nth-child(2)):not(:nth-child(10))")

    elements_list = []
    counter = 0

    for tr in trs:
        tds = tr.select("td[title]")
        for td in tds:
            title = td.get("title")
            if("Synthetic" not in title and "Undiscovered" not in title):
                anchor = td.select_one("a")
                orig_href = anchor.get("href")

                """https://www.cs.mcgill.ca/~rwest/wikispeedia/wpcd/"""

                href = "https://www.cs.mcgill.ca/~rwest/wikispeedia/wpcd/" + orig_href[6:]

                ele_source = req_source(href)
                ele_soup = BeautifulSoup(ele_source.text, "lxml")

                ele_trs = ele_soup.select("table[align='right']:nth-of-type(1) > tr")

                name = ele_soup.select_one("h1.firstHeading").text.strip()
                appearance = None
                phase = None
                density = None
                melting_point = None
                boiling_point = None
                crystal_structure = None

                print(f"\nTrying {name}")

                for ele_tr in ele_trs:
                    ele_tds = ele_tr.select("td")

                    if len(ele_tds) == 2:
                        ele_td0_text = ele_tds[0].text
                        ele_td1_text = ele_tds[1].text

                        if appearance is None:
                            if "Appearance" in ele_td0_text:
                                appearance = ele_td1_text.strip()
                                if " " in appearance:
                                    appearance = appearance[:appearance.index(" ")]

                        if phase is None:
                            if "Phase" in ele_td0_text:
                                phase = ele_td1_text.strip()

                        if density is None:
                            if "Density" in ele_td0_text:
                                density = remove_text_inside_brackets(ele_td1_text).partition("g")[0].strip()

                if(appearance is not None and phase is not None and density is not None):
                    elements_list.append({
                        "Name": name,
                        "Appearance": appearance,
                        "Phase": phase,
                        "Density": density
                    })
                    
                counter += 1
                print(f"{counter}. Done: {name}")

    with open("data/elements.json", "w+") as elements_file:
        elements_file.write(json.dumps(elements_list))

def remove_text_inside_brackets(text, brackets="()[]"):
    count = [0] * (len(brackets) // 2) # count open/close brackets
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b: # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1)**is_close # `+1`: open, `-1`: close
                if count[kind] < 0: # unbalanced bracket
                    count[kind] = 0  # keep it
                else:  # found bracket to remove
                    break
        else: # character is not a [balanced] bracket
            if not any(count): # outside brackets
                saved_chars.append(character)
    return ''.join(saved_chars)
                


get_elements()