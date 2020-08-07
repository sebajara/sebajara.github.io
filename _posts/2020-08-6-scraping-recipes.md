---
title: Scraping cooking recipes
date: 2020-08-06
tags: [Cooking, Web-scraping]
excerpt: "I've always wanted to have a nice cooking database. Here is how to parse recipe pages from allrecipes.com using python."
header:
  image: "/assets/images/2020-08-06_RECIPE_titles_word_cloud.png"
toc: true
toc_label: "Jump to:"
toc_icon: "fast-forward"
---

I would love to have databases related to cooking, like a recipe
database. Unfortunately I have not been able to find a freely available
large dataset. So I decide to scrap
[allrecipes.com](https://www.allrecipes.com/), given it has a very large
number of recipes and appears to have a very active community. Their
site includes detailed ingredients, description, and nutritional
information, among other things.

I found that their site is organized by
<code>https://www.allrecipes.com/recipe/\d+/</code>, where the last
digits appear to function as some kind of ID. That is perfect to have a
loop and automate parsing the recipes. Unfortunately, for some reason
their recipe pages appear to come in two flavors: one like
[ID=7000](https://www.allrecipes.com/recipe/7000/), and a second kind
like [ID=8000](https://www.allrecipes.com/recipe/8000/). I am calling
them "fancy" and "non-fancy" respectively. Here are some screenshots so you
can see the difference.


__"Fancy"__


![fancy-id-7000](/assets/images/2020-08-06_fancy_page.png){:class="img-responsive"} 


__"Non-fancy"__


![fancy-id-8000](/assets/images/2020-08-06_non-fancy_page.png){:class="img-responsive"}

This means I had to make two different ways to parse the pages.

<!--
One thing to mention is that many IDs point to the same pizza
recipe. Probably some default setting in case the ID doesn't exist, but
I could be wrong.
-->

## The strategy

In general, I used <code>scrapy</code> to parse the pages
html. Selectors make very easy to extract content using both
<code>.css()</code> and <code>.xpath()</code> methods. If you "Inspect"
the elements on the page, it is easy to what some unique combination of
classes and ids that map to the content I want. The "View Page Source"
on Firefox is also useful to double check.

One thing was special "non-fancy" pages. It turned out that the only way
to obtain the detail nutrional information was by running a
javascript. I used the strategy depicted in
[towardsdatascience](https://towardsdatascience.com/data-science-skills-web-scraping-javascript-using-python-97a29738353f)
using <code>selenium.webdriver</code> to access the output of the script
from python. It works, but makes scraping quite slow.

Here is the main code for parsing one recipe page. You can find the
whole script
[here](https://raw.githubusercontent.com/sebajara/sebajara.github.io/master/python/2020_08_06_allrecipes_scrap.py). You
would need to adjust the variables at the top to decide what range of
ids to parse, and the output folder for duming the json file. I suggest
to use begin with a small range.

```python
def parse_page(id, usewebdriver=False):
    print("Getting recipe {}".format(id))
    if(usewebdriver):
        driver = webdriver.Firefox()
        # Make a selector object
    sel, url = openpage(id)
    print("... url: {}".format(url))
    # by default we go for the non-fancy page
    fancypage = False
    # 1.0) Recipe title
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
    # 1.1) Recipe author
    author = get_author(sel, fancypage=fancypage)
    # 1.2) List of ingredients
    ingredients = get_ingredient_list(sel, fancypage=fancypage)
    # 1.3) Recipe instructions
    directions = get_directions(sel, fancypage=fancypage)
    # 1.4) Average rating
    star_rating = get_rating(sel, fancypage=fancypage)
    # 1.5) Number of people who have made the recipe
    # 1.6) Number of reviews within the website (for the ratings)
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
        extra_info, loadpage_TimeoutException, nutrition_TimeoutException = get_extrainfo(sel, fancypage=False, driver=driver)
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
```

## Example outputs

To give an idea, I will add here the outputs from parsing the two example
pages with screenshots on the top.

{% highlight python %}
>> parse_page(7000)
 {'id': 7000,
 'title': 'Golden Crescent Rolls',
 'author': 'Mike A.',
 'categories': ['Bread', 'Yeast Bread', 'Rolls and Buns'],
 'ingredients': {'(.25 ounce) package active dry yeast': '2 (.25 ounce) packages active dry yeast',
  'water': '¾ cup warm water (110 degrees F/45 degrees C)',
  'pinch white sugar': '½ cup white sugar',
  'pinch salt': '1 teaspoon salt',
  'eggs': '2  large eggs eggs',
  'stick butter': '¼ cup butter, softened',
  'dash all-purpose flour': '4 cups all-purpose flour'},
 'directions': ['Dissolve yeast in warm water.',
  'Stir in sugar, salt, eggs, butter, and 2 cups of flour. Beat until smooth. Mix in remaining flour until smooth. Scrape dough from side of bowl. Knead dough, then cover it and let rise in a warm place until double (about 1 1/2 hours).',
  'Punch down dough. Divide in half. Roll each half into a 12-inch circle. Spread with butter. Cut into 10 to 15 wedge. Roll up the wedges starting with the wide end. Place rolls with point under on a greased baking sheet. Cover and let rise until double (about 1 hour).',
  'Bake at 400 degrees F (205 degrees C) for 12-15 minute or until golden brown. Brush tops with butter when they come out of the oven.'],
 'star_rating': 4.58,
 'n_reviews': 398,
 'n_madeit': nan,
 'n_servings': 20,
 'n_calories': 180.0,
 'nutritional_info': {'protein': [3.6, 'g'],
  'carbohydrates': [24.4, 'g'],
  'exchange other carbs': [1.5, ''],
  'dietary fiber': [0.8, 'g'],
  'sugars': [5.1, 'g'],
  'fat': [7.7, 'g'],
  'saturated fat': [4.6, 'g'],
  'cholesterol': [36.9, 'mg'],
  'vitamin a iu': [237.1, 'IU'],
  'niacin equivalents': [2.5, 'mg'],
  'vitamin b6': [0.0, 'mg'],
  'vitamin c': [0.0, 'mg'],
  'folate': [64.7, 'mcg'],
  'calcium': [9.3, 'mg'],
  'iron': [1.4, 'mg'],
  'magnesium': [7.0, 'mg'],
  'potassium': [49.7, 'mg'],
  'sodium': [173.4, 'mg'],
  'thiamin': [0.2, 'mg']},
 'loadpage_TimeoutException': 0,
 'nutrition_TimeoutException': 0,
 'access_date': '05/08/2020'}
{% endhighlight %}

For the "non-fancy" pages I need to pass the
<code>usewebdriver=True</code> flag to get the detailed nutritional
information. Otherwise, it would simply parse the regular html of the
page without opening the driver and running the detailed information
script.

{% highlight python %}
>> parse_page(8000, usewebdriver=True)
{'id': 8000,
 'title': 'Strawberry Cream Roll',
 'author': 'JJOHN32',
 'categories': ['Desserts', 'Fruit Desserts', 'Strawberry Desserts'],
 'ingredients': {'16317': '3 eggs',
  '1526': '1 tablespoon white sugar',
  '2496': '1/4 cup cold water',
  '16424': '1 teaspoon vanilla extract',
  '1684': '1 cup sifted all-purpose flour',
  '2356': '1 teaspoon baking powder',
  '16421': '1/4 teaspoon salt',
  '1527': "2 tablespoons confectioners' sugar, for dusting (optional)",
  '1425': '1 teaspoon unflavored gelatin',
  '16258': '1 cup heavy cream, chilled',
  '5233': '1 cup fresh strawberries'},
 'directions': ['Preheat oven to 375 degrees F (190 degrees C). Butter a jelly roll pan. Line it with buttered foil or buttered parchment paper.',
  'Beat the eggs until thick and lemon colored. Gradually add 1 cup white sugar, beating constantly. Stir in water and vanilla extract. Fold in flour, baking powder, and salt. Pour batter into prepared pan.',
  'Bake until cake is springy to the touch and beginning to shrink away from the sides of the pan, about 15 minutes.',
  "Lay out a tea towel, and sprinkle it with confectioners' sugar. Turn the cake out on the towel. Peel off the paper or foil. Cut away crusty edges with kitchen shears or a sharp paring knife. Roll the cake up in the towel, and leave it to cool.",
  "In a microwave-safe bowl, sprinkle the gelatin over the cold water and set aside. Wash and hull the strawberries; if they're large, you may halve or chop them. Melt gelatin in microwave, checking every 15 seconds. Pour gelatin and 1 tablespoon sugar over strawberries.",
  'Whip the cream to medium-stiff peaks. Fold in cooled strawberry mixture. Unroll the cake, spread with the strawberry cream, and roll up again. Chill cake for at least 1 hour.',
  "Before serving, dust cake with confectioners' sugar or top with additional whipped cream."],
 'star_rating': 4.27731084823608,
 'n_reviews': 93,
 'n_madeit': 203,
 'n_servings': 15.0,
 'n_calories': 171.0,
 'nutritional_info': {'Total Fat': '7g',
  'Saturated Fat': '4.0g',
  'Cholesterol': '59mg',
  'Sodium': '92mg',
  'Potassium': '51mg',
  'Total Carbohydrates': '25g',
  'Dietary Fiber': '0.4g',
  'Protein': '2.6g',
  'Sugars': '18g',
  'Vitamin A': '283IU',
  'Vitamin C': '6mg',
  'Calcium': '37mg',
  'Iron': '1mg',
  'Thiamin': '0mg',
  'Niacin': '1mg',
  'Vitamin B6': '0mg',
  'Magnesium': '6mg',
  'Folate': '23mcg'},
 'loadpage_TimeoutException': nan,
 'nutrition_TimeoutException': nan,
 'access_date': '06/08/2020'}
{% endhighlight %}

## Few plots from 50K recipes

So far I have 49690 unique recipes from the site. I am guessing this
represents somewhere between 25-50% of all unique recipes.

To give you an idea, this is how the main top level categories are
represented. Many of the low index IDs happen to be desserts. Personally
I am not a big fan of sweets, so I am hoping this may change as I parse
more pages.

![](/assets/images/2020-08-06_RECIPE_category1_hist.png){:class="img-responsive"} 

I first thought to use this dataset to predict recipe's start
score. Perhaps the score is correlated to the calories per serving? In
the next plot you can see there is no obvious correlation. Furthermore,
the scores are pretty well centered in the range 4-5. I appears
reviewers are very gracious in
[allrecipes.com](https://www.allrecipes.com/), and/or that the quality
of the recipes is very high. Probably scores are only good to filter
very bad quality recipes, but don't have much meaning beyond that.

![](/assets/images/2020-08-06_RECIPE_starscore_vs_calories.png){:class="img-responsive"} 

## What's next?

Some things would be fun to do:
* Recommendation of recipes given a list of ingredients and additional
  constraints. I have something on the making using word2vec. Hope to
  make a post about it soon.
* Reverse engineer ingredients nutritional information. This is a more
  challenging, due to having to parse the beginning of the ingredient's
  string and convert it into something quantitative. After that would be
  just a very big linear regression. Would be fun to see if it works.
