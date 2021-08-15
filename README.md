# Youtube-Video-Spammer  

You can use this as a crontask or whatever. Just feed it the webhook, a channel or playlist, and watch it go.  
You will need to either put your youtube API key into the python file or change it to use environment variables.  
Blah blah blah—*use at your own risk*.  

**Usage:**  

`python random_youtube.py <username=sent username> <playlist=youtube playlist ID> <channel=youtube channel URL> [webhook=webhook URL]`  
> username, channel, and playlist can be specified multiple times  
> must include either channel or playlist options and must have a webhook  

Example:  
`python random_youtube.py username=Wondercat channel=https://www.youtube.com/user/smbctheater webhook=https://discord.com/api/webhooks/876445614444487777/whatevergoeshereIdontknow`
