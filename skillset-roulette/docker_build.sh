cd ..

export APP_FOLDER=skillset-roulette

docker build \
  --build-arg APP_FOLDER=$APP_FOLDER \
  -t satomic/roulette:`date +'%Y%m%d'` \
  -f $APP_FOLDER/Dockerfile .