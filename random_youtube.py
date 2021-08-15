import requests
import sys
import re
import random

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


def send_webhook(text, webhook_url, username):
    assert text, f"text is {text}"
    assert webhook_url, f"webhook_url is {webhook_url}"
    requests.post(webhook_url, data={"content": text, "username": username})


def get_channel_playlistID(channel):
    assert channel, f"channel is {channel}"
    url = f"{channel}/videos"
    results = requests.get(url)
    rex = re.search(
        r"\"watchPlaylistEndpoint\":{\"playlistId\":\"([^\"]+)\"", results.text
    )
    return rex.group(1)


def main():
    random.seed()
    channels = []
    playlistIDs = []
    webhook = ""
    usernames = []
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
        assert channels or playlistIDs
        assert len(webhook) > 0
    except:  # noqa: E722
        return print(
            """Usage:\n python random_youtube.py <username=sent username> <playlist=youtube playlist ID> <channel= youtube channel URL> [webhook=webhook URL]\n username, channel, and playlist can be specified multiple times\n must include either channel or playlist options"""
        )
    video_ids = []
    for channel in channels:
        try:
            playlistIDs.append(get_channel_playlistID(channel))
        except:  # noqa: E722
            return print(
                f"Your channel URL is broken.\nThis one: {channel}\nShould be of the form: https://www.youtube.com/user/smbctheater or https://www.youtube.com/channel/UC13angEs6J09darNmisoRng"
            )
    for playlistID in playlistIDs:
        video_ids += get_videos(playlistID)
    if video_ids:
        video_id = video_ids[random.randint(0, len(video_ids) - 1)]
    if video_id:
        username = None
        if usernames:
            username = usernames[random.randint(0, len(usernames) - 1)]
        send_webhook(f"https://youtu.be/{video_id}", webhook, username)


main()
