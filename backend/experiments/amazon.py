from amazon_paapi import AmazonApi

KEY = "AKIA6377777777777777"
SECRET = "7777777777777777777777777777777777777777"
TAG = "7777777777777777777777777777777777777777"
COUNTRY = "US"

if __name__ == "__main__":
    print("Hello World")
    amazon = AmazonApi(KEY, SECRET, TAG, COUNTRY)

    search_result = amazon.search_items(keywords='garlic')
    for item in search_result.items:
        print(item)