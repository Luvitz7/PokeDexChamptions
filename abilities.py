from bs4 import BeautifulSoup
import re
import requests
import json
from pprint import pprint

def get_soup(url):
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        soup = BeautifulSoup(respuesta.content, "html.parser")
        return soup, respuesta.status_code
    else:
        return None, respuesta.status_code
    
def get_pagination():
    url = "https://pokebase.app/pokemon-champions/abilities"
    soup, status = get_soup(url)

    list_urls = ["https://pokebase.app/pokemon-champions/abilities"]

    if status == 200 :
        pages = soup.find('span', class_=re.compile("mx-1"))

        first_page = int(pages.previous_sibling.contents[0].string)
        last_page = int(pages.previous_sibling.contents[2].string)
    
        for i in range(first_page+1, last_page+1):
            new_url = (f"https://pokebase.app/pokemon-champions/abilities?page={i}")

            list_urls.append(new_url)

    return list_urls

def parse_abilities():
    urls = get_pagination()
    abilities_list = []

    for url in urls:
        soup, status = get_soup(url)

        if status == 200:
            patern = re.compile(r"/pokemon-champions/abilities/")

            for a in soup.find_all("a", href=patern):
                pokemon_list = []
                ability_name = a.string.strip()
                span_link = a.find_parent("span")
                span_valor = span_link.find_next_sibling("span")
                span_text = list(span_valor.stripped_strings) if span_valor else ["No effect found"]

                for text in span_text[1:]:
                    pokemon_list.append(text)

                abilities_list.append({
                    "name": ability_name,
                    "effect": span_text[0],
                    "pokemons": pokemon_list
                })       
    
#    print(f"Se han obtenido {len(abilities_list)} habilidades.")
#    pprint(abilities_list[0])

    with open("data/abilities_en.json", "w", encoding="utf-8") as file:
        json.dump(abilities_list, file, ensure_ascii=False, indent=4) 

    return abilities_list

parse_abilities()