from selenium import webdriver
import json
from selenium.common.exceptions import NoSuchElementException

BASE_URL = 'https://www.nba.com/'

def get_chrome_web_driver(options):
  return webdriver.Chrome('./chromedriver', options=options)

def get_web_driver_options():
  return webdriver.ChromeOptions()

def set_ignore_certificate_error(options):   
  options.add_argument('--ignore-certificate-errors')

def set_browser_as_incognito(options):
  options.add_argument('--ignore-certificate-errors')

class NbaApi:
  def __init__(self, base_url):
    self.base_url = base_url
    options = get_web_driver_options()
    set_ignore_certificate_error(options)
    set_browser_as_incognito(options)
    self.driver = get_chrome_web_driver(options)

  def run(self):
    print("Running script...")
    self.driver.get(self.base_url)
    print("Opened NBA.com")
    players_id = self.get_players_id()
    print(f'Found links for {len(players_id)} players')
    players_data = self.get_players_data(players_id)
    print("Generating json report...")
    with open('nba_players_data.json', 'w') as f:
      json.dump(players_data, f)
    print("Finished")


  def get_players_data(self, players_id):
    players_data = {}
    print("Getting players' data")
    for i, id in enumerate(players_id):   ##### Get rid of enumerate and i to grab all players
      self.driver.get(f"https://stats.nba.com/player/{id}/?Season=2019-20&SeasonType=Regular%20Season")
      first_name = self.driver.find_element_by_class_name("player-summary__first-name").text
      last_name = self.driver.find_element_by_class_name("player-summary__last-name").text
      name = first_name + "_" + last_name
      print(name)
      player_personal_info = self.get_player_personal_info(id)  # name, height, weight, age, college, years_in_nba, etc...
      player_career_stats = self.get_player_career_stats(id) # mpg, fg%, 3p%, points, assists, blocks, off rating, usg %, etc...
      players_data[name] = {**player_personal_info, **player_career_stats} # merge dictionary
      # if i > 5:     # this will only grab the first 5 players 
      #  break
    return players_data

  def get_player_career_stats(self, id):
    found_player_stats = False
    while not found_player_stats:
      try:
        info = self.driver.find_elements_by_class_name("nba-stat-table__overflow")[0:2] # this returns an array of 5 tables of stats
        player_stats = {}
        table1 = info[0].find_elements_by_tag_name("tbody")[0].find_elements_by_tag_name("tr") # returns stats from each season
        table2 = info[1].find_elements_by_tag_name("tbody")[0].find_elements_by_tag_name("tr") # returns advance stats
        for i in range(len(table1)):
          season_stats = table1[i].text.split()
          advance_stats = table2[i].text.split()
          player_stats[season_stats[0]] = {  # the key is the year of the season
            "team": season_stats[1],
            "minutes_per_game": season_stats[3],
            "points_per_game": season_stats[4],
            "field_goals_made": season_stats[5],
            "field_goals_attempted": season_stats[6],
            "field_goal_percentage": season_stats[7],
            "threes_made": season_stats[8],
            "threes_attempted": season_stats[9],
            "three_percentage": season_stats[10],
            "free_throws_made": season_stats[11],
            "free_throws_attempted": season_stats[12],
            "free_throw_percentage": season_stats[13],
            "offensive_rebounds_per_game": season_stats[14],
            "defensive_rebounds_per_game": season_stats[15],
            "rebounds_per_game": season_stats[16],
            "assists_per_game": season_stats[17],
            "turnovers_per_game": season_stats[18],
            "steals_per_game": season_stats[19],
            "blocks_per_game": season_stats[20],
            "fouls_per_game": season_stats[21],
            "plus_minus_per_game": season_stats[25],
            "offensive_rating": advance_stats[4],
            "defesnive_rating": advance_stats[5],
            "net_rating": advance_stats[6],
            "effective_field_goal_percentage": advance_stats[14],
            "usage_percentage": advance_stats[16],
            "player_impact_estimate": advance_stats[18]
          }
        return player_stats

      except NoSuchElementException:
        self.driver.get(f"https://stats.nba.com/player/{id}/?Season=2019-20&SeasonType=Regular%20Season")
        print('trying to get player season stats again...')
      except Exception as e:
        print(e)
        print(f'Can not get player season info for id {id}')
        print('trying to get player season stats again...')

  def get_player_personal_info(self,id):
    found_player_personal_info = False
    while not found_player_personal_info:
      try: 
        info = self.driver.find_elements_by_class_name("player-stats__stat-value")
        """
        info returns an array
        index 0 - career points per game
        index 1 - career rebounds per game
        index 2 - career assists per game
        index 3 - career PIE per game (player impact estimate)
        index 4 - player height (feet - inches)
        index 5 - player weight
        index 6 - player age
        index 7 - player birth date
        index 8 - player college/nationality
        index 9 - player draft pick
        index 10 - player years of experience in the NBA
        """
        
        height = self.feet_and_inches_to_inches(info[4].text)
        weight = info[5].text[:3] # we only want the numbers not lbs
        age = info[6].text
        prior = info[8].text 
        exp = info[10].text[:2]
        player_personal_info = {
          "height": height,
          "weight": weight,
          "age": age,
          "prior": prior,
          "exp": exp,
        }
        return player_personal_info

      except Exception as e:
        print(e)
        print(f'Can not get player personal info for id {id}')
        print('trying to find player personal info again...')


  def feet_and_inches_to_inches(self, feet_and_inches):
    arr = feet_and_inches.split('-')
    feet = int(arr[0])
    inches = int(arr[1])
    return feet * 12 + inches

  def get_players_id(self):
    print('Searching players...')
    players_id = []
    found_players_id = False
    while not found_players_id:
      try:
        self.driver.get(f"{self.base_url}/players")     # Goes to nba.com/players
        player_left_block = self.driver.find_elements_by_id("player-left-block")  # target parent 
        players_list = player_left_block[0].find_elements_by_tag_name("a")        # target child 
        print("Getting players id...")
        players_id = [player.get_attribute('href').rsplit('/',1)[1] for player in players_list]  # get players id
        if len(players_id)>0:
          found_players_id = True
          return players_id
      except Exception as e:
        print("Failed to get players data")
        print(e)
        print("Trying again...")
    




 

if __name__ == '__main__':
  nba = NbaApi(BASE_URL)
  nba.run()




