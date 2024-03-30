To make things work you have to go through some oAuth stuff, and get credentials.

# Handle Errors
- Quota errors: can't do nothing try next day when quota is reset
- credential issue: Need to populate client_secret.json in specific format, otherwise it will throw error
- also when authorization is done, it will create a file called `script_name-oAuth.json`, which will be used for future authorization, if you want to change the account, you need to delete this file and re-run the script, and then reauthorize the account you want to use.
- don't forget to change the client_secret.json file for different account, otherwise it will use the same account as before and give quota errors
- [blog](https://sunil-dhaka.github.io/automation/automate-video-uploads.html)

# Warnings
- To make this stuff work is not easy because of certain factors. Main one is google keeps changing things and google is very strict about multiple oAuth. Even after so much work, I could not make it fully automated. I have to go to browser to click on one button. One benefit these scripts have is that you can batch process your folders, so that manual oAuth is one time deal.
- And then also yt-v3 api has quota restrictions, as mentioned in errors.
- So if you are stuck, then you are on your own. 
