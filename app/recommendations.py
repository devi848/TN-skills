from urllib.parse import quote_plus


PLATFORMS = {
    "amazon":
        "https://www.amazon.in/s?k={q}",

    "flipkart":
        "https://www.flipkart.com/search?q={q}",

    "ikea":
        "https://www.ikea.com/in/en/search/?q={q}",

    "myntra":
        "https://www.myntra.com/{q}",

    "meesho":
        "https://www.meesho.com/search?q={q}",

    "bluestone":
        "https://www.bluestone.com/search?q={q}",

    "tanishq":
        "https://www.tanishq.co.in/search?q={q}",

    "caratlane":
        "https://www.caratlane.com/search.html?query={q}",

    "melorra":
        "https://www.melorra.com/search?q={q}",

    "swiggy":
        "https://www.swiggy.com/search?query={q}",

    "zomato":
        "https://www.zomato.com/search?query={q}",

    "bookmyshow":
        "https://in.bookmyshow.com/search/?q={q}",

    "google":
        "https://www.google.com/search?q={q}"
}


def add_links(result, planner_type):

    platforms = {
        "home": [
            "amazon",
            "flipkart",
            "ikea"
        ],

        "party": [
            "amazon",
            "flipkart",
            "swiggy",
            "zomato",
            "bookmyshow",
            "google"
        ],

        "jewelry": [
            "amazon",
            "flipkart",
            "bluestone",
            "tanishq",
            "caratlane",
            "melorra",
            "meesho"
        ]
    }[planner_type]

    for category in result.get(
        "budget_breakdown",
        []
    ):

        for item in category.get(
            "items",
            []
        ):

            search_text = (
                item.get("search_terms")
                or item.get("name")
                or "product"
            )

            query = quote_plus(
                search_text
            )

            item["shopping_links"] = {
                platform:
                    PLATFORMS[platform].format(
                        q=query
                    )
                for platform in platforms
            }

    return result