from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import csv

def open_dev_tools_and_extract_html(url):
    # Initialize the Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--auto-open-devtools-for-tabs")

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to the URL
        print(f"Navigating to URL: {url}")
        driver.get(url)

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Scroll down multiple times
        print("Scrolling down to load more content...")
        for _ in range(50):  # Adjust the number of scrolls as needed
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for content to load after each scroll

        # Open developer tools (Command + Option + I for Mac)
        ActionChains(driver).key_down(Keys.COMMAND).key_down(Keys.ALT).send_keys('i').key_up(Keys.COMMAND).key_up(Keys.ALT).perform()

        # Wait for a moment to ensure developer tools are open
        time.sleep(5)

        # Switch to the Console tab in developer tools (Command + Option + J for Mac)
        ActionChains(driver).key_down(Keys.COMMAND).key_down(Keys.ALT).send_keys('j').key_up(Keys.COMMAND).key_up(Keys.ALT).perform()

        # Extract the HTML
        html = driver.page_source

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Extract all h2 elements
        h2_elements = soup.find_all('h2')

        # Save h2 content to a separate file
        with open("h2_content.txt", "w", encoding="utf-8") as f:
            for h2 in h2_elements:
                f.write(f"{h2.text}\n")

        print("H2 content extracted and saved to 'h2_content.txt'.")

        # Extract the infinity-scrolling tag content
        infinity_scrolling = soup.find('infinity-scrolling')
        if infinity_scrolling:
            with open("infinity_scrolling.html", "w", encoding="utf-8") as f:
                f.write(str(infinity_scrolling))
            print("Infinity-scrolling content extracted and saved to 'infinity_scrolling.html'.")
        else:
            print("No infinity-scrolling tag found.")

        # Save the full HTML to a file
        with open("google_jobs.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("Full HTML extracted and saved to 'google_jobs.html'.")
        
        # Parse the infinity-scrolling content and save to CSV
        infinity_scrolling = soup.find('infinity-scrolling')
        if infinity_scrolling:
            job_listings = infinity_scrolling.find_all('div', class_='EimVGf')
            
            with open('job_listings.csv', 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Title', 'Company', 'Location', 'Posted', 'Job Type', 'Salary']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for job in job_listings:
                    title = job.find('div', class_='tNxQIb PUpOsf').text.strip()
                    company = job.find('div', class_='wHYlTd MKCbgd a3jPc').text.strip()
                    location = job.find('div', class_='wHYlTd FqK3wc MKCbgd').text.strip()
                    
                    # Extract additional details if available
                    details = job.find_all('div', class_='I2Cbhb')
                    posted_date = ''
                    job_type = ''
                    salary = ''
                    
                    for detail in details:
                        if 'Posted' in detail.text:
                            posted_date = detail.text.strip()
                        elif 'Full-time' in detail.text or 'Part-time' in detail.text or 'Contractor' in detail.text:
                            job_type = detail.text.strip()
                        elif 'a year' in detail.text:
                            salary = detail.text.strip()
                    
                    writer.writerow({
                        'Title': title,
                        'Company': company,
                        'Location': location,
                        'Posted': posted_date,
                        'Job Type': job_type,
                        'Salary': salary
                    })
                    
                    print(f"Title: {title}")
                    print(f"Company: {company}")
                    print(f"Location: {location}")
                    print(f"Posted: {posted_date}")
                    print(f"Job Type: {job_type}")
                    print(f"Salary: {salary}")
                    print("--------------------")
            
            print("Job listings extracted and saved to 'job_listings.csv'.")
        
        print("Press Enter to close the browser...")
        input()

        return html

    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://www.google.com/search?q=data+engineer+jobs&ibp=htl;jobs"
    extracted_html = open_dev_tools_and_extract_html(url)
    print(f"Extracted HTML length: {len(extracted_html)}")