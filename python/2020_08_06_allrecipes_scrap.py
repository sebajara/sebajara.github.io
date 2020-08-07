import scrapy
import requests
import re
import json
import numpy as np
import string
from datetime import date
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

outfolder = './'
lowid = 7000
highid = 8000

def openpage(id):
    # Just in case, we use a dummy header when using requests.get
    headers = requests.utils.default_headers()
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
    url = 'https://www.allrecipes.com/recipe/{}/'.format(id)
    noerror = 0
    while(not noerror):
        try:
            html = requests.get(url, headers=headers).content
            noerror = 1
        except:
            noerror = 0
    sel = scrapy.Selector(text=html)
    return(sel, url)

def get_title(sel, fancypage=False):
    if(fancypage):
        # eg. id = 141000
        title = sel.css(' div.headline-wrapper h1::text').extract_first()
    else:
        title = sel.css(' section.recipe-summary h1::text').extract_first()
    return(title)

def get_author(sel, fancypage=False):
    if(fancypage):
        author = sel.css(' a.author-name::text').extract_first()
        if(not author): # there seem to be 2 variants
            author = sel.css(' span.author-name::text').extract_first()
    else:
        author = sel.css(' span.submitter__name::text').extract_first()
    return(author)

def get_ingredient_list(sel, fancypage=False):
    ingredients = {}
    if(fancypage):
        ingrids = sel.css(' ul.ingredients-section input.checkbox-list-input') 
        ingridstxt = sel.css(' ul.ingredients-section span.ingredients-item-name')
        if(ingrids):  # just in case
            for (inp, span) in zip(ingrids, ingridstxt):
                ingid = inp.xpath('@value').extract_first()
                ingrid_txt = span.css('::text').extract_first()
                if(ingid and ingrid_txt):
                    ingredients[ingid.strip()] = ingrid_txt.strip()
        else:
            print("Ingredients could not be retrieved for recipe\n".format(id))
    else:
        ingrids = sel.css(' ul.list-ingredients-1 span.recipe-ingred_txt')+sel.css(' ul.list-ingredients-2 span.recipe-ingred_txt')
        if(ingrids):  # just in case
            for span in ingrids:
                ingid = span.xpath('@data-id').extract_first()
                ingrid_txt = span.css('::text').extract_first()
                if(ingid and ingrid_txt):
                    ingredients[ingid] = ingrid_txt.strip()
        else:
            print("Ingredients could not be retrieved for recipe\n".format(id))        
    return(ingredients)

def get_directions(sel, fancypage=False):
    if(fancypage):
        directions = [txt.strip() for txt in sel.css(' ul.instructions-section div.paragraph p::text').extract()]
    else:
        directions = [txt.strip() for txt in sel.css(' span.recipe-directions__list--item::text').extract()]
    return(directions)

def get_rating(sel, fancypage=False):
    if(fancypage):
        txt = sel.css(' div.recipe-ratings span.review-star-text::text').extract_first()
        if(txt):
            star_rating = float(re.findall('(\d+\.*\d*).*', txt.strip())[0])
        else:
            star_rating = np.nan
    else:
        txt = sel.css(' section.recipe-summary div.rating-stars').xpath('@data-ratingstars').extract_first()
        if(txt):
            star_rating = float(txt)
        else:
            star_rating = np.nan
    return(star_rating)

def get_nmadereview(sel, fancypage=False):
    if(fancypage):
        n_made = np.nan # I don't see this info displayed on this new version
        txts = [txt.strip() for txt in sel.css(' li.ugc-ratings-list-item span::text').extract()]
        if(txts):
            for txt in txts:
                if('Ratings' in txt):
                    n_reviews = int(re.findall('(\d+).*', txt)[0])
        else:
            n_reviews = np.nan
    else:
        txts = [txt.strip() for txt in sel.css(' section.recipe-summary a.read--reviews span::text').extract()]
        if(txts):
            for txt in txts:
                if('reviews' in txt):
                    n_reviews = int(re.findall('(\d+).*', txt)[0])
                elif('made it' in txt):
                    n_made = int(re.findall('(\d+).*', txt)[0])
        else:
            n_reviews = np.nan
            n_made = np.nan
    return(n_made, n_reviews)

def get_categories(sel, fancypage=False):
    if(fancypage):
        categories = [txt.strip() for txt in sel.css(' ol.breadcrumbs__list span.breadcrumbs__title::text').extract()
                      if not((txt.strip() == 'Home') or (txt.strip() == 'Recipes'))]
    else:
        categories = sel.xpath('//meta[@itemprop=\'recipeCategory\']/@content').extract()
    return(categories)

