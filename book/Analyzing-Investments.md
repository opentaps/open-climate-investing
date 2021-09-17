## Analyzing Investments

True story: I used to manage portfolios of mortgage backed securities.  These were very complex to analyze, because as interest rates changed, their rates of repayment changed.  As a result, their value relative to other bonds such as Treasuries would move differently as rates rose and fell.  So we and other investors and traders developed
very complex models calld "Option Adjusted Spread" or OAS models to evaluate them.  Unfortunately, the markets then moved in ways even these complex models couldn't predict. 
Actual mortage prepayments were far higher than any models predicted, the market was in disarray, and the OAS models came up with results that nobody believed.

Then one day, I thought "What if we ran the models backwards?"  This is commonly done when there is no fundamental model to evaluate an investment with.
Instead of plugging in parameters to calculate the price of, say, an option, you could 
plug in an option's market price to calculate the volatility that would get you that price.  This is called "implied volatility" and is actually how options of all sorts are traded.  Traderes use it trade different options versus each other, and they also compare their own views of market volatility with what the market is thinking.

Along those lines, I came up with an implied prepayment model where I could put in the prices of securities and come up with a prepayment model that would fit those prices.  
Then, I thought, I could compare that model with my own beliefs about future prepayments.  I didn't actually get to use it much, but I did get a paper published (Yay!), and now 
I see that paper even got cited by other papers (Wow!)

Later, I met a Trader at a Big Firm.  This Big Firm had lots of analysts, including one of the best prepayment analysts on the Street.  But he just sat there by himself off to the side and kept sending us scatterplots that looked like this:

I was dumbfounded.  This is nothing but a plot of prices against interest rates.  There's no sophisticated quantitative finance at work.  It was a spreadsheet he maintained himself (I think) without any of the research
department's fancy models.  But he calmly explained it to me: "This is the market's prepayment model.  I've got the history of the market and all those analysts with
all their models to compare the current prices with.  That's better than any one person's model."  He was way ahead of all the Wisdom of the Crowd talk that's in vogue nowadays, 
but it worked well for him.  This market-based model helped him identify mispricings and opportunities where big fancy models failed.  He went on to be _very_ successful.  

Today we're told that ESG or climate investing is hard because it's hard to get the data and hard to interpret them.  Hard to know which long-term scenario to use and how to 
analyze them.  But there is another way.  The market tells you.  There are hundreds, probably thousands, of smart people already looking at the climate risks of all sorts of 
traded investments such as stocks and futures.  You can piggy back on all the time and money they spent on data services, computer models, and research -- for free!  
All you need is market prices, a computer, and some [models](https://github.com/opentaps/open-climate-investing) -- which we gave you for free!

There are some very successful investors who only trade with market implied models and do no fundamental research.
For most investors, though, this kind of market implied model is not the end, maybe not even the beginning of the end, but it is the end of the beginning.
It is a good way to quickly flag down opportunities, such as mispricings between securities and differences between the market's thinking and your fundamental analysis.
It is a great check on your analysis, those "Am I Sure?" moments that could save your career.  It is also the best way to make sure that a fund you're sold really does
what they said it would do.

