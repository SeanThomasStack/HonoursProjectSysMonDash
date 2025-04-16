hello,
once you get the docker file onto your linux distro
you will have to move it to where in the file system you want your container to run
once your happy with the layout open the terminal and navigate to the directory of the Docker file 
run the following commands (may be requred to use sudo or to install docker if not already done)

docker build -t sysmondash .
note that the "." is required in the command

docker run -p 5000:5000 sysmondash

once running you should navigate to http://localhost:5000 to see the dashboard
to see the recorded stat submission navigate to http://localhost:5000/snapshot