def get_nservings(sel, fancypage=False):
    if(fancypage):
        # NOTE: this website version also includes prep and cooking
        # times, which we are not parsing
        n_servings = np.nan
        for div in sel.css(' div.two-subcol-content-wrapper div.recipe-meta-item'):
            head = div.css(' div.recipe-meta-item-header::text').extract_first()
            txt = div.css(' div.recipe-meta-item-body::text').extract_first()
            if('Servings' in head):
                n_servings = int(txt.strip())
    else:
        n_servings = sel.xpath('//meta[@id=\'metaRecipeServings\']/@content').extract_first()
        if(n_servings):
            n_servings = float(n_servings)
        else:
            n_servings = np.nan
    return(n_servings)

def get_ncalories(sel, fancypage=False):
    if(fancypage):
        n_calories = np.nan
    else:
        cals = sel.xpath('//span[@class=\'calorie-count\']/@aria-label').extract_first()
        if(cals):
            n_calories = float(re.findall('.*?(\d+).*?', cals)[0])
        else:
            n_calories = np.nan
    return(n_calories)

def get_nut_info(sel, fancypage=False):
    n_calories = np.nan
    if(fancypage):
        nut_text = sel.css(' div.recipe-nutrition-section div.section-body::text').extract_first()
        extra_info = {}
        if(nut_text):
            nut_text = nut_text.strip()
            # NOTE: apparently separations are not always by semi-colon,
            # sometimes is by a dot. Kind of a pain, given floats also
            # have a dot. In any case, we are picking the right info
            # with the extra section. Leave just in case? Would be easy
            # to detect and remove errors later.
            for item in re.sub('\s+', ' ', nut_text).split(';'):
                if(item == ''):
                    continue
                elif('calories' in item):
                    n_calories = float(re.findall('(\d+).*?', item)[0])
                else:
                    subitem = item.strip().split(' ')
                    num = float(subitem[0])
                    units = subitem[1]
                    content = ' '.join(subitem[2:])
                    extra_info[content] = [num, units]
    else:
        nut_span = sel.css(' div.nutrition-summary-facts span')
        extra_info_num = {}
        extra_info_units = {}
        extra_info = {}
        if(nut_span):
            # here the code is slightly more convoluted as the value and
            # type of value is in one span, but the units are the span
            # following it. So we get save the types when we find them,
            # and then put the value and units into the separate arrays
            # using the type key, so we can finally combine them at the
            # end.
            for span in nut_span:
                itemprop_temp = span.xpath('@itemprop').extract_first()
                if(itemprop_temp): # if there is a type, save it
                    itemprop = itemprop_temp
                text = span.css('::text').extract_first()
                units = span.xpath('@aria-label').extract_first()
                if(not itemprop_temp == 'calories'):  # we already got that
                    if(itemprop_temp):  # then is the span with the value
                        itemprop = itemprop.replace('Content', '')
                        extra_info_num[itemprop] = text
                        # NOTE: some text values are '< 1', so for now
                        # let's keep it as a string
                    elif(units):  # then is the span with the units
                        # remove punctuations as we dont need them
                        units = units.translate(str.maketrans('', '', string.punctuation))
                        extra_info_units[itemprop] = units
            extra_info = {k: [v, extra_info_units[k]] for (k, v) in extra_info_num.items()}
    return(extra_info, n_calories)

def get_extrainfo(sel, fancypage=False, driver=None, url=None):
    extra_info = {}
    if(fancypage):
        # 2) Extra nutritional info is a lot easier here
        for row in sel.css(' section.recipe-nutrition div.nutrition-row'):
            name = row.css(' span.nutrient-name::text').extract_first().strip()
            if(name and ('from' not in name)):
                if(name):
                    name = re.sub(':', '', name)
                value = row.css(' span.nutrient-value::text').extract_first().strip()
                numvalue = re.findall('(\d+\.*\d*).*?', value)[0]
                unit = value.replace(numvalue, '')
                extra_info[name] = [float(numvalue), unit]
        loadpage_TimeoutException = 0
        nutrition_TimeoutException = 0
    elif(driver):
        # we need to run a openNutritionAndTrack() script
        # NOTE: the approach was inspired by this towardsdatascience post:
        # https://towardsdatascience.com/data-science-skills-web-scraping-javascript-using-python-97a29738353f
        # NOTE 2: this makes the whole scrapping quite slower and
        # doesn't add a lot more information.
        loadpage_TimeoutException = np.nan
        nutrition_TimeoutException = np.nan
        delay = 60  # seconds
        n_servings = np.nan
        n_calories = np.nan
        driver.get(url)
        try:
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'see-full-nutrition')))
            driver.execute_script("openNutritionAndTrack();")
            try:
                WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'recipe-nutrition')))
                result = driver.find_elements_by_xpath("//div[contains(@class, 'recipe-nutrition')]")
                if(result):
                    nutritional_info = result[0].text
                    # 2.1) number of servings
                    # 2.2) calories per serving
                    # 2.3) Detailed nutritional_info
                    infos = nutritional_info.split('\n')  # separate each line
                    for txt in infos:
                        if('Servings Per Recipe' in txt):
                            n_servings = int(re.findall('.*?(\d+).*?', txt)[0])
                        elif('Calories:' in txt):
                            n_calories = float(re.findall('.*?(\d+).*?', txt)[0])
                        elif(': ' in txt):
                            # save the detailed info into a dic
                            extra_info[txt.split(': ')[0]] = txt.split(': ')[1]
            except TimeoutException:
                nutrition_TimeoutException = 1
                print("Exceeded waiting time waiting for openNutritionAndTrack()")
        except TimeoutException:
            print("Exceeded waiting time loading page")
            loadpage_TimeoutException = 1
    return(extra_info, loadpage_TimeoutException, nutrition_TimeoutException)

