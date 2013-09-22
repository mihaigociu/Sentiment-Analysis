Sentiment-Analysis
==================

Python Sentiment Analysis

train and classify sentiments
s = SentimentAnalysis()

load the TweetCorups sentiments
note - you'll need to run the TweetCorupsInstaller first
s.initTwitterSentiments(0.8)

load the nltk movie reviews sentiments
s.initMovieReviews(0.75)

train a list of sentiments
neg_tweets = ['I do not like this car','I feel tired this morning', 'the concert sucks' ]
s.addSentiments(neg_tweets, 'negative')
s.addSentiments(['bad bad bad concert'], 'negative')

once you are done adding data, call the train method
s.train()

once you called the train function you can start classifing
to classify sentence use
s.classify(sentence)

or a paragraph
s.classifyParagraph(p)

you can also classify a url
there are two variable here, one is the url
and the second is the method which the text will be 
processed by, either via looping through the paragraphs
and returning the accumulative positive-negative value
s.classifyURL(url, False)
or by summarizing the text first and analysing the summarized version
s.classifyURL(url)
