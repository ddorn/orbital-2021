rm -r **/__pycache__
rm -r dist
mkdir dist
#cp -r assets states *.{py,md,nix} dist
git ls-files | zip -r --names-stdin dist/game.zip