def parse_page(id, usewebdriver=False):
    print("Getting recipe {}".format(id))
    if(usewebdriver):
        driver = webdriver.Firefox()
        # Make a selector object
    sel, url = openpage(id)
    print("... url: {}".format(url))
    # by default we go for the non-fancy page
    fancypage = False
    # 1.0) recipe title
    title = get_title(sel, fancypage=fancypage)
    if(not title):
        fancypage = True
        title = get_title(sel, fancypage=fancypage)
        print("... recipe {} is a fancy page".format(id))
    else:
        print("... recipe {} is a non-fancy page".format(id))
    # If we don't get the title, skip.
    if(not title): 
        print("... Skipping recipe {}".format(id))
        return()
    # 1.1) recipe author
    author = get_author(sel, fancypage=fancypage)
    # 1.2) list of ingredients
    ingredients = get_ingredient_list(sel, fancypage=fancypage)
    # 1.3) recipe instructions
    directions = get_directions(sel, fancypage=fancypage)
    # 1.4) average rating
    star_rating = get_rating(sel, fancypage=fancypage)
    # 1.5) number of people who have made the recipe
    # 1.6) number of reviews within the website (for the ratings)
    n_made, n_reviews = get_nmadereview(sel, fancypage=fancypage)
    # 1.7) Recipe categories
    categories = get_categories(sel, fancypage=fancypage)
    # 1.8) Number of servings
    n_servings = get_nservings(sel, fancypage=fancypage)
    # 1.9) Number of calories per serving
    n_calories = get_ncalories(sel, fancypage=fancypage)
    # 1.10) nutrional content
    if(fancypage):
        extra_info, n_calories = get_nut_info(sel, fancypage=fancypage)
    else:
        extra_info, _ = get_nut_info(sel, fancypage=fancypage)
    # 2) Additional nutrional content
    loadpage_TimeoutException = np.nan
    nutrition_TimeoutException = np.nan
    if(fancypage):
        extra_info = get_extrainfo(sel, fancypage=fancypage)
    elif((not fancypage) and usewebdriver):
        extra_info, loadpage_TimeoutException, nutrition_TimeoutException = get_extrainfo(sel, fancypage=False, driver=driver, url=url)
    # 3) ======= Compile all the data
    data = {"id": id,
            "title": title,
            "author": author,
            "categories": categories,
            "ingredients": ingredients,
            "directions": directions,
            "star_rating": star_rating,
            "n_reviews": n_reviews,
            "n_madeit": n_made,
            "n_servings": n_servings,
            "n_calories": n_calories,
            "nutritional_info": extra_info,
            "loadpage_TimeoutException": loadpage_TimeoutException,
            "nutrition_TimeoutException": nutrition_TimeoutException,
            "access_date": date.today().strftime("%d/%m/%Y")}
    if(usewebdriver):
        # Close webdriver
        driver.quit()
    return(data)

