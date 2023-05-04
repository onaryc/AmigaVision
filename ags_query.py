#!/usr/bin/env python3

# AGSImager: Query entries and paths

import sys

import ags_paths as paths
import ags_util as util

# -----------------------------------------------------------------------------

def get_entry(db, name):
    def sanitize(entry):
        if entry is None:
            return None
        entry = dict(entry)
        if entry_is_notwhdl(entry):
            return entry
        if entry_is_valid(entry) and entry["slave_path"].find("/") > 0:
            entry["slave_dir"] = entry["slave_path"].split("/")[0]
            entry["slave_name"] = entry["slave_path"].split("/")[1]
            entry["slave_id"] = entry["slave_name"][:-6]
            return entry
        return None

    n = name.lower()
    patterns = [
        "{}".format(n),
        "game--{}".format(n),
        "game--{}--{}".format(n, n),
        "game--{}files--{}files".format(n, n),
        "game--{}ntsc--{}ntsc".format(n, n),
        "game--{}2mb--{}2mb".format(n, n),
        "game--{}1mb--{}1mb".format(n, n),
        "game--{}512kb--{}512kb".format(n, n),
        "game--{}aga--{}aga".format(n, n),
        "game--{}image--{}image".format(n, n),
        "game--{}4disk--{}4disk".format(n, n),
        "game--{}3disk--{}3disk".format(n, n),
        "game--{}2disk--{}2disk".format(n, n),
        "demo--{}".format(n),
        "demo--{}--{}".format(n, n),
        "game-notwhdl--{}%".format(n),
        "demo-notwhdl--{}%".format(n),
        "mags-notwhdl--{}%".format(n),
        "game--{}%".format(n),
        "demo--{}%".format(n),
        "%--{}%".format(n),
        "%{}%".format(n)
    ]
    for p in patterns:
        e = db.cursor().execute('SELECT * FROM titles WHERE id LIKE ?', (p.lower(),)).fetchone()
        entry = sanitize(e)
        if entry:
            (preferred_entry, _) = get_entry(db, entry["preferred_version"]) if entry.get("preferred_version", None) else (None, None)
            return entry, preferred_entry
    return None, None

def entry_is_valid(entry):
    if not (isinstance(entry, dict)): return False
    if not ("id" in entry and entry["id"]): return False
    if not ("title" in entry and entry["title"]): return False
    if not ("archive_path" in entry and entry["archive_path"]): return False
    if "slave_path" in entry and entry["slave_path"]:
        return True
    elif "game-notwhdl--" in entry["id"] or "demo-notwhdl--" in entry["id"] or "mags-notwhdl--" in entry["id"]:
        return True
    return False

def entry_is_aga(entry):
    if entry_is_valid(entry) and entry.get("aga", 0) > 0:
        return True
    return False

def entry_is_notwhdl(entry):
    if entry_is_valid(entry) and "game-notwhdl--" in entry["id"]:
        return True
    if entry_is_valid(entry) and "demo-notwhdl--" in entry["id"]:
        return True
    if entry_is_valid(entry) and "mags-notwhdl--" in entry["id"]:
        return True
    return False

def name_is_fuzzy(name):
    return not "--" in name

def has_english_language(entry):
    return "english" in entry.get("language", "").lower()

def get_languagues(entry):
    return list(filter(None, entry.get("language", "").split(", ")))

def get_countries(entry):
    return list(filter(None, entry.get("country", "").split(", ")))

def get_publishers(entry):
    return list(filter(None, entry.get("publisher", "").split(", ")))

def get_hardware_short(entry):
    hardware = entry.get("hardware", "")
    if hardware:
        return hardware.replace("/ECS", "").replace("AGA/CD32", "CD32").replace("OCS/CDTV", "CDTV").replace("/", "-")
    else:
        return ""

def get_whd_slavename(entry):
    if entry_is_valid(entry):
        name = entry["slave_name"]
        return name
    else:
        return None

def get_archive_path(entry):
    if entry_is_valid(entry):
        arc_path = util.path(paths.titles(), entry["archive_path"])
        return arc_path if util.is_file(arc_path) else None
    else:
        return None

def get_short_slavename(name):
    excess = len(name) - 30
    if excess > 0:
        parts = name.split(".")
        if len(parts) == 2 and parts[1].lower() == "slave":
            parts[0] = parts[0][:-excess]
            return ".".join(parts)
    return name

def get_whd_dir(clone_path, entry):
    if entry_is_notwhdl(entry):
        return util.path(clone_path, "DH1", "WHD", "N")
    else:
        p = "0-9" if entry["slave_dir"][0].isnumeric() else entry["slave_dir"][0].upper()
        if entry["id"].startswith("demo--"):
            return util.path(clone_path, "DH1", "WHD", "D", p)
        if entry["id"].startswith("mags--"):
            return util.path(clone_path, "DH1", "WHD", "M", p)
        else:
            return util.path(clone_path, "DH1", "WHD", "G", p)

def get_amiga_whd_dir(entry):
    if not entry_is_valid(entry):
        return None
    elif entry_is_notwhdl(entry):
        return None
    else:
        p = "0-9" if entry["slave_dir"][0].isnumeric() else entry["slave_dir"][0].upper()
        if entry["id"].startswith("demo--"):
            return "WHD:D/" + p + "/" + entry["slave_dir"]
        elif entry["id"].startswith("mags--"):
            return "WHD:M/" + p + "/" + entry["slave_dir"]
        else:
            return "WHD:G/" + p + "/" + entry["slave_dir"]

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print("not runnable")
    sys.exit(1)
