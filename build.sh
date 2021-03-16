rm -r dist
mkdir dist
git ls-files | zip -r --names-stdin dist/game.zip
poetry run pyinstaller --noconsole --add-data assets/:assets --onefile main.py
wine pyinstaller.exe --noconsole --add-data assets\;assets --onefile main.py