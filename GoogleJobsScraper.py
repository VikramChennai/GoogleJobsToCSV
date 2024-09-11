from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from bs4 import BeautifulSoup
import csv
import os
import pandas as pd
from OpenAIConfig import syncAzureOpenAIClient
from dotenv import load_dotenv

load_dotenv()


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
        for _ in range(40):  # Adjust the number of scrolls as needed
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
        
        # Parse the infinity-scrolling content and save popup HTML
        infinity_scrolling = soup.find('infinity-scrolling')
        if infinity_scrolling:
            job_listings = infinity_scrolling.find_all('a', class_='MQUd2b')

            print(f"Job listings: {job_listings}")
            
            filename = "job_details.csv"
            file_exists = os.path.isfile(filename)
            
            with open(filename, "a", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['Title', 'Company', 'Location', 'Posted Date', 'Job Type', 'Description', 'Qualifications', 'Responsibilities'])
            
            for job in job_listings:
                title = job.find('div', class_='tNxQIb PUpOsf').text.strip()
                
                # Find the job element
                job_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//a[contains(@class, 'MQUd2b') and .//div[contains(text(), '{title}')]]"))
                )
                
                # Scroll the element into view
                driver.execute_script("arguments[0].scrollIntoView(true);", job_element)
                time.sleep(1)  # Short pause to allow any animations to complete
                
                # Wait for the element to be clickable
                clickable_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//a[contains(@class, 'MQUd2b') and .//div[contains(text(), '{title}')]]"))
                )
                
                # Click the element using JavaScript
                driver.execute_script("arguments[0].click();", clickable_element)
                
                time.sleep(2)  # Wait for the job details to load

                # Extract the job details HTML
                job_details_html = driver.find_element(By.CSS_SELECTOR, 'div[jsname="dn277e"]').get_attribute('outerHTML')
                
                # Parse the job details HTML
                job_details_soup = BeautifulSoup(job_details_html, 'html.parser')
                
                # Extract job details
                company = job_details_soup.find('div', class_='RorkHe').text.strip()
                print("\nCompany:")
                print(company)
                print()

                location = job_details_soup.find('div', class_='waQ7qe').text.strip()
                print("Location:")
                print(location)
                print()
                
                rcztb_spans = job_details_soup.find_all('span', class_='RcZtZb')
                #print(f"Debug - RcZtZb spans: {rcztb_spans}")
                
                posted_date = rcztb_spans[0].text.strip() if rcztb_spans else "N/A"
                print("Posted Date:")
                print(posted_date)
                print()

                job_type = rcztb_spans[1].text.strip() if len(rcztb_spans) > 1 else "N/A"
                print("Job Type:")
                print(job_type)
                print()
                
                description = job_details_soup.find('span', class_='us2QZb').text.strip()
                print("Description:")
                print(description)
                print()
                
                # Extract qualifications and responsibilities
                highlights = job_details_soup.find_all('ul', class_='zqeyHd')
                qualifications = []
                responsibilities = []
                
                if len(highlights) > 0:
                    qualifications = [li.text for li in highlights[0].find_all('li', class_='LevrW')]
                    print("Qualifications:")
                    for qual in qualifications:
                        print(f"- {qual}")
                    print()

                if len(highlights) > 1:
                    responsibilities = [li.text for li in highlights[1].find_all('li', class_='LevrW')]
                    print("Responsibilities:")
                    for resp in responsibilities:
                        print(f"- {resp}")
                    print()

                print("------------------------")  # Separator for readability
                
                # Append the extracted data to the CSV file
                with open(filename, "a", newline='', encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([title, company, location, posted_date, job_type, description, '; '.join(qualifications), '; '.join(responsibilities)])
                
                print(f"Job details for '{title}' appended to '{filename}'.")
            
            print("All job details have been saved.")
        
        print("Press Enter to close the browser...")
        input()

        return html

    finally:
        driver.quit()

def deduplicate_csv(filename):
    # Read the CSV file
    df = pd.read_csv(filename)
    
    # Drop duplicate rows based on exact matches of 'Description' and 'Company'
    df_deduped = df.drop_duplicates(subset=['Description', 'Company'])
    
    # Save the deduplicated DataFrame back to CSV
    df_deduped.to_csv(filename, index=False)
    
    print(f"Deduplicated CSV saved to {filename}")
    print(f"Original row count: {len(df)}")
    print(f"Deduplicated row count: {len(df_deduped)}")

def extract_tools_from_job_details(filename):
    # Read the CSV file
    df = pd.read_csv(filename)
    
    # Add a new column for tools/software if it doesn't exist
    if 'Tools/Software' not in df.columns:
        df['Tools/Software'] = ''
    
    # Function to extract tools using LLM
    def get_tools_from_llm(text):
        prompt = f"Extract the tools and software mentioned in the following job description. Only list the names of the tools and software, separated by commas:\n\n{text}"
        response = syncAzureOpenAIClient.chat.completions.create(
            model=os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME'),
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts tools and software from job descriptions."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    
    # Iterate through each row and extract tools
    for index, row in df.iterrows():
        # Combine relevant columns
        job_text = f"{row['Description']} {row['Qualifications']} {row['Responsibilities']}"
        
        # Extract tools using LLM
        tools = get_tools_from_llm(job_text)
        
        # Update the 'Tools/Software' column
        df.at[index, 'Tools/Software'] = tools
        
        print(f"Processed job {index + 1}/{len(df)}")
    
    # Save the updated DataFrame back to CSV
    df.to_csv(filename, index=False)
    print(f"Updated CSV with tools/software saved to {filename}")

if __name__ == "__main__":
    #url = "https://www.google.com/search?q=data+engineer+jobs&ibp=htl;jobs"
    #extracted_html = open_dev_tools_and_extract_html(url)
    #print(f"Extracted HTML length: {len(extracted_html)}")
    
    # Deduplicate the CSV file
    #deduplicate_csv("job_details.csv")
    
    # Extract tools/software from job details
    extract_tools_from_job_details("job_details.csv")