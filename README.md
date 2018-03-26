# Mirror

<strong>mirror.py</strong> is a simple tool to keep files up-to-date by comparing them with a master copy on a remote server. It is a tiny, bare-bones, simple version of tools like cvs and subversion. Features:

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

Options:
  -f F | Use F as the name for the file list file (default: .FILELIST)
  -c C | Use C as the name for the configuration file (default: .mirror)
```

Client-side invocation:

```
mirror.py [options]

Options:
  -f F | Use F as the name for the file list file (default: .FILELIST).
  -c C | Use C as the name for the configuration file (default: .mirror).
  -s S | Set source URL to S (required, unless specified in configuration file).
  -u U | Set username for Basic authentication to U.
  -p P | Set password for Basic authentication to P.
  -x   | Dry run: print operations to be performed, without actually performing them.
```

If the options -h or --help are present on the command-line, the program will print a usage message and exit.

## Configuration file

The configuration file is a simple text file containing lines of the form "key = value". The following two keys are currently defined:

```
filelist - specifies the name of the filelist file. This needs to be the same on the server and on the client. [Equivalent to -f option]
url - specifies the URL of the repository. [Equivalent to -s option]
username - specifies username for authentication. [Equivalent to -u option]
password - specifies password for authentication. [Equivalent to -p option]

```

## Usage
### Server side

On the server side, mirror.py needs to create a "file list", ie a file containing details of all the files and directories in the repository. This file should be recreated every time a file in the repository is modified. Its name is ".FILELIST" by default, but this can be changed with the -f command-line option or through the configuration file (using a name starting with a dot is recommended).

Detailed steps to set up a repository on a web server:

* Create a directory for the repository under the server's web space;
* Copy the required files (including subdirectories if appropriate) under the repository directory;
* Ensure that all files and directories are readable by the httpd process;
* Optionally: create a configuration file specifying an alternative name for the file list.
* Invoke mirror.py with the -i option followed by the list of files in the repository.

For example, let's assume we are setting up a repository on host <strong>myhost.org</strong> under the <strong>repos/myapp</strong> folder. The repository includes a number of files in the top-level directory, and two subdirectories: src/, containing files with extension .c, and doc/ containing files with extension .txt. To initialize this repository we should go to the repository directory and execute:

```
mirror.py -i * src/*.c doc/*.txt
```

Note that directories need to be explicitly included in the file list. In the previous example, the * takes care of that.

If a command-line argument starts with '@', the remainder of the argument is interpreted as the name of a file containing filenames to be added to the file list. So another way of accomplishing the result above would be to store all desired filenames into a file called e.g. repofiles, and then execute:
 
 ```
 mirror.py -i @repofiles
 ```
 
 ### Client side
 On the client, create a directory for the repository. Normally you would use the same name as on the server, in this case <strong>myapp</strong>. Then cd to this directory and execute:
 
 ```
 mirror.py -s http://myhost.org/repos/myapp/
 ```
 
 Alternatively, you can save the url to the configuration file as follows:
 
 ```
 url = http://myhost.org/repos/myapp/
 ```
 
 In this case, client-side invocation simply becomes:
 
 ```
 mirror.py
 ```
 
 The program will perform the following operations:
 
 * Download the file list from the server and save it locally (removing previous version if any);
 * Compare all entries in the file list with local files or directories;
 * If a directory in the file list does not exist locally, it is created;
 * If a file in the file list does not exist locally, or if the remote version is newer than the local version, the file is downloaded;
 * A message is printed to standard output showing whether the download was successful.

## Security

If the repository directory on the server is protected through Basic authentication, the client will need to provide username and password when submitting its requests. This can be done in two different ways:

* Specify username and password on the command-line, using the -u and -p options;
* Write username and password in the configuration file, using the _username_ and _password_ directives.

## Usage in code

You can include the functionality provided by <strong>mirror.py</strong> into your programs. This can be used, for example,
to automatically update a program. To do this, you need to include the <strong>mirror.py</strong> module
and create an instance of the <strong>Mirror</strong> class; set its attributes using its <strong>set</strong> method,
and finally call its <strong>main</strong> method. See this example:

```python
from mirror import Mirror

def updateMe():
  m = Mirror()
  m.set('http://myhost.org/repos/myapp/',
        {'username': 'myusername',
	 'password': 'mypass'})
  (updated, failed) = m.main()
  print "{} updated, {} failed".format(updated, failed)
```

The first argument to <strong>set</strong> is the URL of the repository; the second argument is an optional dictionary containing any subset of the following keys:

* filelist
* username (for Basic authentication)
* password (for Basic authentication)
* output (stream for regular output - default is standard output)
* debug (stream for messages - default is standard error)
* dry (if True, don't actually download anything

## Bugs, limitations, wishlist
 
 * Python2 only for now.
 * If a download fails, there's basically no way to know why.
 * Security is based on Basic authentication, which is not terribly strong. Another easy way of providing (very limited) security is to use a non-standard name for the file list. That way, only someone who knows the name you used will be able to mirror the files in the repository.
 * No way to commit changes to the server, and no support for file versions. Use svn or git if you need that!
 
