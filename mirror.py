#!/usr/bin/env python

import sys
import urllib
import os
import os.path
import stat

CONFFILE = ".mirror"
FILELISTHDR = "# FILELIST"

def plural(l):
    return "" if len(l) == 1 else "s"

class Mirror():
    conffile = CONFFILE
    srcpath = None
    dstpath = "."
    filelist = ".FILELIST"
    created = []
    modified = []
    filenames = []
    debug = sys.stderr
    mode = "get"
    dry = False
    
    def __init__(self):
        self.modified = []
        self.fileames = []

    def usage(self):
        sys.stdout.write("""mirror.py - simple file mirroring

Usage: mirror.py [options] 
       mirror.py -i [options] files...

Options:

  -s S | Set source URL to S (e.g. http://my.server.com/repo/). Required.
  -f F | Set name of file list file (default: {}).
  -c C | Set name of configuration file (default: {} in source directory).
  -x   | Dry run: print operations to be performed, don't actually do them.
  -i   | Initialize mode: write files listed on command-line to file list
         (run this in the repo directory).

(c) 2018, A. Riva
""".format(self.filelist, self.conffile))

    def msg(self, string, *args):
        sys.stderr.write("# " + string.format(*args))
        
    def parseArgs(self, args):
        if "-h" in args or "--help" in args:
            self.usage()
            return False
        self.maybeLoadConf(args)
        prev = ""
        for a in args:
            if prev == "-s":
                self.srcpath = a
                prev = ""
            elif prev == "-d":
                self.dstpath = a
                prev = ""
            elif prev == "-f":
                self.filelist = a
                prev = ""
            elif a in ["-s", "-d", "-f"]:
                prev = a
            elif a == "-i":
                self.mode = "list"
            elif a == "-x":
                self.dry = True
            else:
                self.filenames.append(a)
        return True

    def maybeLoadConf(self, args):
        prev = ""
        for a in args:
            if prev == "-c":
                self.conffile = a
                prev = ""
            elif a == "-c":
                prev = a
        if os.path.isfile(self.conffile):
            self.msg("Reading configuration defaults from {}\n", self.conffile)
            with open(self.conffile, "r") as f:
                for line in f:
                    fields = [ s.strip() for s in line.split("=") ]
                    if len(fields) == 2:
                        key = fields[0]
                        if key == "url":
                            self.srcpath = fields[1]
                        elif key == "filelist":
                            self.filelist = fields[1]

    def writeFilelist(self):
        nin = len(self.filenames)
        nout = 0
        with open(self.filelist, "w") as out:
            out.write(FILELISTHDR + "\n")
            for fn in self.filenames:
                if os.path.isfile(fn) or os.path.isdir(fn):
                    fs = os.stat(fn)
                    mode = fs.st_mode
                    if stat.S_ISREG(mode):
                        ftype = "F"
                    elif stat.S_ISDIR(mode):
                        ftype = "D"
                    else:
                        continue
                    out.write("{}\t{}\t{}\t{}\t{}\n".format(fn, ftype, mode, fs.st_size, fs.st_mtime))
                    nout += 1
        self.msg("{}/{} files added to file list.\n", nout, nin)
        
    def getFilelist(self):
        if os.path.isfile:
            try:
                os.remove(self.filelist)
            except:
                pass
        url = self.srcpath + "/" + self.filelist
        self.msg("Retrieving file list from `{}'.\n", url)
        try:
            (filename, headers) = urllib.urlretrieve(url, self.filelist)
            with open(filename, "r") as f:
                hdr = f.readline().strip()
                if hdr != FILELISTHDR:
                    self.msg("File list `{}' is not in correct format.\n", filename)
                    return False
            self.msg("File list `{}' retrieved.\n", self.filelist)
            return filename
        except:
            self.msg("Error downloading file list from URL `{}'.\n", url)
            return False

    def findChanged(self):
        with open(self.filelist, "r") as f:
            f.readline()
            for line in f:
                fields = line.rstrip("\r\n").split("\t")
                path = fields[0]
                ftype = fields[1]
                size = int(fields[3])
                mtime = float(fields[4])
                if ftype == "D":
                    if not os.path.isdir(path):
                        self.created.append(fields)
                elif ftype == "F":
                    if os.path.isfile(path):
                        fs = os.stat(path)
                        if mtime > fs.st_mtime:
                            self.modified.append(fields)
                    else:
                        self.created.append(fields)
        w = True
        if self.created:
            self.msg("{} new file{}.\n", len(self.created), plural(self.created))
            w = False
        if self.modified:
            self.msg("{} file{} modified.\n", len(self.modified), plural(self.modified))
            w = False
        if w:
            self.msg("All files up to date.\n")

    def updateAll(self):
        if self.created:
            self.msg("Downloading {} new file{}...\n", len(self.created), plural(self.created))
            for cr in self.created:
                self.updateOne("N", cr)
        if self.modified:
            self.msg("Downloading {} modified file{}...\n", len(self.modified), plural(self.modified))
            for cr in self.modified:
                self.updateOne("U", cr)

    def updateOne(self, code, cr):
        path = cr[0]
        ftype = cr[1]
        mode = int(cr[2])
        size = int(cr[3])
        sys.stdout.write(code + ftype + "\t" + path + "\t")
        if self.dry:
            sys.stdout.write("???\n")
            return
        if ftype == "D":
            #try:
            os.makedirs(path)
            os.chmod(path, mode)
            sys.stdout.write("ok.\n")
            #except:
            sys.stdout.write("failed.\n")
        elif ftype == "F":
            try:
                os.remove(path + ".bak")
                os.rename(path, path + ".bak")
            except:
                pass        # This may fail on Windows
            urllib.urlretrieve(self.srcpath + "/" + path, path)
            if os.path.isfile(path) and os.stat(path).st_size == size:
                os.chmod(path, mode)
                sys.stdout.write("ok.\n")
            else:
                sys.stdout.write("failed.\n")
                try:
                    os.rename(path + ".bak", path)
                except:
                    pass
                
    def main(self):
        if M.getFilelist():
            M.findChanged()
            if M.modified or M.created:
                M.updateAll()
                
if __name__ == "__main__":
    M = Mirror()
    if M.parseArgs(sys.argv[1:]):
        if M.mode == "list":
            M.writeFilelist()
        else:
            M.main()
