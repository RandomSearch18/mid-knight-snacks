# Mid-Knight Snacks

<p align="center">
  <img hspace="4" src="https://img.shields.io/badge/a%20counterspell%20game-FEC2FB%3F?style=for-the-badge&logo=undertale&logoColor=ffffff&color=FF4186" alt="A Counterspell Game">
  <img hspace="4" src="https://img.shields.io/badge/made%20for%20high%20seas-FEC2FB?style=for-the-badge&logo=hackclub&logoColor=1C4188" alt="Made for High Seas">
</p>

A castle- and beef-themed game, made during the [Counterspell](https://counterspell.hackclub.com/) game jam in Autumn 2024.

## How to run the game

1. Clone the repository
2. Create a venv if you want (`python3 -m venv .venv` and `source .venv/bin/activate`)
3. Install Pygame with `python3 -m pip install -r requirements.txt`
4. `python3 main.py`

## Demo video

[Download or view the video (1.5 MB, mp4)](./demos/Mid-Knight%20Snacks.mp4)

<video controls src="demos/Mid-Knight Snacks.mp4" title="Mid-Knight Snacks demo video"></video>

## Screenshot

![Screenshot of the game running on Linux](./demos/mid-knight-snacks.png)

## Building for the web

Following the [Pygbag documentation](https://pygame-web.github.io/wiki/pygbag/#running-your-project-in-your-own-browser):

1. Install Pygbag: `python3 -m pip install pygbag`
2. Build and serve the game: `python3 -m pygbag .`
3. Visit <http://localhost:8000> in your browser and wait for the game to load

To just build the files without serving them, run `python -m pygbag --build .`

## Credits

Developed by Andrew, Mish and Morgan.
