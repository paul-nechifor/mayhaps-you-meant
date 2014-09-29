#!/usr/bin/env python2
# coding: utf-8

from collections import namedtuple
from datetime import datetime
from kant_generator_pro import KantGenerator
from os import path
import praw
import random
import re
import time
import traceback
import urllib2
import yaml

def getRelative(file):
    return path.join(path.dirname(__file__), file)

class Corrector:
    def __init__(self, correctionsFile):
        text = open(correctionsFile).read()
        self.wrongs = yaml.load(text)
        self.right = {}
        for right, wrongs in self.wrongs.items():
            for wrong in wrongs:
                if self.right.has_key(wrong):
                    print 'Duplicate:', wrong, right, self.right[wrong]
                    exit()
                self.right[wrong] = right
        regex = r'(\b' + r'\b|\b'.join(self.right) + r'\b)'
        self.wrongRegex = re.compile(regex)

    def find(self, text):
        ret = []
        for match in self.wrongRegex.findall(text):
            ret.append((match, self.right[match]))
        return ret

class Responder:
    def __init__(self, responsesFile, emotesFile, format, info={}):
        self.kg = KantGenerator(responsesFile)
        text = unicode(open(emotesFile).read(), 'utf-8')
        self.emotes = yaml.load(text)
        self.format = format
        self.info = info

    def getText(self, wrong, right):
        self.kg.refresh()
        response = self.fixSyntax(self.kg.output())
        info = self.info.copy()
        info['wrong'] = wrong
        info['right'] = right
        info['response'] = response.format(**info)
        info['emote'] = self.getEmote(wrong)
        md = self.format.format(**info)
        return md

    def fixSyntax(self, text):
        text = re.sub('\s+', ' ', text)
        text = text.replace(' ,', ',')
        text = text.replace(' .', '.')
        return text

    def getEmote(self, wrong):
        if wrong == 'alot':
            type = 'flutalot'
        else:
            type = random.choice(self.emotes)
        return '[](/{}) '.format(type)

    def getSmallText(self, text):
        # Replace with different space. Python's Unicode support is shit.
        text = text.replace(' ', u' ')
        text = '^^' + text.replace('\n\n', '\n\n^^')
        return text

class Client:
    def __init__(self):
        self.v = self.getValues()
        self.reddit = praw.Reddit(user_agent=self.v.userAgent)
        self.corrector = Corrector(getRelative('data/corrections.yaml'))
        self.responder = Responder(getRelative('data/responses.xml'),
                getRelative('data/emotes.yaml'), self.v.format)
        self.responses = []
        self.nComments = 0
        self.lastReplyTime = time.time()
        self.lastLogTime = time.time()

    def getValues(self):
        text = open(getRelative('config.yaml')).read()
        v = yaml.load(text)
        try:
            text = open(getRelative('config-private.yaml')).read()
            for key, value in yaml.load(text).items():
                v[key] = value
        except IOError:
            print 'No `config-private.yaml` found.'
        V = namedtuple('V', v.keys())
        return V(**v)

    def log(self, text):
        print datetime.now().isoformat(), text

    def login(self):
        self.log('Logging in.')
        self.reddit.login(self.v.username, self.v.password)
        self.log('Logged in.')

    def reset(self):
        self.log('Resetting.')
        self.responses = []

    def run(self):
        self.log('Started running.')
        for comment in praw.helpers.comment_stream(self.reddit,
                self.v.subreddit, verbosity=self.v.verbosity):
            self.processComment(comment)
            if time.time() - self.lastReplyTime > self.v.commentSleepTime:
                self.reply()

    def loop(self):
        while True:
            try:
                self.login()
                self.run()
            except urllib2.HTTPError:
                self.log('Replying forbidden.')
                time.sleep(self.v.resetSleepTime)
            except:
                self.log('Error')
                traceback.print_exc()
                self.reset()
                time.sleep(self.v.resetSleepTime)

    def processComment(self, comment):
        self.updateLog()
        wrongs = self.corrector.find(comment.body)
        if len(wrongs) == 0:
            return
        self.responses.append((comment, wrongs))

    def updateLog(self):
        self.nComments += 1
        numberUpdate = self.nComments % self.v.commentFrequency == 0
        timeUpdate = time.time() - self.lastLogTime > self.v.logUpdateTime
        update = numberUpdate or timeUpdate
        if not update:
            return
        self.lastLogTime = time.time()
        self.log('comments={} resp={} left={:.2f}'.format(
                self.nComments,
                len(self.responses),
                self.v.commentSleepTime - (time.time() - self.lastReplyTime)))

    def getBestResponse(self):
        # For now it just returns the latest response possible.
        return self.responses[-1]

    def getResponseText(self, wrongs):
        # Correct a random wrong.
        wrong, right = random.choice(wrongs)
        self.log('Replying: "{}" -> "{}".'.format(wrong, right))
        return self.responder.getText(wrong, right)

    def reply(self):
        self.log('Will try to reply.')
        self.lastReplyTime = time.time()
        if len(self.responses) == 0:
            self.log('Nothing to respond to.')
            return
        comment, wrongs = self.getBestResponse()
        text = self.getResponseText(wrongs)
        print '-'*20
        print text
        print '-'*20
        text = self.responder.getSmallText(text)
        comment.reply(text)

def main():
    client = Client()
    client.loop()

if __name__ == '__main__':
    main()
