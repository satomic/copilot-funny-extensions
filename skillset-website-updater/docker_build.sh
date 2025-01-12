cd ..

docker build --build-arg APP_FOLDER=skillset-website-updater -t satomic/skillset:`date +'%Y%m%d'` -f skillset-website-updater/Dockerfile .