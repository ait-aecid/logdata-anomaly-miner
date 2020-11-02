This directory contains files enabled to be included in the analysis
pipeline configuration. The files are made available by including
this directory within the site packages.

If you have objections enabling all the python site packages stored
on this host within a process running with elevated privileges,
you can also include only some site package components by placing
symlinks here, e.g.

ln -s /usr/lib/python3.6/dist-packages/pytz conf-enabled/pytz
