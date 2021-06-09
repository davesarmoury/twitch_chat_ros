#!/usr/bin/env python
# coding: utf-8
encoding='ASCII'
import rospy
from std_msgs.msg import String
import sys
import irc.bot
import requests
from twitch_chat_ros.msg import twitch_message

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel, pub):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.pub = pub

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        rospy.loginfo('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+ token)], username, username)

    def on_welcome(self, c, e):
        rospy.loginfo('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def getTagsDict(self, e):
        tags = {}
        for i in e.tags:
            if i["value"] != None:
                tags[i["key"].replace("-","_")] = i["value"].encode(encoding="UTF-8", errors='replace')
        return tags

    def populate_msg(self, e, tags):
        msg = twitch_message()

        msg.type = e.type.encode(encoding="UTF-8", errors='replace')
        msg.source = e.source.encode(encoding="UTF-8", errors='replace')
        msg.target = e.target.encode(encoding="UTF-8", errors='replace')
        for a in e.arguments:
            msg.arguments.append(a)
        if "badge_info" in tags.keys(): msg.tags.badge_info = tags["badge_info"]
        if "badges" in tags.keys(): msg.tags.badges = tags["badges"]
        if "bits" in tags.keys(): msg.tags.bits = tags["bits"]
        if "client_nonce" in tags.keys(): msg.tags.client_nonce = tags["client_nonce"]
        if "color" in tags.keys(): msg.tags.color = tags["color"]
        if "display_name" in tags.keys(): msg.tags.display_name = tags["display_name"]
        if "emotes" in tags.keys(): msg.tags.emotes = tags["emotes"]
        if "flags" in tags.keys(): msg.tags.flags = tags["flags"]
        if "id" in tags.keys(): msg.tags.id = tags["id"]
        if "mod" in tags.keys(): msg.tags.mod = tags["mod"]
        if "room_id" in tags.keys(): msg.tags.room_id = tags["room_id"]
        if "subscriber" in tags.keys(): msg.tags.subscriber = tags["subscriber"]
        if "tmi_sent_ts" in tags.keys(): msg.tags.tmi_sent_ts = tags["tmi_sent_ts"]
        if "turbo" in tags.keys(): msg.tags.turbo = tags["turbo"]
        if "user_id" in tags.keys(): msg.tags.user_id = tags["user_id"]
        if "user_type" in tags.keys(): msg.tags.user_type = tags["user_type"]

        return msg

    def on_pubmsg(self, c, e):
        tags = self.getTagsDict(e)
        self.pub.publish(self.populate_msg(e, tags))
        return

    def callback(self, data):
        pass

def main():
    rospy.init_node('twitch_bot', anonymous=True)

    username = rospy.get_param('~username')
    client_id = rospy.get_param('~client_id')
    token = rospy.get_param('~token')
    channel = rospy.get_param('~channel')

    pub = rospy.Publisher('received_message', twitch_message, queue_size=10)
    bot = TwitchBot(username, client_id, token, channel, pub)
    sub = rospy.Subscriber('send_msg', String, bot.callback)
    bot.start()

if __name__ == "__main__":
    main()
