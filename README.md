# sciencetoots

This script listens to public tweets mentioning "Send to @ScienceToots",
it checks if the tweets are replies to another tweet or thread and send the
replied tweets/threads to Mastodon via [@sciencetoots@mstdn.science](https://mstdn.science/@sciencetoots). An archive
of the tweet IDs already sent prevents the bot from sending multiple times the same
tweet/thread. Images are also included in the messages sent to Mastodon.

The script needs [tweepy](https://www.tweepy.org/) and [toot](https://toot.readthedocs.io/).
