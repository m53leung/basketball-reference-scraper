from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from string import ascii_lowercase
import csv
import time
import os
import re

from stats import PLAYER_SEASON_STAT_COLUMNS, AWARDS, ALL_NBA, ALL_STAR

time_stamp = time.strftime('%Y-%m-%d_%H-%M-%S')
if not os.path.isdir('data'):
    os.mkdir('data')
    
os.mkdir(f'data/{time_stamp}')
os.mkdir(f'data/{time_stamp}/regular_season')

options = Options()
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=options)

# Scrape data for a player page
def scrape_player(url: str):
    driver.get(url)
    name = driver.find_element(by=By.XPATH, value='//*[@id="meta"]//h1').text
    print(f'Scraping data for {name}...')

    total_stats_table = driver.find_element(by=By.XPATH, value='//*[@id="totals_stats"]')
    stats_by_season_rows = total_stats_table.find_elements(by=By.XPATH, value='tbody/tr')
    id = url.split('/')[-1].split('.')[0]
    with open(f'data/{time_stamp}/regular_season/{id}({name}).csv', 'x') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(PLAYER_SEASON_STAT_COLUMNS + AWARDS + [ALL_STAR, ALL_NBA])

        for row in stats_by_season_rows:
            # year = int(row.find_element(by=By.XPATH, value='*[@data-stat="year_id"]').text.split('-')[0])
            if len(row.find_elements(by=By.XPATH, value='*')) != 32:
                continue

            row_stats = []

            for stat_name in PLAYER_SEASON_STAT_COLUMNS:
                row_stats.append(row.find_element(by=By.XPATH, value=f'*[@data-stat="{stat_name}"]').text)

            awards_dict = dict([[award, 0] for award in (AWARDS + [ALL_STAR, ALL_NBA])])
            awards = row.find_element(by=By.XPATH, value='*[@data-stat="awards"]').text.split(',')

            for award in awards:
                award_split = award.split('-')
                if award_split[0] in AWARDS:
                    awards_dict[award_split[0]] = int(award_split[1])

                if award == ALL_STAR:
                    awards_dict[ALL_STAR] = 1

                match = re.search('^NBA([1-9])$', award)
                if match:
                    awards_dict[ALL_NBA] = int(match.group(1))

            for award in AWARDS + [ALL_STAR, ALL_NBA]:
                row_stats.append(awards_dict[award])

            csv_writer.writerow(row_stats)

# Scrape data for players of this letter
def scrape_players_by_letter(letter: str):
    print(f'Scraping data for {letter} players...')
    driver.get(f'https://www.basketball-reference.com/players/{letter}/')

    header = driver.find_element(by=By.XPATH, value='//*[@id="players_sh"]/h2')
    num_players = int(header.text.split()[0])

    player_links = driver.find_elements(by=By.XPATH, value='//*[@id="players"]/tbody/tr/th//a')
    player_urls = [link.get_attribute('href') for link in player_links]

    assert num_players == len(player_links)
    print(f'{len(player_links)} players found')

    for url in player_urls:
        scrape_player(url)

# for letter in ascii_lowercase:
#     scrape_players_by_letter(letter)
# scrape_player('https://www.basketball-reference.com/players/j/jamesle01.html')
# scrape_player('https://www.basketball-reference.com/players/u/ubileed01.html')
scrape_players_by_letter('a')

driver.quit()
