#!/usr/bin/env python
# coding: utf-8

# # GitHub Repository Scraper

# This Jupyter Notebook scrapes GitHub repositories for various topics and stores the data in CSV files. It uses web scraping techniques to extract repository information from GitHub topic pages, such as repository name, username, star count, and URL. The scraped data is organized by topic, and each topic's repositories are saved in a separate CSV file within the 'data' directory.
# 
# The code uses libraries like Requests, BeautifulSoup, and Pandas to facilitate the scraping and data manipulation processes. You can run the `main()` function to initiate the scraping of topics and repositories.
# 
# Author: Ahmed Gamal
# Date: 8/26/2023
# 

# In[1]:


# Import necessary libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Function to make an HTTP GET request to a given URL and return the page contents as a BeautifulSoup object
def get_page_contents(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception('Failed to load the page {}'.format(url))
    return BeautifulSoup(response.text, "html.parser")

# Function to parse star counts (e.g., '1.2k' -> 1200)
def parse_star_count(stars_str):
    stars_str = stars_str.strip()
    if stars_str[-1] == 'k':
        return int(float(stars_str[:-1]) * 1000)
    return int(stars_str)

# Function to extract repository information from a topic page
def get_repo_info(h3_tag, star_tag, base_url):
    a_tags = h3_tag.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url = base_url + a_tags[1]['href']
    stars = parse_star_count(star_tag.text.strip())
    return username, repo_name, stars, repo_url

# Function to scrape and store repositories for a specific topic
def scrape_topic(topic_url, path):
    if os.path.exists(path):
        print('The file {} already exists. Skipping...'.format(path))
        return
    topic_doc = get_page_contents(topic_url)
    
    # Initialize a dictionary to store repository information
    topic_repos_dict = {
        'username': [],
        'repo_name': [],
        'stars': [],
        'repo_url': []
    }

    # Get the h3 tags containing repo name, username, repo URL
    h3_selection_class = "f3 color-fg-muted text-normal lh-condensed"
    repo_tags = topic_doc.find_all('h3', {'class': h3_selection_class})
    
    # Get the star tags
    star_selector = "Counter js-social-count"
    star_tags = topic_doc.find_all('span', {'class': star_selector})

    # Get repo info and populate the dictionary
    for i in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[i], star_tags[i], 'https://github.com')
        topic_repos_dict['username'].append(repo_info[0])
        topic_repos_dict['repo_name'].append(repo_info[1])
        topic_repos_dict['stars'].append(repo_info[2])
        topic_repos_dict['repo_url'].append(repo_info[3])

    # Create a DataFrame from the dictionary and save it as a CSV file
    topic_df = pd.DataFrame(topic_repos_dict)
    topic_df.to_csv(path, index=None)

# Function to scrape and store information for all topics and their repositories
def scrape_topics_repos():
    print('Scraping list of topics')
    topic_url = 'https://github.com/topics'
    doc = get_page_contents(topic_url)
    
    topics_dict = {
        'title': get_topic_titles(doc),
        'description': get_topic_descs(doc),
        'url': get_topic_urls(doc)
    }

    topics_df = pd.DataFrame(topics_dict)
    
    # Create a directory to store data if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Loop through topics and scrape repositories for each
    for index, row in topics_df.iterrows():
        print('Scraping top repositories for {}'.format(row['title']))
        scrape_topic(row['url'], 'data/{}.csv'.format(row['title']))

# Function to get topic titles from the page contents
def get_topic_titles(doc):
    selection_class = "f3 lh-condensed mb-0 mt-1 Link--primary"
    topic_title_tags = doc.find_all("p", {"class": selection_class})
    topic_titles = [tag.text.strip() for tag in topic_title_tags]
    return topic_titles

# Function to get topic descriptions from the page contents
def get_topic_descs(doc):
    desc_selector = "f5 color-fg-muted mb-0 mt-1"
    topic_desc_tags = doc.find_all("p", {"class": desc_selector})
    topic_descs = [tag.text.strip() for tag in topic_desc_tags]
    return topic_descs

# Function to get topic URLs from the page contents
def get_topic_urls(doc):
    topic_url_selector = "no-underline flex-1 d-flex flex-column"
    topic_link_tags = doc.find_all('a', {'class': topic_url_selector})
    base_url = "https://github.com"
    topic_urls = [base_url + tag['href'] for tag in topic_link_tags]
    return topic_urls

# Main function to start the scraping process
def main():
    scrape_topics_repos()

if __name__ == "__main__":
    main()


# In[ ]:




