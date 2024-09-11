Literally grabs google jobs and filters it out for you. Great for finding companies in need of a specific service based on jobs. We used it to find ppl looking for Data Engineering @ Ardentai.io


**Usage:**

Run GoogleJobsScraper.py to run the scraper. Make sure to set the right URL for the page. Also idk if the html classnames change per person so you might have to adjust that.

The file contains a de-duplicator as well as an LLM based parser that will grab items from description and get you and output. Feel free to adjust this. Honestly use this more as good boilerplate for your use case


There's also a file for analysis. feel free to edit that as you like. It clips into the generated CSV to extract the info you want. Super easy to just highlight and ask cursor/gpt to rewrite it for your use case.

