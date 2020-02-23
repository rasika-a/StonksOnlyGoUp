import praw
import pandas as pd
import requests
import stocker
from bs4 import BeautifulSoup

def getScore(sub):
    return sub.score

def getDDPostTitles():
    reddit = praw.Reddit(client_id='4AKaie_Ao4jaWQ',
                        client_secret='79N7FMADsGXgCvF0LqZJEiMtkg4',
                        user_agent='script:StonksPredictor')

    ddSubs = []
    for submission in reddit.subreddit('wallstreetbets').hot():
        if submission.link_flair_text == 'DD':
            ddSubs.append(submission)
    
    for submission in reddit.subreddit('wallstreetbets').new():
        if submission.link_flair_text == 'DD':
            ddSubs.append(submission)

    ddSubs.sort(key = getScore, reverse=True)
    ddSubsTitles = [sub.title for sub in ddSubs]
    return ddSubsTitles

def validateSP500(tickerName):
    table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df = table[0]

    for sp500Ticker in df['Symbol']:
        if tickerName == sp500Ticker:
            return True
    return False

def getTickers(ddSubsTitles):

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
   ]

    for titles in ddSubsTitles:
        words = [w for w in titles.split() if len(w) < 5 and w.upper() not in blacklist_words and w.isalpha()]
        
        for ticker in words:
            try:
                if wordnet.synsets(ticker):
                    continue
                elif len(stocker.predict.tomorrow(ticker)) == 0:
                    continue
                elif len(allResults) < 4:
                    allResults.add(ticker)
                else:
                    break
            except:
                continue
    
    return allResults

def printContents(collection):
    print("-------------------")
    for elem in collection:
        print(elem)
    print("-------------------")

def main():
    ddSubsTitles = getDDPostTitles()
    #printContents(ddSubsTitles)
    allTickers = getTickers(ddSubsTitles)
    printContents(allTickers)

if __name__ == "__main__":
    main()


        



        


    