# ======== Testing
# ==== Fancy site:
# >> parse_page(7000)
# {'id': 7000,
# 'title': 'Golden Crescent Rolls',
# 'author': 'Mike A.',
# 'categories': ['Bread', 'Yeast Bread', 'Rolls and Buns'],
# 'ingredients': {'(.25 ounce) package active dry yeast': '2 (.25 ounce) packages active dry yeast',
#  'water': '¾ cup warm water (110 degrees F/45 degrees C)',
#  'pinch white sugar': '½ cup white sugar',
#  'pinch salt': '1 teaspoon salt',
#  'eggs': '2  large eggs eggs',
#  'stick butter': '¼ cup butter, softened',
#  'dash all-purpose flour': '4 cups all-purpose flour'},
# 'directions': ['Dissolve yeast in warm water.',
#  'Stir in sugar, salt, eggs, butter, and 2 cups of flour. Beat until smooth. Mix in remaining flour until smooth. Scrape dough from side of bowl. Knead dough, then cover it and let rise in a warm place until double (about 1 1/2 hours).',
#  'Punch down dough. Divide in half. Roll each half into a 12-inch circle. Spread with butter. Cut into 10 to 15 wedge. Roll up the wedges starting with the wide end. Place rolls with point under on a greased baking sheet. Cover and let rise until double (about 1 hour).',
#  'Bake at 400 degrees F (205 degrees C) for 12-15 minute or until golden brown. Brush tops with butter when they come out of the oven.'],
# 'star_rating': 4.58,
# 'n_reviews': 398,
# 'n_madeit': nan,
# 'n_servings': 20,
# 'n_calories': 180.0,
# 'nutritional_info': {'protein': [3.6, 'g'],
#  'carbohydrates': [24.4, 'g'],
#  'exchange other carbs': [1.5, ''],
#  'dietary fiber': [0.8, 'g'],
#  'sugars': [5.1, 'g'],
#  'fat': [7.7, 'g'],
#  'saturated fat': [4.6, 'g'],
#  'cholesterol': [36.9, 'mg'],
#  'vitamin a iu': [237.1, 'IU'],
#  'niacin equivalents': [2.5, 'mg'],
#  'vitamin b6': [0.0, 'mg'],
#  'vitamin c': [0.0, 'mg'],
#  'folate': [64.7, 'mcg'],
#  'calcium': [9.3, 'mg'],
#  'iron': [1.4, 'mg'],
#  'magnesium': [7.0, 'mg'],
#  'potassium': [49.7, 'mg'],
#  'sodium': [173.4, 'mg'],
#  'thiamin': [0.2, 'mg']},
# 'loadpage_TimeoutException': 0,
# 'nutrition_TimeoutException': 0,
# 'access_date': '05/08/2020'}
# ==== Non-fancy site:
# >> parse_page(8000)
#{'id': 8000,
# 'title': 'Strawberry Cream Roll',
# 'author': 'JJOHN32',
# 'categories': ['Desserts', 'Fruit Desserts', 'Strawberry Desserts'],
# 'ingredients': {'16317': '3 eggs',
#  '1526': '1 tablespoon white sugar',
#  '2496': '1/4 cup cold water',
#  '16424': '1 teaspoon vanilla extract',
#  '1684': '1 cup sifted all-purpose flour',
#  '2356': '1 teaspoon baking powder',
#  '16421': '1/4 teaspoon salt',
#  '1527': "2 tablespoons confectioners' sugar, for dusting (optional)",
#  '1425': '1 teaspoon unflavored gelatin',
#  '16258': '1 cup heavy cream, chilled',
#  '5233': '1 cup fresh strawberries'},
# 'directions': ['Preheat oven to 375 degrees F (190 degrees C). Butter a jelly roll pan. Line it with buttered foil or buttered parchment paper.',
#  'Beat the eggs until thick and lemon colored. Gradually add 1 cup white sugar, beating constantly. Stir in water and vanilla extract. Fold in flour, baking powder, and salt. Pour batter into prepared pan.',
#  'Bake until cake is springy to the touch and beginning to shrink away from the sides of the pan, about 15 minutes.',
#  "Lay out a tea towel, and sprinkle it with confectioners' sugar. Turn the cake out on the towel. Peel off the paper or foil. Cut away crusty edges with kitchen shears or a sharp paring knife. Roll the cake up in the towel, and leave it to cool.",
#  "In a microwave-safe bowl, sprinkle the gelatin over the cold water and set aside. Wash and hull the strawberries; if they're large, you may halve or chop them. Melt gelatin in microwave, checking every 15 seconds. Pour gelatin and 1 tablespoon sugar over strawberries.",
#  'Whip the cream to medium-stiff peaks. Fold in cooled strawberry mixture. Unroll the cake, spread with the strawberry cream, and roll up again. Chill cake for at least 1 hour.',
#  "Before serving, dust cake with confectioners' sugar or top with additional whipped cream."],
# 'star_rating': 4.27731084823608,
# 'n_reviews': 93,
# 'n_madeit': 203,
# 'n_servings': 15.0,
# 'n_calories': 171.0,
# 'nutritional_info': {'fat': ['7 ', 'grams of fat'],
#  'carbohydrate': ['25', 'grams of carbohydrates'],
#  'protein': ['2.6 ', 'grams of protein'],
#  'cholesterol': ['59 ', 'milligrams of cholesterol'],
#  'sodium': ['92 ', 'milligrams of sodium']},
# 'loadpage_TimeoutException': nan,
# 'nutrition_TimeoutException': nan,
# 'access_date': '05/08/2020'}

# ============== LOOP OVER RECIPE IDS AND SAVE
recipes = {}  # we will save the raw data scraped into a dictionary
for id in range(lowid, highid+1):
    recipes[id] = parse_page(id)
with open('{}allrecipes_scrap_json_{}_{}.txt'.format(outfolder, lowid, highid),
          'w') as outfile:
    json.dump(recipes, outfile)
