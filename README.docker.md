# Docker Container for fskintra

This is a Docker container for running fskintra.

Run Directly:

    docker run -t -i \
               -v </host/eg/home/user/.skoleintra>:/root/.skoleintra \
	       fskintra \
	       <command>

Where <command> is fskintra with options, e.g:

    fskintra -h        # for help
    fskintra --config  # to generate config - Remember to map host dir, see below
    fskintra -q        # to run quiet
    fskintra --password PASSWORD # to change password

and `</host/eg/home/user/.skoleintra>` is the folder on the docker host,
where the data are stored.

For general fskintra help: See https://github.com/svalgaard/fskintra
.... origin of the Docker: See https://github.com/bennyslbs/fskintra
