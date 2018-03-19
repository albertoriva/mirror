# Mirror

<strong>mirror.py</strong> is a simple tool to keep files up-to-date by comparing them with a master copy on a remote server. It's a tiny, bare-bones, simple version of tools like cvs and subversion. Features:

* Extremely easy to set up and use;
* Cross-platform;
* Can be integrated in Python applications;
* Handles files, directories, and permissions;
* Works over HTTP/HTTPS;
* Totally free.

Limitations:

* Does not support client-to-server commit;
* Limited authentication support;
* Always downloads whole files if modified (i.e. does not merge local and remote changes).

## Arguments

<strong>mirror.py</strong> is invoked in two different ways, depending on whether it is being used on the server (to set up a repository) or on the client (to synchronize local files with the repository). Server-side invocation:

```
mirror.py -i [options] files...

options:
  -f F | Use F as the name for the file list file (default: .FILELIST)
  -c C | Use C as the name for the configuration file (default: .mirror)
```

## Usage
### Server side

On the server side, mirror.py needs to create a "file list", ie a file containing details of all the files and directories in the repository. This file should be recreated every time a file in the repository is modified. Its name is ".FILELIST" by default, but this can be changed with the -f command-line option or through the configuration file (see below).

Steps to set up a repository on a web server:

* Create a directory for the repository under the server's web space;
* Copy the required files (including subdirectories if appropriate) under the repository directory;
* Ensure that all files and directories are readable by the httpd process;
* Optionally: create a configuration file specifying an alternative name for the
