# keiojp-scraper

Scrape, take a screenshot of news, and post it to Slack every hour.

*This repository does not have any relationship with keio.jp portal site.

## requirement/setup
- python3
- venv
- some packages (see `requirements.md`)
- google chrome
- `config.ini`

To make `config.ini`, refer to the `config.ini.example`.

### to install venv packages
```
python3 -m venv keiojp-scraper
source keiojp-scraper/venv/activate.fish
pip install -r requirements.txt
```

### to get google chrome
```
curl https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-beta
```

## run
Use screen or something to keep session.

```
source keiojp-scraper/venv/activate.fish
python3 ./scrape.py
```
