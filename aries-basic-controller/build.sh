echo "Building :latest image"
docker build -t didx-ai/aries-basic-controller:latest .

# TODO: alter this docker tag name to match account in DockerHub
#echo "pushing image to Registry"
#docker push dibbsza/oidc-controller-dot-net:latest
