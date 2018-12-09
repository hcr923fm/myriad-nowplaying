import socket
import csv
import os
import os.path
import shlex
import argparse

opt_parser = argparse.ArgumentParser()
opt_parser.add_argument("--tagged_folder", "-f",
                        action="store", nargs="?", type=str,)
args = opt_parser.parse_args()

# TODO: Can we interrogate the RB-OA3 to determine which studio is on air?
MYRIAD_CLIENT_IPS = ["192.168.0.2", "192.168.0.7"]
TCP_PORT = 6950
MYRIAD_SERVER_IP = "192.168.0.4"
MYRIAD_TAGGED_DIR = args.tagged_folder if args.tagged_folder else "\\\\" + MYRIAD_SERVER_IP + \
    "\\PSquared\\AudioWall\\0000s\\Tagged"
COMMAND = "PLAYER TAGPLAYINGAUDIO ALL\n"


def getDataUntilNewLine(s):
    data = ""
    while data.rfind("\n") == -1:
        data += s.recv(1)

    return data


# print "Attempting to tag all playing audio"

for server in MYRIAD_CLIENT_IPS:
    # print "--->", server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server, TCP_PORT))
    success = False
    failcount = 0
    while (not success and failcount < 3):
        s.send(COMMAND)
        data = getDataUntilNewLine(s)

        if data.find("Success") != -1:
            success = True
            # print "--->    Success"
            s.close()
        elif data.find("Connected") != -1:
            # print "--->    Connected"
            pass
        else:
            # print "--->    Failed, retrying"
            failcount += 1

    if not success:
        print "Failed to get Now Playing data, exiting..."
        exit(1)

files = os.listdir(MYRIAD_TAGGED_DIR)
files = sorted(files)

latest_file_name = files.pop()
latest_file_path = os.path.join(MYRIAD_TAGGED_DIR, latest_file_name)
now_playing_is_song = False
now_playing_title = ""
now_playing_artist = ""

with open(latest_file_path, "r") as tagged_csv:
    csv_reader = csv.DictReader(tagged_csv, fieldnames=["StartDateTime", "HDReference", "Player", "SecondsPlayed",
                                                        "LogReference", "OnAirReference", "ScheduleReference", "Location", "CurrentUser", "HDSerialisation"])

    for row in csv_reader:
        item_data_string = row["HDSerialisation"]
        if (not item_data_string) or (row["HDSerialisation"] == "HDSerialisation"):
            continue
        item_data_split = shlex.split(item_data_string)
        item_data = {}
        for item_data_unit in item_data_split:
            item_data_parts = item_data_unit.split("=")
            item_data[item_data_parts[0]] = item_data_parts[1]

            # TODO: Look at SecondsPlayed - if it's more than (say) 6 minutes out, it's probably stuck.
            # So, then exit(3)

        if item_data["ContTypInf"] == "Music":
            now_playing_is_song = True
            now_playing_artist = item_data["AName1"]
            now_playing_title = item_data["ITitle"]

if now_playing_is_song:
    print now_playing_artist, "-", now_playing_title
else:
    exit(2)

os.remove(latest_file_path)
