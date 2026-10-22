## Working with containers

### Running specific commands within a container

We saw earlier that we can use the `apptainer inspect` command to see the run script that a container is configured to run by default. What if we want to run a different command within a container, or we want to open a shell within a container that we can interact with?

If we know the path of an executable that we want to run within a container, we can use the `apptainer exec` command. For example, using the `hello-world.sif` container that we've already pulled from Docker Hub, we can run the following:

~~~
$ apptainer exec hello-world.sif /bin/echo Hello World!
~~~
{: .language-bash}

~~~
FATAL:   stat /bin/echo: no such file or directory
~~~
{: .output}

Here we see that a container has been started from the `hello-world.sif` image and the `/bin/echo` command was not found. The command provided an error and the container has terminated.

## Exercise: Running a different command within the "hello-world" container
~~~
Q: Can you run a container based on the `hello-world.sif` image that **replicates the run command**?
~~~


### Running a shell within a container

If you want to open an interactive shell within a container, apptainer provides the `apptainer shell` command. Let's download a Ubuntu image from Docker Hub:

~~~
$ apptainer pull ubuntu.sif docker://ubuntu
~~~
{: .language-bash}

Again, using the `ubuntu.sif` image, and within our `test` directory, we can run a shell within a container from the hello-world image:

~~~
$ apptainer shell ubuntu.sif
~~~
{: .language-bash}

~~~
Apptainer> whoami
[<your username>]
Apptainer> ls
hello-world.sif
ubuntu.sif
Apptainer> 
~~~
{: .output}

As shown above, we have opened a shell in a new container started from the `ubuntu.sif` image.

#### Exercise: Running a shell inside a apptainer container
~~~
Q: What do you notice about the output of the above commands entered within the apptainer container shell?
 
Q: How would some programs behave?  Try `cat /etc/os-release` and `uname -a`.
~~~

Use the `exit` command to exit from the container shell.

### Users, files and directories within a apptainer container

The first thing to note is that when you run `whoami` within the container you should see the username that you are signed in as on the host system when you run the container. For example, if my username is `c.username`:

~~~
$ apptainer shell ubuntu.sif
apptainer> whoami
c.username
~~~
{: .language-bash}

When the container is started, apptainer appends the relevant user and group lines from the host system to the `/etc/passwd` and `/etc/group` files within the container.

apptainer also _binds_ some directories from the host system where you are running the `apptainer` command into the container that you're starting. Note that this bind process isn't copying files into the running container, it is simply making an existing directory on the host system visible and accessible within the container environment. If you write files to this directory within the running container, when the container shuts down, those changes will persist in the relevant location on the host system.

There is a default configuration of which files and directories are bound into the container but ultimate control of how things are set up on the system where you're running apptainer is determined by the system administrator.

#### Exercise: Files in apptainer containers
~~~
Q: What do you notice about the ownership of files in a container started from the ubuntu image? (e.g. take a look at the ownership of files in the root directory (`/`))
 
Q: In this container, try overwriting the `/environment` file. What do you notice?

Q: In your home directory within the container shell, try and create a simple text file. Is it possible to do this? If so, why? If not, why not?! If you can successfully create a file, what happens to it when you exit the shell and the container shuts down?
~~~

Depending on the setup you may be able to control which directories are mounted via the `--bind/--no-mount` command or the `APPTAINER_BINDPATH` environment variable

## Using Docker images with apptainer

apptainer can use Docker images as seen earlier, opening up access to a huge number of existing container images available on [Docker Hub](https://hub.docker.com/) and other registries.

While apptainer doesn't support running Docker images directly, it can pull them from Docker Hub and convert them into a suitable format for running via apptainer. When you pull a Docker image, apptainer pulls the slices or _layers_ that make up the Docker image and converts them into a single-file apptainer SIF image.

For example, moving on from the simple _Hello World_ examples that we've looked at so far, let's pull one of the [official Docker Python images](https://hub.docker.com/_/python). We'll use the image with the tag `3.8.2-slim-buster` which has Python 3.8.2 installed on Debian's [Buster](https://www.debian.org/releases/buster/) (v10) Linux distribution:

~~~
$ apptainer pull python-3.8.2.sif docker://python:3.8.2-slim-buster
~~~
{: .language-bash}

~~~
INFO:    Converting OCI blobs to SIF format
INFO:    Starting build...
Getting image source signatures
Copying blob 54fec2fa59d0 done
Copying blob cd3f35d84cab done
Copying blob a0afc8e92ef0 done
Copying blob 9691f23efdb7 done
Copying blob 6512e60b314b done
Copying config 1c498e093b done
Writing manifest to image destination
Storing signatures
2020/12/13 23:43:09  info unpack layer: sha256:54fec2fa59d0a0de9cd2dec9850b36c43de451f1fd1c0a5bf8f1cf26a61a5da4
2020/12/13 23:43:10  info unpack layer: sha256:cd3f35d84caba5a287676eeaea3d371e1ed5af8c57c33532228a456e0505b2d5
2020/12/13 23:43:10  info unpack layer: sha256:a0afc8e92ef0f5e56ddda03f8af40a4396226443a446e457ab6ed2dcdec62619
2020/12/13 23:43:11  info unpack layer: sha256:9691f23efdb7fd2829d06ad8fb9c8338487c183bb1aefa0d737cece2a612f51b
2020/12/13 23:43:11  info unpack layer: sha256:6512e60b314b980bce8ece057d15292db0f50ca12dbe6dd5752e1e54c64ccca2
INFO:    Creating SIF file...
~~~
{: .output}

Note how we see apptainer saying that it's "_Converting OCI blobs to SIF format_". We then see the layers of the Docker image being downloaded and unpacked and written into a single SIF file. Once the process is complete, we should see the python-3.8.2.sif image file in the current directory.

We can now run a container from this image as we would with any other apptainer image.

#### Exercise: Running the Python 3.8.2 image that we just pulled from Docker Hub
~~~
 Try running the Python 3.8.2 image. What happens?
~~~ 
In addition to running a container and having it run the default run script, you could also start a container running a shell in case you want to undertake any configuration prior to running Python. This is covered in the following exercise:

####  Exercise: Open a shell within a Python container
~~~
Try to run a shell within a apptainer container based on the `python-3.8.2.sif` image. That is, run a container that opens a shell rather than the default Python interactive console as we saw above.

See if you can find more than one way to achieve this.

Within the shell, try starting the Python interactive console and running some Python commands.
~~~
