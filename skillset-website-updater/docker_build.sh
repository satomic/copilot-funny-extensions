cd ..

export APP_FOLDER=skillset-website-updater

docker build \
--build-arg APP_FOLDER=$APP_FOLDER \
-t satomic/skillset:`date +'%Y%m%d'` \
-f $APP_FOLDER/Dockerfile .