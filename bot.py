#!/usr/bin/env python2
# coding: utf-8

from kant_generator_pro import KantGenerator
from os import path
import praw
import random
import re
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
        regex = r'(\b' + '|'.join(self.right) + r'\b)'
        self.wrongRegex = re.compile(regex)

    def findSet(self, text):
        ret = []
        for match in self.wrongRegex.findall(text):
            print match
            ret.append((match, self.right[match]))
        return ret

class Responder:
    def __init__(self, responsesFile, emotesFile, format, info={}):
        self.kg = KantGenerator(responsesFile)
        text = open(emotesFile).read()
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
        if wrong is 'alot':
            type = 'flutalot'
        else:
            type = random.choice(self.emotes)
        return '[](/{}) '.format(type)


class Client:
    def __init__(self):
        self.v = self.getValues()
        self.reddit = praw.Reddit(user_agent=self.v['userAgent'])
        self.corrector = Corrector(getRelative('data/corrections.yaml'))
        responses = getRelative('data/responses.xml')
        emotes = getRelative('data/emotes.yaml')
        self.responder = Responder(responses, emotes, self.v['format'])

    def getValues(self):
        text = open(getRelative('config.yaml')).read()
        v = yaml.load(text)
        try:
            text = open(getRelative('config-private.yaml')).read()
            for key, value in yaml.load(text).items():
                v[key] = value
        except IOError:
            print 'No `config-private.yaml` found.'
        return v

    def login(self):
        self.reddit.login(self.v['username'], self.v['password'])

def main():
    client = Client()

if __name__ == '__main__':
    main()
