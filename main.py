import StringIO
import json
import logging
import random
import urllib
import urllib2

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = '211204587:AAHXcoJk-Cdw28NKWnNDG4Y_LXFewxNt3nA'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                reply('Hey bby')
                reply('I\'m onald Trump.')
                reply('don\'t worry, I\'ll give you the \'D\' later.  ;)')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False)
            elif text == '/image':
                img = Image.new('RGB', (512, 512))
                base = random.randint(0, 16777216)
                pixels = [base+i*j for i in range(512) for j in range(512)]  # generate sample image
                img.putdata(pixels)
                output = StringIO.StringIO()
                img.save(output, 'JPEG')
                reply(img=output.getvalue())
            else:
                reply('What command?')

        # CUSTOMIZE FROM HERE

        elif text.endswith('?'):
            reply('No no no, I\'m the one who asks questions around here.')
        else:
            if getEnabled(chat_id):
                randQuoteInt = random.randint(0, 17)
                trumpQuotes = ["You\'re really attractive. Unlike that Ariana Huffington. Ariana Huffington is unattractive, both inside and out. I fully understand why her former husband left her for a man - he made a good decision.",
                "You know, it really doesn\'t matter what you write as long as you\'ve got a young, and beautiful, piece of ass.",
                "I\'ll name all of my buildings after you if you change your name to \'Trump.\'",
                "Unlike my bid for presidency, my interest in you isn\'t a publicity stunt.",
                "Give me your number or else I\'ll start a nonsensical twitter war with you.",
                "It\'s okay, I don\'t need to see your birth certificate because you\'re white.",
                "Baby it\'s cold outside... So climate change can\'t be real.",
                "How bout we deport those panties?",
                "You really put the \'rump\' in \'Trump\'.  ;)",
                "Roses are red, violets are blue, I had my gardener deported after he picked these flowers for you.",
                "Hey beautiful, I\'d buy you a drink but I don\'t want you becoming dependent on handouts.",
                "I would love to drill you like an Alaskan oil field",
                "Are you a debate moderator? Because you\'re making this hard.",
                "As everybody knows, but the haters and losers refuse to acknowledge, I do not wear a wig. My hair may not be perfect, but it\'s mine.",
                "My whole life is about winning. I don\'t lose often. I almost never lose.",
                "Do you mind if I sit back a little? Because your breath is very bad.",
                "You don\'t seem very smart. That\'s great though! I love the poorly educated.",
                "Do you know why they call me Trump? Because they couldn't take their eyes away from my huge trumpet"]
                reply(trumpQuotes[randQuoteInt])
            else:
                logging.info('not enabled for chat_id {}'.format(chat_id))


# add an ethnicity checker, then insult them with a quote


#        elif 'who are you' in text:
#            reply('telebot starter kit, created by yukuku: https://github.com/yukuku/telebot')
#        elif 'what time' in text:
#            reply('look at the corner of your screen!')
#        else:
#            if getEnabled(chat_id):
#                reply('nope.')
#            else:
#                logging.info('not enabled for chat_id {}'.format(chat_id))


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
