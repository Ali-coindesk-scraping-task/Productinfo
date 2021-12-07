"""
Created on Sat Dec 04 08:48:50 2021

@author: Ali Mir
"""


import requests #Fetch HTML
from bs4 import BeautifulSoup as BS # Pull the data
import lxml # Parse HTML to Python
import pandas as pd # Dataframe module





#Topics to be scraped are Science and Poetry
url = "https://books.toscrape.com/index.html"





# First-layer scraping function to grab all the link to the sub categories; the result will be a dictionary
def dict_of_links(url):
    re = requests.get(url)
    soup = BS(re.content, "lxml")
    list_all_cat = []
    dict_all_cat = {}
    for categories in soup.find("ul", class_="nav nav-list").find_all("a"):
        name_of_diff_cats = (categories.text.strip())
        links = (url.replace("index.html", "") + categories.get("href").strip())
        list_all_cat.append((name_of_diff_cats, links))
    # Creating a dictionary from a list of tuples    
    for a, b in list_all_cat:
        dict_all_cat.setdefault(a, b)
    return(dict_all_cat)

main_links = dict_of_links(url) #dictionary of links and their corresponding category name


# Second-layer scraping function in order to acquire the links of "ALL" the books in that category.

# Expects a direct link the category page to be provided. Some pages have more than 20 books in their category, 
# forcing a secondary layer scraping. This requirement is being done by recursively checking for the "Next Page" button.

# Returns 2 lists: a list containing links to each book's page for further scraping and a list containing the name of the books.

def link_of_all_books_in_category(link):
    BookS_links = []
    name_of_books = []
    condition = True
    while condition:
        response = requests.get(link)
        soup = BS(response.content, "lxml")
        try:
            for books in soup.find("ol", class_="row").find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3"):
                books_links = books.find("div", class_="image_container").find("a").get("href").replace("../../../", "")
                books_links = "https://books.toscrape.com/catalogue/"+ books_links
                BookS_links.append(books_links)
                books_names = books.find_all("img", class_="thumbnail")[0].get("alt")
                name_of_books.append(books_names)

            next_page = soup.find("li", class_="next").find("a").get("href")
            if next_page is not None:
                next_page_link = link.split("/")
                fix_link = ("/".join(next_page_link[0:7]))
                fix = fix_link + "/" + next_page
                link = fix
            else:
                condition = False
        except:
            condition = False
    return BookS_links, name_of_books

# Third-layer scraping function to store all of each individual books' information in a dictionary

def book_info(list_of_links):
    empty_set = set()
    info_dict = {"Summary" : empty_set}
    for links in list_of_links:
        response = requests.get(links)
        soup = BS(response.content, "lxml")
        for infoo in soup.find_all("tr"):
            summary = soup.find_all("p")[3].text
            empty_set.add(summary)
            kii = infoo.find("th").text
            val = infoo.find("td").text
            if kii not in info_dict:
                empty_ls = []
                empty_ls.append(val)
                info_dict[kii] = empty_ls
            else:
                empty_list = []
                for values in info_dict[kii]:
                    empty_list.append(values)
                empty_list.append(val)
                info_dict[kii] = empty_list
    return info_dict

# Dataframe creation functionality

def save_it(categories: list):
    
    main_links = dict_of_links(url) #dictionary of links and their corresponding category name
    
    headers = {"Category":[] ,"Book_Name":[] ,"Book_Link":[] ,"UPC" :[] ,"Price_Excl_Tax" : [],"Price_Incl_Tax" :[] ,"Tax" :[] ,"Availability" :[] ,"Number_of_Reviews" :[] ,"Summary_Of_Book" : []}
    df = pd.DataFrame.from_dict(headers)
    
    for Category in categories:
        print(Category, "category scraped successfully!!!")
        Book_Links, name_of_books = link_of_all_books_in_category(main_links[Category])
        book_info_dict = book_info(Book_Links)
        dict_list = {"Category": [Category] * len(Book_Links),
                    "Book_Name": name_of_books,
                    "Book_Link": Book_Links,
                     "UPC" : list(book_info_dict["UPC"]),
                     "Price_Excl_Tax" : list(book_info_dict["Price (excl. tax)"]),
                     "Price_Incl_Tax" : list(book_info_dict["Price (incl. tax)"]),
                     "Tax" : list(book_info_dict["Tax"]),
                     "Availability" : list(book_info_dict["Availability"]),
                     "Number_of_Reviews" : list(book_info_dict["Number of reviews"]),
                     "Summary_Of_Book" : list(book_info_dict["Summary"])
                    }
        df1 = pd.DataFrame.from_dict(dict_list)
        df = df.append(df1, ignore_index=True)
    return df


# Calling the function for dataframe creation, with the option of adding as desired categories for scraping as an entry of list
desired_categories = ["Science", "Poetry"]
dataframe_saved = save_it(desired_categories)

# Saving the dataframe as a CSV file to the current working directory.
# Note that utf-8 encoding is enforced for proper encoding as Python uses Unicode
fn = []
for categories in desired_categories:  
    l = categories[0:2]
    fn.append(l)

file_name = ("&".join(fn))    
dataframe_saved.to_csv(f"{file_name}.csv", encoding="utf-8-sig")
