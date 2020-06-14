#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The script was developed by Reto Stauffer and extended by Daniel Naschberger.

The sourcecode of Reto Stauffer can be found at :
https://github.com/retostauffer/GEFS_Downloader_Simple"""

def bar():
    """bar()

    Simply prints a line of "-" on stdout.
    """
    print("{:s}".format("".join(["-"]*70)))

# -------------------------------------------------------------------
# -------------------------------------------------------------------
def get_file_names(filedir, baseurl, date, mem, step, avgspr):
    """get_file_names(filedir, baseurl, date, mem, step)

    Generates the file names (remote and local).

    Parameters
    ----------
    filedir : str
        name of the directory where to create the file "local"
    baseurl : str
        base url, used to format the data (can contain %Y%m%d or similar)
    date : datetime.datetime
        defines model initialization date and time
    mem : int
        member number
    step : int
        forecast step (in hours)

    Returns
    -------
    Returns a dict with three entries for the indexfile ("idx"), the grib file ("grib"),
    and the local file name ("local"), plus the file name of the local subset. Only
    used if subset is defined and wgrib2 is available (see main script).
    """
    import os
    import datetime as dt

    # Create URL  	geavg.t00z.pgrb2af00.idx
    if avgspr in ['avg', 'spr']:
        gribfile = os.path.join(date.strftime(baseurl),
                            "ge{:s}.t{:s}z.pgrb2af{:s}".format(avgspr, date.strftime("%H"),
                            "{:02d}".format(step) if step < 100 else "{:03d}".format(step)))
        local = date.strftime("GFEE_%Y%m%d_%H00") + "_{:s}_f{:03d}.grb2".format(avgspr, step)
        subset = date.strftime("GFSE_%Y%m%d_%H00") + "_{:s}_f{:03d}_subset.grb2".format(avgspr, step)
    else:
        gribfile = os.path.join(date.strftime(baseurl),
                            "ge{:s}{:02d}.t{:s}z.pgrb2f{:s}".format(
                            "c" if mem == 0 else "p", mem, date.strftime("%H"),
                            "{:02d}".format(step) if step < 100 else "{:03d}".format(step)))
        local    = date.strftime("GEFS_%Y%m%d_%H00") + "_{:02d}_f{:03d}.grb2".format(mem, step)
        subset   = date.strftime("GEFS_%Y%m%d_%H00") + "_{:02d}_f{:03d}_subset.grb2".format(mem, step)
    return {"grib"   : gribfile,
            "idx"    : "{:s}.idx".format(gribfile), 
            "local"  : os.path.join(filedir, local),
            "subset" : os.path.join(filedir, subset)}


# -------------------------------------------------------------------
# -------------------------------------------------------------------
class idx_entry(object):
    def __init__(self, args):
        """idx_entry(args)

        A small helper class to handle index entries.
        
        Parameters
        ----------
        args : list
            list with three entries (bytes start, param name, param level)
        """
        self._byte_start = int(args[0])
        self._var        = str(args[1])
        self._lev        = str(args[2])
        self._byte_end   = False

    def add_end_byte(self, x):
        """add_end_byte(x)

        Appends the ending byte.
        """
        self._byte_end = x

    def end_byte(self):
        """end_byte()

        Returns end byte.
        """
        try:
            x = getattr(self, "_byte_end")
        except:
            raise Error("whoops, _byte_end attribute not found.")
        return x 

    def start_byte(self):
        """start_byte()

        Returns start byte.
        """
        try:
            x = getattr(self, "_byte_start")
        except:
            raise Error("whoops, _byte_start attribute not found.")
        return x 

    def key(self):
        """key()

        Returns
        -------
        Returns a character string "<param name>:<param level>".
        """
        try:
            var = getattr(self, "_var")
            lev = getattr(self, "_lev")
        except Exception as e:
            raise Exception(e)

        return "{:s}:{:s}".format(var,lev)

    def range(self):
        """range()

        Returns
        -------
        Returns the byte range for curl.
        """
        try:
            start = getattr(self, "_byte_start")
            end   = getattr(self, "_byte_end")
        except Exception as e:
            raise Exception(e)
        end = "" if end is None else "{:d}".format(end)

        return "{:d}-{:s}".format(start, end)

    def __repr__(self):
        if isinstance(self._byte_end, bool):
            end = "UNKNOWN"
        elif self._byte_end is None:
            end = "end of file"
        else:
            end = "{:d}".format(self._byte_end)
        return "IDX ENTRY: {:10d}-{:>10s}, '{:s}'".format(self._byte_start,
                end, self.key())

