# Getting Started

Sign in to the remote platform, that you have been provided access to. Check that the `apptainer` command is available in your terminal:

> ## Loading a module

~~~
$ module load apptainer
~~~
{: .language-bash}


~~~
$ apptainer --version
~~~
{: .language-bash}

~~~
apptainer version 1.5.3
~~~
{: .output}

Depending on the version of Apptainer installed on your system, you may see a different version. At the time of writing, `1.5.4` is the latest release of Apptainer.


Let's begin by creating a `test` directory, changing into it and _pulling_ a test _Hello World_ image from Docker:

~~~
$ mkdir test
$ cd test
$ apptainer pull hello-world.sif docker://hello-world:latest
~~~
{: .language-bash}

~~~
INFO:    Converting OCI blobs to SIF format
INFO:    Starting build...
Getting image source signatures
Copying blob 719385e32844 done
Copying config 0dcea989af done
Writing manifest to image destination
Storing signatures
2023/12/11 22:09:54  info unpack layer: sha256:719385e32844401d57ecfd3eacab360bf551a1491c05b85806ed8f1b08d792f6
~~~
{: .output}

What just happened?! We pulled a SIF image from Docker using the `apptainer pull` command and directed it to store the image file using the name `hello-world.sif`. If you run the `ls` command, you should see that the `hello-world.sif` file is now in your current directory. This is our image and we can now run a container based on this image:

~~~
$ apptainer run hello-world.sif
~~~
{: .language-bash}

~~~
Hello from Docker!
...
~~~
{: .output}

The above command ran the _hello-world_ container from the image we downloaded from Docker and the resulting output was shown. 


How did the container determine what to do when we ran it?! What did running the container actually do to result in the displayed output?

When you run a container from an image without using any additional command line arguments, the container runs the default run script that is embedded within the image. This is a shell script that can be used to run commands, tools or applications stored within the image on container startup. We can inspect the image's run script using the `apptainer inspect` command:

~~~
$ apptainer inspect -r hello-world.sif
~~~
{: .language-bash}

~~~
#!/bin/sh
OCI_ENTRYPOINT=''
OCI_CMD='"/hello"'
...
~~~
{: .output}

This shows us the script within the `hello-world.sif` image configured to run by default when we use the `apptainer run` command.

## apptainer's image cache

While apptainer doesn't have a local image repository in the same way as Docker, it does cache downloaded image files. As we saw in the previous episode, images are simply `.sif` files stored on your local disk. 

If you delete a local `.sif` image that you have pulled from a remote image repository and then pull it again, if the image is unchanged from the version you previously pulled, you will be given a copy of the image file from your local cache rather than the image being downloaded again from the remote source. This removes unnecessary network transfers and is particularly useful for large images which may take some time to transfer over the network. To demonstrate this, remove the `hello-world.sif` file stored in your `test` directory and then issue the `pull` command again:

~~~
$ rm hello-world.sif
$ apptainer pull hello-world.sif docker://hello-world
~~~
{: .language-bash}

~~~
INFO:    Using cached SIF image
~~~
{: .output}

As we can see in the above output, the image has been returned from the cache and we don't see the output that we saw previously showing the image being downloaded from apptainer Hub.

How do we know what is stored in the local cache? We can find out using the `apptainer cache` command:

~~~
$ apptainer cache list
~~~
{: .language-bash}

~~~
There are 1 container file(s) using 44.00 KiB and 3 oci blob file(s) using 3.36 KiB of space
Total space used: 47.36 KiB
~~~
{: .output}

This tells us how many container files are stored in the cache and how much disk space the cache is using but it doesn't tell us _what_ is actually being stored. To find out more information we can add the `-v` verbose flag to the `list` command:

~~~
$ apptainer cache list -v
~~~
{: .language-bash}

~~~
NAME                     DATE CREATED           SIZE             TYPE
0dcea989af054c9b5ab290   2023-12-11 22:16:39    0.57 KiB         blob
719385e32844401d57ecfd   2023-12-11 22:16:39    2.40 KiB         blob
ad7c8b818cf3016b2b6437   2023-12-11 22:16:39    0.39 KiB         blob
e28fc75c4cbf64761ce6dd   2023-12-11 22:16:40    44.00 KiB        oci-tmp

There are 1 container file(s) using 44.00 KiB and 3 oci blob file(s) using 3.36 KiB of space
Total space used: 47.36 KiB
~~~
{: .output}

This provides us with some more useful information about the actual images stored in the cache. In the `TYPE` column we can see that our image type is `blob` because it's a `docker` image that has been pulled from Docker Hub. 

> ## Cleaning the apptainer image cache
> We can remove images from the cache using the `apptainer cache clean` command. Running the command without any options will display a warning and ask you to confirm that you want to remove everything from your cache.
>
> You can also remove specific images or all images of a particular type. Look at the output of `apptainer cache clean --help` for more information.
{: .callout}

## Cache Location

Apptainer by default will use ~/.apptainer/cache which can cause issues if you have a quota limit on you home directory.

This can be overridden by the environment variable `APPTAINER_CACHEDIR`

~~~
$ echo $APPTAINER_CACHEDIR
~~~
{: .language-bash}

## References

https://github.com/ARCCA/intro_singularity/

\[1\] Gregory M. Kurzer, Containers for Science, Reproducibility and Mobility: Singularity P2. Intel HPC Developer Conference, 2017. Available at: https://www.intel.com/content/dam/www/public/us/en/documents/presentation/hpc-containers-singularity-advanced.pdf
