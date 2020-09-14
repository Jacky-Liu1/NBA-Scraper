from selenium import webdriver

BASE_URL = 'https://www.nba.com/'

def get_chrome_web_driver(options):
  return webdriver.Chrome('./chromedriver', options=options)

def get_web_driver_options():
  return webdriver.ChromeOptions()

def set_ignore_certificate_error(options):   
  options.add_argument('--ignore-certificate-errors')

def set_browser_as_incognito(options):
  options.add_argument('--incognito')

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
    players_links = self.get_players_links()
    print(f'Found links for {len(players_links)} players')
    players_data = self.get_players_data(players_links)


  def get_players_data(self, players_links):
    pass

  def get_players_links(self):
    print('Searching players data...')
    self.driver.get(f"{self.base_url}/players")     # Goes to nba.com/players
    player_left_block = self.driver.find_elements_by_id("player-left-block")  # target parent 
    players_links = []
    try:
      players_list = player_left_block[0].find_elements_by_tag_name("a")        # target child
      players_links = [player.get_attribute('href') for player in players_list]  # get players link
      return players_links
    except Exception as e:
      print("Failed to get players data")
      print(e)
      return players_links


if __name__ == '__main__':
  nba = NbaApi(BASE_URL)
  nba.run()