# -------------------------------------------------------------------
# -------------------------------------------------------------------
def parse_index_file(idxfile, params):
    """parse_index_file(idxfile, config)
 
    Downloading and parsing the grib index file, extracts the
    bytes of the required fields/variables.

    Parameters
    ----------
    idxfile : str
        url to the index file
    params : dict
        contains the config of the requested parameters

    Returns
    -------
    Things ... (tdb)
    """

    import requests
    try:
        print(idxfile)
        req  = requests.get(idxfile)
        data = req.text.split("\n")
    except Exception as e:
        print("[!] Problems reading index file\n    {:s}\n    ... return None".format(idxfile))
        return None

    # List to store the required index message information
    idx_entries = []

    # Parsing data (extracting message starting byte,
    # variable name, and variable level)
    import re
    comp = re.compile("^\d+:(\d+):d=\d{10}:([^:.*]*):([^:.*]*)")
    byte = 1 # initial byte
    for line in data:
        if len(line) == 0: continue
        mtch = re.findall(comp, line)
        if not mtch:
            raise Exception("whoops, pattern mismatch \"{:s}\"".format(line))
        # Else crate the variable hash
        idx_entries.append(idx_entry(mtch[0]))

    # Now we know where the message start (bytes), but we do not
    # know where they end. Append this information.
    for k in range(0, len(idx_entries)):
        if (k + 1) == len(idx_entries):
            idx_entries[k].add_end_byte(None)
        else:
            idx_entries[k].add_end_byte(idx_entries[k+1].start_byte() - 1)
    #    print(idx_entries[k])

    # Go trough the entries to find the messages we request for.
    res = []
    for x in idx_entries:
        if x.key() in params: res.append(x.range())
        
    # Return ranges to be downloaded
    return res

# -------------------------------------------------------------------
def download_range(grib, local, range):
    print(local)
    import requests
    r = requests.get(grib)

    with open(local, 'wb') as f:
        f.write(r.content)
        f.close()
    return True


