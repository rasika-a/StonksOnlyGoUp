import praw
from nltk.corpus import words as nltkwords
import alpaca_trade_api as tradeapi
import config

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


class tickerSuggestion:

    def __init__(self, PRAW_CLIENT_ID, PRAW_CLIENT_SECRET, PRAW_USER_AGENT, ALPACA_KEY_ID, ALPACA_SECRET):
        self.api = tradeapi.REST(config.ALPACA_KEY_ID, config.ALPACA_SECRET, api_version='v2')
        
        self.reddit = praw.Reddit(client_id=config.PRAW_CLIENT_ID, client_secret=config.PRAW_CLIENT_SECRET,
        user_agent= config.PRAW_USER_AGENT)
        
        self._authenticator = IAMAuthenticator(config.IBM_API_KEY)
        self.natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2019-07-12',
        authenticator=self._authenticator)
        self.natural_language_understanding.set_service_url(config.IBM_SERVICE_URL)


    def _getScore(self, sub):
        return sub.score

    def getDDPostTitlesContentUrl(self):
        ddSubs = []
        for submission in self.reddit.subreddit('wallstreetbets').hot():
            if submission.link_flair_text == 'DD':
                ddSubs.append(submission)
        
        for submission in self.reddit.subreddit('wallstreetbets').new():
            if submission.link_flair_text == 'DD':
                ddSubs.append(submission)

        ddSubs.sort(key = self._getScore, reverse=True)
        ddSubsTitlesContentUrl = [(sub.title, sub.selftext, sub.shortlink) for sub in ddSubs]

        return ddSubsTitlesContentUrl

    def getTickers(self, ddSubsTitlesContentUrl):
        allResults = set()
        ibmSentiment = {}
        blacklist_words = [
          "YOLO", "TOS", "CEO", "CFO", "CTO", "DD", "BTFD", "WSB", "OK", "RH",
          "KYS", "FD", "TYS", "US", "USA", "IT", "ATH", "RIP", "BMW", "GDP",
          "OTM", "ATM", "ITM", "IMO", "LOL", "DOJ", "BE", "PR", "PC", "ICE",
          "TYS", "ISIS", "PRAY", "PT", "FBI", "SEC", "GOD", "NOT", "POS", "COD",
          "AYYMD", "FOMO", "TL;DR", "EDIT", "STILL", "LGMA", "WTF", "RAW", "PM",
          "LMAO", "LMFAO", "ROFL", "EZ", "RED", "BEZOS", "TICK", "IS", "DOW"
          "AM", "PM", "LPT", "GOAT", "FL", "CA", "IL", "PDFUA", "MACD", "HQ",
          "OP", "DJIA", "PS", "AH", "TL", "DR", "JAN", "FEB", "JUL", "AUG",
          "SEP", "SEPT", "OCT", "NOV", "DEC", "FDA", "IV", "ER", "IPO", "RISE"
          "IPA", "URL", "MILF", "BUT", "SSN", "FIFA", "USD", "CPU", "AT",
          "GG", "ELON", "TO", "SEE", "THE", "ON", "YOU", "IS", "BUY", "LONG", "SHORT", "POOR", "RICH",
          "DEAL", "ALL", "BAD", "PUTS", "VS", "V", "A", "FOR"
       ] + nltkwords.words()

        for titles,content,url in ddSubsTitlesContentUrl:
            word_list = [w for w in titles.split() if len(w) < 5 and w.upper() not in blacklist_words and w.isalpha()]
            
            for ticker in word_list:
                try:
                    ret = self.api.get_asset(ticker)
                except:
                    continue
                vaderSentiment = self.getSentimentVaderForTicker(content)
                ibmSentiment = self.getSentimentIbmForTicker(content)
                tickerSentimentResultTup = (ticker,url, vaderSentiment["compound"], vaderSentiment["pos"], vaderSentiment["neg"], vaderSentiment["neu"], ibmSentiment['compound'], ibmSentiment['puts'], ibmSentiment['calls'], ibmSentiment['others'])
                allResults.add(tickerSentimentResultTup)  

        return allResults

    def getSentimentVaderForTicker(self, postText):
        analyzer = SentimentIntensityAnalyzer()
        vs = analyzer.polarity_scores(postText)
        #print(text, vs["compound"])
        return vs

    def getSentimentIbmForTicker(self,postText):
        #setup
        result = {'puts' : 0.0, 'calls': 0.0, 'others': 0.0}
        response = self.natural_language_understanding.analyze(
                    text = postText,
                    features=Features(sentiment=SentimentOptions(targets=['puts', 'calls', '']))).get_result()

        for targetWord in response["sentiment"]["targets"]:
            if targetWord["text"] == '':
                result['others'] = targetWord["score"]
            else:
                result[targetWord["text"]] = targetWord["score"]
        
        result["compound"] = response["sentiment"]["document"]["score"]

        return result
        

    def printContents(self, collection):
        #print("-------------------")
        for elem in collection:
            print(elem)
        #print("-------------------")

if __name__ == "__main__":
    stockSuggestions = tickerSuggestion(config.PRAW_CLIENT_ID, config.PRAW_CLIENT_SECRET, config.PRAW_USER_AGENT, config.ALPACA_KEY_ID, config.ALPACA_SECRET)
    ddSubsTitlesContentUrl = stockSuggestions.getDDPostTitlesContentUrl()
    #stockSuggestions.printContents(ddSubsTitlesContentUrl)
    allTickers = stockSuggestions.getTickers(ddSubsTitlesContentUrl)
    stockSuggestions.printContents(allTickers)


        



        


    

