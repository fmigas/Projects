import re
import requests
from bs4 import BeautifulSoup
from loguru import logger


def remove_excess_newlines(text):
    return re.sub(r'\n{2,}', '\n', text)


def download_website(url: str) -> str | None:
    main_content = None

    try:
        # Step 1: Download the website
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Step 2: Parse the website content and extract main text
        soup = BeautifulSoup(response.content, "html.parser")

        # Extracting the main content - you can customize this further
        # Common tags for main content: <p>, <article>, etc.
        main_content = "\n".join([p.get_text(strip = True) for p in soup.find_all('p')])

        logger.info(f"Url {url} downloaded successfully'.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching the website: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    return main_content
