from datetime import datetime, timedelta
import json


class Tweet:
    def __init__(self, tweet_record):
        self.tweet_id = tweet_record[2]
        self.text = tweet_record[3]
        self.author_id = tweet_record[4]
        self.conversation_id = tweet_record[5]
        self.strava_url = tweet_record[6]
        self.media_count = tweet_record[7]
        self.public_metrics = dict(json.loads(tweet_record[9].replace("'", "\"")))
        self.entities = dict(json.loads(tweet_record[10].replace("'", "\"")))
        # self.reply = tweet_record[12]

    def __repr__(self):
        return 'Tweet {}'.format(self.created_at)

    def has_replies(self):
        if self.public_metrics['reply_count'] > 0:
            return 1
        return 0

    def get_text(self):
        return self.text

    def get_strava_url(self):
        return self.strava_url

    def get_created_at(self):
        return datetime.fromisoformat(self.created_at[:-1])

    def get_created_at_str(self):
        return self.created_at

    def is_within_timeframe(self, tweet, days=30):
        return timedelta(days) > (tweet.get_created_at() - self.get_created_at()) >= timedelta(0)

    def get_author_id(self):
        return self.author_id

    def get_media_count(self):
        return self.media_count

    def get_id(self):
        return int(self.tweet_id)

    def get_entities(self):
        return self.entities

    def get_reply_count(self):
        return self.public_metrics['reply_count']

    def get_like_count(self):
        return self.public_metrics['like_count']

    def get_public_metrics(self):
        return self.public_metrics

    def get_convo_id(self):
        return self.conversation_id

    def get_expanded_url_strava(self):
        try:
            ent = dict(json.loads(self.entities.replace("'", "\"")))
            urls_present = ent.get('urls', False)
            if not urls_present:
                return 'No Urls'
            url = str(urls_present[0].get('expanded_url', 'no expanded url'))
            if '?' in url:
                url = url.split('?')[0]
            if 'activities' in url and len(url.split('/')) > 4:
                url_t = ''
                for i in range(5):
                    url_t += url.split('/')[i] + '/'
                if len(url_t) > 42:
                    url_t = url_t[0:44]
                return url_t[:-1]
            return url
        except json.decoder.JSONDecodeError:
            return 'No url'
        except AttributeError:
            return 'No url'

    def get_expanded_url(self):
        try:
            ent = dict(json.loads(self.entities.replace("'", "\"")))
            urls_present = ent.get('urls', False)
            if not urls_present:
                return 'No Urls'
            url = str(urls_present[0].get('expanded_url', 'no expanded url'))
            if '?' in url:
                url = url.split('?')[0]
            return url
        except json.decoder.JSONDecodeError:
            return 'No url'
        except AttributeError:
            return 'No url'

    def is_behance(self):
        if 'behance' in self.get_expanded_url():
            return True
        return False

    def is_strava(self):
        if 'strava' in self.get_expanded_url_strava():
            return True
        return False

    def is_dribble(self):
        if 'dribbble.com/shots' in self.get_expanded_url():
            return True
        return False

    def is_myrun(self):
        if 'mapmyrun.com/workout/' in self.get_expanded_url():
            return True
        return False

    def is_activity(self):
        try:
            if len(self.get_expanded_url().split('/')) > 3 and self.get_expanded_url().split('/')[3] == 'activities':
                print('found')
                return True
        except AttributeError:
            return False
        return False
