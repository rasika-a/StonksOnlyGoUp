import praw
from nltk.corpus import words as nltkwords
import alpaca_trade_api as tradeapi
import config

class tickerSuggestion:

    def __init__(self, PRAW_CLIENT_ID, PRAW_CLIENT_SECRET, PRAW_USER_AGENT, ALPACA_KEY_ID, ALPACA_SECRET):
        self.api = tradeapi.REST(ALPACA_KEY_ID, ALPACA_SECRET, api_version='v2')
        self.reddit = praw.Reddit(client_id=PRAW_CLIENT_ID, client_secret=PRAW_CLIENT_SECRET,
        user_agent= PRAW_USER_AGENT)

    def _getScore(self, sub):
        return sub.score

    def getDDPostTitles(self):
        ddSubs = []
        for submission in self.reddit.subreddit('wallstreetbets').hot():
            if submission.link_flair_text == 'DD':
                ddSubs.append(submission)
        
        for submission in self.reddit.subreddit('wallstreetbets').new():
            if submission.link_flair_text == 'DD':
                ddSubs.append(submission)

        ddSubs.sort(key = self._getScore, reverse=True)
        ddSubsTitles = [sub.title for sub in ddSubs]
        return ddSubsTitles

    def getTickers(self, ddSubsTitles):
        allResults = set()

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

        for titles in ddSubsTitles:
            word_list = [w for w in titles.split() if len(w) < 5 and w.upper() not in blacklist_words and w.isalpha()]
            
            for ticker in word_list:
                try:
                    ret = self.api.get_asset(ticker)
                    if len(allResults) < 4:
                        allResults.add(ticker)
                    else:
                        break
                except:
                    continue
        
        return allResults

    def printContents(self, collection):
        print("-------------------")
        for elem in collection:
            print(elem)
        print("-------------------")

if __name__ == "__main__":
    stockSuggestions = tickerSuggestion(config.PRAW_CLIENT_ID, config.PRAW_CLIENT_SECRET, config.PRAW_USER_AGENT, config.ALPACA_KEY_ID, config.ALPACA_SECRET)
    ddSubsTitles = stockSuggestions.getDDPostTitles()
    #stockSuggestions.printContents(ddSubsTitles)
    allTickers = stockSuggestions.getTickers(ddSubsTitles)
    stockSuggestions.printContents(allTickers)


        



        


    