# -------------------------------------------------------------------
# Main script
# -------------------------------------------------------------------
if __name__ == "__main__":

    # List of the required parameters. Check the index file
    # to see the available parameters. Always <param>:<level> where
    # <param> and <level> are the strings as in the grib index file.

    # Import some required packages
    import sys, os, re
    import argparse, sys
    import datetime as dt
    import numpy as np
    import distutils.spawn
    import subprocess as sub


    # Change Working dir:
    dir_of_file = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_of_file)
    os.chdir('../../')
    cwd = os.getcwd()
    print('Arbeitsverzeicniss: {}'.format(cwd))

    # Parsing input args
    parser = argparse.ArgumentParser(description="Download some GEFS data")
    parser.add_argument("--date","-d", type = str,
               help = "Model initialization date. Format has to be YYYY-mm-dd!")
    parser.add_argument("--runhour","-r", type = int,
               help = "Model initialization hour, 0/6/12/18, integer.")
    parser.add_argument("--parm", "-p", type=str,
                        help="GFSE parm, tmp_2m/rh_2m, string.")
    parser.add_argument("--avgspr","-as", type = str,
               help = "GFSE Mean or Spread, avg/spr, string.")
    args = vars(parser.parse_args())

    # Checking args
    if args["runhour"] is None or args["date"] is None:
        parser.print_usage(); sys.exit(9)
    if not re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", args["date"]):
        parser.print_usage()
        raise ValueError("wrong format for input -d/--date")
    if not args["runhour"] in [0, 6, 12, 18]:
        parser.print_usage()
        raise ValueError("wrong input for -r/--runhour, has to be 0/6/12/18")
    if not args["parm"] in ['tmp_2m', 'rh_2m', 'ugrd_10m', 'vgrd_10m']:
        parser.print_usage()
        raise ValueError("wrong input for -p/--parm, has to be tmp_2m/rh_2m/ugrd_10m/vgrd_10m")
    if not args["avgspr"] in [None, 'avg', 'spr']:
        parser.print_usage()
        raise ValueError("wrong input for -as/--avgspr, has to be avg/spr")

    if args["parm"] == 'tmp_2m':
        params = ["TMP:2 m above ground"]
    elif args["parm"] == 'rh_2m':
        params = ["RH:2 m above ground"]
    elif args["parm"] == 'ugrd_10m':
        params = ["UGRD:10 m above ground"]
    elif args["parm"] == 'vgrd_10m':
        params = ["VGRD:10 m above ground"]

    # Config
        # Provide folder structure.
    data_path = "/get_available_data/gefs"
    if not os.path.exists(f"{data_path}"):
        os.mkdir(f"{data_path}")

    if not os.path.exists(f"{data_path}/data/"):
        os.mkdir(f"{data_path}/data/")

    outdir = "/get_available_data/gefs/data/gfs_forcast/{}".format(args["parm"])
    baseurl_avgspr = "https://www.ftp.ncep.noaa.gov/data/nccf/com/gens/prod/gefs.%Y%m%d/%H/pgrb2a/"
    baseurl_ens = "http://nomads.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.%Y%m%d/%H/pgrb2/"
    # Subset (requires wgrib2), can also be None.
    # Else a dict with N/S/E/W in degrees (0-360!)
    subset = {"E": 20, "W": 8, "S": 45, "N": 53}


    # Crate date arg
    date = dt.datetime.strptime("{:s} {:02d}:00".format(args["date"], args["runhour"]),
                                  "%Y-%m-%d %H:%M")

    # Steps/members. The +1 is required to get the required sequence!
    steps = np.arange(6, 300+1, 6, dtype = int)

    bar()
    if args["avgspr"] in ['avg', 'spr']:
        members = np.arange(0, 1, 1, dtype = int)
        print("Downloading members:\n  {:s}:  ".format(args["avgspr"]))
        baseurl = baseurl_avgspr
    else:
        members = np.arange(0, 20+1, 1, dtype=int)
        print("Downloading members:\n  {:s}".format(", ".join(["{:d}".format(x) for x in members])))
        baseurl = baseurl_ens


    print("Downloading steps:\n  {:s}".format(", ".join(["{:d}".format(x) for x in steps])))
    print("For date/model initialization\n  {:s}".format(date.strftime("%Y-%m-%d %H:%M UTC")))
    print("Base url:\n  {:s}".format(date.strftime(baseurl)))
    bar()

    # Looping over the different members first
    for mem in members:
        # Looping over forecast lead times
        for step in steps:
            bar()
            if args["avgspr"] in ['avg', 'spr']:
                print("Processing +{:03d}h forecast, {:s}".format(step, args["avgspr"]))
            else:
                print("Processing +{:03d}h forecast, member {:02d}".format(step, mem))

            # Specify and create output directory if necessary
            filedir = "{:s}/{:s}".format(outdir, date.strftime("%Y%m%d%H%M"))
            if not os.path.isdir(filedir):
                try:
                    os.makedirs(filedir)
                except:
                    raise Exception("Cannot create directory {:s}!".format(filedir))

            # Getting file names
            files = get_file_names(filedir, baseurl, date, mem, step, args["avgspr"])
            print(files)
            if os.path.isfile(files["subset"]):
                print("- Local subset exists, skip")
                bar()
                continue
            if os.path.isfile(files["local"]):
                print("- Local file exists, skip")
                bar()
                continue


            # Else start download
            print (f"- Grib file: {files['grib']}\n- Index file: {files['idx']}\n - Local file: {files['local']}\n- Subset file: {files['subset']}")

            # Read/parse index file (if possible)
            required = parse_index_file(files["idx"], params)

            # If no messages found: continue
            if required is None: continue
            if len(required) == 0: continue

            # Downloading the data
            download_range(files["grib"], files["local"], required)

            # If wgrib2 exists: crate subset (small_grib)
            if not subset is None:
                WE  = "{:.2f}:{:.2f}".format(subset["W"], subset["E"])
                SN  = "{:.2f}:{:.2f}".format(subset["S"], subset["N"])
                cmd = ["wgrib2", files["local"], "-small_grib", WE, SN, files["subset"]]
                print("- Subsetting: {:s}".format(" ".join(cmd)))
                p = sub.Popen(cmd, stdout = sub.PIPE, stderr = sub.PIPE) 
                out,err = p.communicate()

                if p.returncode == 0:
                    print("- Subset created, delete global file")
                    os.remove(files["local"])
                else:
                    print("[!] Problem with subset, do not delete global grib2 file.")


            # Else post-processing the data
            bar()