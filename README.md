# Mirror

<strong>mirror.py</strong> is a simple tool to keep files up-to-date by comparing them with a master copy on a remote server. It's a tiny, bare-bones, simple version of tools like cvs and subversion. Features:

* Extremely easy to set up and use;
* Handles files, directories, and permissions;
* Works over HTTP/HTTPS.

Limitations:

* Does not support client-to-server commit.
* Always downloads whole files if modified (i.e. does not merge local and remote changes.
