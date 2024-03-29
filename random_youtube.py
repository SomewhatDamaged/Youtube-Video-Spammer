import requests
import sys
import re
import random
import json
import os

api_key = "<put your API key here>"  # Youtube API key.


def get_videos(playlistID):
    assert playlistID, f"playlistID is {playlistID}"
    url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={playlistID}&key={api_key}"
    headers = {
        "Accept": "application/json",
    }
    pageToken = ""
    output_ids = []
    while True:
        if pageToken:
            results = requests.get(url + f"&pageToken={pageToken}", headers=headers)
        else:
            results = requests.get(url, headers=headers)
        results = results.json()
        if results:
            for vidData in results["items"]:
                try:
                    # insert blacklisting data here
                    output_ids.append(vidData["snippet"]["resourceId"]["videoId"])
                except:  # noqa: E722
                    continue
            if "nextPageToken" in results:
                pageToken = results["nextPageToken"]
            else:
                break
        else:
            break
    return output_ids


def resolve_channelID(username):
    assert username, f"username is {username}"
    url = f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&q={username}&type=channel&key={api_key}"
    headers = {
        "Accept": "application/json",
    }
    results = requests.get(url, headers=headers)
    results = results.json()
    if results:
        for channelData in results["items"]:
            try:
                return channelData["id"]["channelId"]
            except:  # noqa: E722
                continue
    return None


def process_playlistID(channel):
    assert channel, f"channel is {channel}"
    channelID = re.fullmatch(r"https:\/\/(?:www\.)?youtube\.com\/(?:(user|c)|channel)\/(?(1)(?P<user>.+)|(?P<channel>.+))", channel)
    assert channelID is not None, f"{channel} did not match any existing Youtube channel URLs /o\\"
    if not channelID.group("channel"):
        channelID = resolve_channelID(channelID.group("user"))
    assert channelID is not None, f"{channel} did not match any existing Youtube channel URLs /o\\"
    return get_channel_playlistID(channelID)


def send_webhook(text, webhook_url, username):
    assert text, f"text is {text}"
    assert webhook_url, f"webhook_url is {webhook_url}"
    requests.post(webhook_url, data={"content": text, "username": username})


def get_channel_playlistID(channelID):
    print(f"channelID = {channelID}")
    assert channelID, f"channel is {channelID}"
    url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&id={channelID}&key={api_key}"
    headers = {
        "Accept": "application/json",
    }
    pageToken = ""
    while True:
        if pageToken:
            results = requests.get(url + f"&pageToken={pageToken}", headers=headers)
        else:
            results = requests.get(url, headers=headers)
        results = results.json()
        if results:
            for playlistData in results["items"]:
                try:
                    return playlistData["contentDetails"]["relatedPlaylists"]["uploads"]
                except:  # noqa: E722
                    continue
            if "nextPageToken" in results:
                pageToken = results["nextPageToken"]
            else:
                break
        else:
            break
    return None


def read_history(path):
    if not os.path.exists(path):
        write_history(path, [])
        return []
    else:
        with open(path) as infile:
            return json.load(infile)


def write_history(path, data):
    with open(path, "w") as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=False)


def add_tickets(ticket_name, number_of_tickets, lottery):
    number_of_tickets = max(number_of_tickets, 1)
    lottery.extend([ticket_name for _ in range(number_of_tickets)])
    return lottery


def process_ticket(ticket_name, lottery):
    if "|" in ticket_name:
        add_tickets(ticket_name.rsplit("|", 1)[0], int(ticket_name.rsplit("|", 1)[1]), lottery)
    else:
        lottery.append(ticket_name)


def build_lottery(lottery_in):
    lottery_out = []
    for ticket_name in lottery_in:
        process_ticket(ticket_name, lottery_out)
    return lottery_out


def main():
    random.seed()
    channels = []
    playlistIDs = []
    webhook = ""
    usernames = []
    history = ""
    history_data = None
    video_id = None
    try:
        for arg in sys.argv:
            if arg.endswith(".py"):
                continue
            if arg.startswith("username="):
                usernames.append(arg.split("=", 1)[1])
                continue
            if arg.startswith("webhook="):
                webhook = arg.split("=", 1)[1]
                continue
            if arg.startswith("playlist="):
                playlistIDs.append(arg.split("=", 1)[1])
                continue
            if arg.startswith("channel="):
                channels.append(arg.split("=", 1)[1])
                continue
            if arg.startswith("history="):
                history = arg.split("=", 1)[1]
                continue
        assert channels or playlistIDs
        assert len(webhook) > 0
    except:  # noqa: E722
        return print(
            """Usage:
 python random_youtube.py <username=sent username> <playlist=youtube playlist ID> <channel=youtube channel URL> <history=path to a JSON file> [webhook=webhook URL]
 username, channel, and playlist can be specified multiple times
 must include either channel or playlist options and must have a webhook.
 if history is set, the specified file will be used to avoid posting dupes until all videos in the playlist are shown."""
        )
    video_ids = []
    if history:
        history_data = read_history(history)
        print(f"History: {history_data}")
    for channel in channels:
        playlistID = process_playlistID(channel)
        try:
            if playlistID is not None:
                playlistIDs.append(playlistID)
            else:
                print(f"Warning: Channel {channel} has no videos! O.O")
        except:  # noqa: E722
            return print(
                f"Your channel URL is broken.\nThis one: {channel}\nShould be of the form: https://www.youtube.com/user/smbctheater or https://www.youtube.com/channel/UC13angEs6J09darNmisoRng"
            )
    for playlistID in playlistIDs:
        video_ids += get_videos(playlistID)
    if history_data is not None:
        limited_video_ids = [vid for vid in video_ids if vid not in history_data]
        print(f"Remaining videos: {limited_video_ids}")
        if not limited_video_ids:
            write_history(history, [])
            history_data = []
        else:
            video_ids = limited_video_ids
    if video_ids:
        video_ids = [name for name in video_ids]
        video_id = random.choice(video_ids)
    if video_id is not None:
        if history_data is not None:
            history_data.append(video_id)
            write_history(history, history_data)
        username = None
        if usernames:
            username = random.choice(build_lottery(usernames))
        send_webhook(f"https://youtu.be/{video_id}", webhook, username)


main()
