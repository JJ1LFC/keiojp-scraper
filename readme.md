# keiojp-scraper

Scrape, take a screenshot or update diff of news, and post it to Slack.

*This repository does not have any relationship with keio.jp portal site.

## requirement/setup
- python3
- venv
- some packages (see `requirements.txt`)
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

## text mode
When text mode is enabled (default by `config.ini.example`), text diff of news is posted instead of the screenshot.
![](https://user-images.githubusercontent.com/38905988/90960798-2ce0ee80-e4df-11ea-97cd-80a63e4904b5.png)

To disable text mode, set `textmode` in `[global]` of `config.ini` to `false`.

## run
Use screen or something to keep session.

```
source keiojp-scraper/venv/activate.fish
python3 ./scrape.py
```
