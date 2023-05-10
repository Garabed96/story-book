Run Docker:
docker run -p 1122:1122 portfolio

Build Docker: 
docker build -t portfolio . 

Build a Docker Name:Tag, Tag represents the image, Name represents the Container
docker build -t portfolio:latest . 

Show Docker Images:
docker images 

Delete Docker Container:
docker rm <container_name/id>


Running Containers: docker ps

Stop Docker Container
docker stop <container_name/id>

To delete images make sure to delete container first****
