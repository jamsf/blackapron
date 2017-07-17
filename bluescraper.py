import io
import re
import argparse
import requests
import json
import time
from lxml import html

SEASONS = ['fall', 'winter', 'spring', 'summer']

CUISINES = ['african', 'american', 'asian', 'british', 'cajun', 'caribbean', 'chinese',
            'easteuro', 'egyptian', 'french', 'german', 'greek', 'indian', 'italian', 'japanese',
            'korean', 'latin', 'mediterranean', 'mexican', 'middleeastern', 'moroccan', 'nepalese',
            'southern', 'spanish', 'swedish', 'thai', 'vietnamese']

PROTEINS = ['beef', 'fish', 'lamb', 'pork', 'poultry', 'shellfish', 'vegetarian']

MEASUREMENTS = [' Ounce ', ' Ounces ', ' Bunch ', ' Bunches ', ' Tablespoon ', ' Tablespoons ',
                ' Teaspoon ', ' Teaspoons ', ' Cup ', ' Cups ', ' Pinch ', ' Pound ', ' Pounds ']

BLUE_URL = 'https://www.blueapron.com/recipes/{0}'
THIS_WEEK_RECIPES_URL = 'https://www.blueapron.com/cookbook/all/all/This%20Week'

class Ingredient():
    def __init__(self, name, amount, measurement=''):
        self.name = name
        self.amount = amount
        self.measurement = measurement
        self.sanitize_html_friendly()

    def sanitize_html_friendly(self):
        self.amount = self.amount.replace('&#188;', '.25')
        self.amount = self.amount.replace('&#189;', '.5')
        self.amount = self.amount.replace('&#190;', '.75')
        self.amount = self.amount.replace('&#8531;', '.33')
        self.amount = self.amount.replace('&#8532;', '.66')
        self.amount = self.amount.replace('&#8539;', '.15')
        self.name = self.name.replace('&amp;', '&')
        self.name = self.name.replace('&#232;', 'e')
        self.name = self.name.replace('&#238;', 'i')


    def pretty_print(self):
        if self.measurement:
            print '{0}\n\tAmount: {1}\n\tMeasurement: {2}'.format(self.name, self.amount, self.measurement)
        else:
            print '{0}\n\tAmount: {1}'.format(self.name, self.amount)

class Recipe:
    def __init__(self, name, ingredients, url, calories, season, cuisine, protein):
        self.name = name
        self.ingredients = ingredients
        self.url = url
        self.season = season
        self.cuisine = cuisine
        self.protein = protein
        self.calories = calories

    def to_json_serializable(self):
        recipe = {'name': self.name, 'url': self.url, 'calories': self.calories, 'season': self.season, 
                'cuisine': self.cuisine, 'protein': self.protein}
        ingredients_list = []
        for i in self.ingredients:
            ingredients_list.append(i.__dict__)
        recipe['ingredients'] = ingredients_list
        return recipe


"""""""""""""""""""""""""""
INGREDIENTS
"""""""""""""""""""""""""""

def get_ingredients(page):
    tree = html.fromstring(page.content)
    parent_elem_list = tree.xpath('//li[@itemprop="ingredients"]')
    ingredients = []

    for elem in parent_elem_list:
        # might be a non-story
        i_elem = elem.find('div')
        if i_elem == None:
            i_elem = elem.find('a')
        
        ingredient = parse_ingredient(stringify_children(i_elem))
        ingredients.append(ingredient)

    return ingredients

def get_calorie_count(page):
    tree = html.fromstring(page.content)
    elem = tree.xpath('//span[@itemprop="nutrition"]')
    if len(elem) <= 0:
        return '-1'
    elem = elem[0]
    nutr_elem = elem.find('span')
    calories = nutr_elem.text
    return calories


def parse_ingredient(raw_ingredient_str):
    # Parse Ingredient and measurement
    ingredient_re = re.compile('<\/span>(.+?)\n')
    ingredient_str = ingredient_re.findall(raw_ingredient_str)[0]
    measurement = ''
    ingredient = ''
    for m in MEASUREMENTS:
        if m in ingredient_str:
            measurement = m.strip()
            ingredient = ingredient_str.replace(measurement, '').strip()
            break
    if not ingredient:
        ingredient = ingredient_str.strip()

    # parse amount
    amount_re = re.compile('<span class="amount">(.+?)<\/span>')
    amount = amount_re.findall(raw_ingredient_str)[0]

    full_ingredient = Ingredient(ingredient, amount, measurement)

    return full_ingredient

# Breaks down ingredient elements into a parcable string
def stringify_children(node):
    from lxml.etree import tostring
    from itertools import chain
    parts = ([node.text] +
            list(chain(*([c.text, tostring(c), c.tail] for c in node.getchildren()))) +
            [node.tail])
    # filter removes possible Nones in texts and tails
    return ''.join(filter(None, parts))


"""""""""""""""""""""""""""
RECIPES 
"""""""""""""""""""""""""""

def get_full_recipes(recipe_links, limit=180):    
    full_recipes = {}
    with open('./recipes-minify.json', 'r') as f:
        full_recipes = json.load(f)

    print "Existing Recipe Loaded Count: {0}".format(str(len(full_recipes)))
    i = 0
    for link,info in recipe_links.iteritems():
        if link in full_recipes:
            continue
        i += 1
        if i > limit:
            break

        page = requests.get(BLUE_URL.format(link))
        ingredients = get_ingredients(page)
        calories = get_calorie_count(page)
        name = link.replace('-', ' ').title()
        url = BLUE_URL.format(link)
        recipe = Recipe(name, ingredients, url, calories, info['season'], info['cuisine'], info['protein'])
        full_recipes[link] = recipe.to_json_serializable()
        print "({0}/{1}) - {2}".format(str(i), str(limit), name)

        time.sleep(1)

    print full_recipes
    return full_recipes


def get_all_recipes():
    recipe_links = serialize_all_recipes()

    full_recipes = get_full_recipes(recipe_links)

    print '\nTotal Number of Recipes to Serialized: ' + str(len(full_recipes))

    with open('./recipes.json', 'w') as f:
        f.write(json.dumps(full_recipes, indent=4, sort_keys=True))
    with open('./recipes-minify.json', 'w') as f:
        f.write(json.dumps(full_recipes))

"""
def get_recipe_links_from_web(link):
    page = requests.get(link)
    tree = html.fromstring(page.content)
    elem = tree.xpath('//span[@itemprop="nutrition"]')
"""

def get_recipes_links(link):
    full_recipe_text = ''
    if link.startswith('http'):
        page = requests.get(link)
        full_recipe_text = page.content
    else:
        with open(link, 'r') as f:
            full_recipe_text = f.read()

    recipe_re = re.compile('<a href="(?:https:\/\/www\.blueapron\.com)?\/recipes\/(.+?)">')
    recipes = recipe_re.findall(full_recipe_text)



    return recipes

def serialize_all_recipes():
    all_recipes = get_recipes_links('./blue.htm')

    recipe_to_tags = {x: {'cuisine':[],'season':[],'protein':[]} for x in all_recipes}

    # add cuisine tags
    for cuisine in CUISINES:
        recipes = get_recipes_links('./cuisine/{0}.htm'.format(cuisine))
        for link in recipes:
            if link in recipe_to_tags:
                recipe_to_tags[link]['cuisine'].append(cuisine)

    # add season tags
    for season in SEASONS:
        recipes = get_recipes_links('./season/{0}.htm'.format(season))
        for link in recipes:
            if link in recipe_to_tags:
                recipe_to_tags[link]['season'].append(season)

    # add prtein tags 
    for protein in PROTEINS:
        recipes = get_recipes_links('./protein/{0}.htm'.format(protein))
        for link in recipes:
            if link in recipe_to_tags:
                recipe_to_tags[link]['protein'].append(protein)

    return recipe_to_tags

def get_recipes_this_week():
    links = get_recipes_links(THIS_WEEK_RECIPES_URL)
    print links
    full_recipes = []
    i = 0
    for link in links:
        i += 1
        page = requests.get(BLUE_URL.format(link))
        ingredients = get_ingredients(page)
        calories = get_calorie_count(page)
        name = link.replace('-', ' ').title()
        url = BLUE_URL.format(link)
        # We don't care about the season/cuisine/protein here since it's a limited set
        recipe = Recipe(name, ingredients, url, calories, [], [], [])
        recipe_json = recipe.to_json_serializable()
        full_recipes.append(recipe)
        print "({0}/{1}) - {2}".format(str(i), str(len(links)), name)

        time.sleep(1)

    return full_recipes


"""""""""""""""""""""""""""
MAIN 
"""""""""""""""""""""""""""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--recipe")
    args = parser.parse_args()

    get_all_recipes()
    #serialize_all_recipes()

if __name__ == '__main__':
    main()