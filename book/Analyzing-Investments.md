## Analyzing Investments

True story: I used to manage portfolios of mortgage backed securities.  These were very complex to analyze, because as interest rates changed, their rates of repayment changed.  As a result, their value relative to other bonds such as Treasuries would move differently as rates rose and fell.  

So we and other investors and traders usedvery complex models called "Option Adjusted Spread" or OAS models to evaluate them.  These models projected interest rates and then repayment rates of the mortgages for 30 years under thousands of different scenarios, then aggregated the scenarios to come up with values for securities in the present day.  The OAS models were calibrated to the market prices of treasury or interest rate swap rates and options, so that they, in effect, valued the mortgage backed securities against them.  This also allowed mortgages to be hedged with treasuries, swaps, and options, which is what mortgage hedge funds in fact did.  But since these OAS models all relied on models of prepayments based on historical analysis of the data, in effect these funds were making bets on the correctness of their prepayment models.


Then the markets moved in ways even these complex models couldn't predict: Rates fell a lot more than expected, and actual mortage repayment rates were far higher than any models predicted.  As a result, the OAS models came up with results that nobody believed.  They were no longer useful for hedging or valuing securities.  Whoever still used them was in effect flying blind.

So one day, I thought "What if we ran the models backwards?"  This is commonly done when there is no fundamental model to evaluate an investment with.
Instead of plugging in parameters to calculate the price of, say, an option, you could 
plug in an option's market price to calculate the volatility that would get you that price.  This is called "implied volatility" and is actually how options of all sorts are traded.  Traderes use it trade different options versus each other, and they also compare their own views of market volatility with what the market is thinking.

Along those lines, I came up with an implied prepayment model where I could put in the prices of securities and come up with a prepayment model that would fit those prices.  
Then, I thought, I could compare that model with my own beliefs about future prepayments.  I could also use it to trade or hedge one group of securities with another.  I didn't actually get to use it much, but I did get a paper published (Yay!), and now I see that paper even got cited by other papers (Woohoo!)

Later, I met a Trader at a Big Firm.  This Big Firm had lots of analysts, including one of the best prepayment analysts on the Street.  But he just sat there by himself off to the side and kept sending us scatterplots that looked like this:

![A Market Based Model for Mortgage Backed Securities](images/mbs_market_model.PNG)

Huh...  This is nothing but a plot of prices against interest rates.  There's no sophisticated quantitative finance at work.  It was a spreadsheet he maintained himself (I think) without any of the research
department's fancy models.  People thought of his scatterplots as something between a toy and a joke.  But as he told it, "This is the market's OAS model.  I've got the history of the market and all those analysts with
all their models to compare the current prices with.  That's better than any one person's model."  He was way ahead of all the Wisdom of the Crowd talk that's in vogue nowadays, 
but it worked well for him.  This market-based model helped him identify mispricings and opportunities where big fancy models failed.  He went on to be _very_ successful.  

Today we're told that ESG or climate investing is hard because it's hard to get the data and hard to interpret them.  Hard to know which long-term scenario to use and how to 
analyze them.  But this is nothing new, and there is a way to get around these problems.  Let the market tell you.  There are hundreds, probably thousands, of smart people already looking at the climate risks of all sorts of 
traded investments such as stocks and futures.  You can piggy back on all the time and money they spent on data services, computer models, and research -- for free!  All you need is market prices, a computer, and some [models](https://github.com/opentaps/open-climate-investing) -- which we gave you for free!

There are some very successful investors who only trade with market implied models and do no fundamental research.
For most investors, though, this kind of market implied model is not the end, maybe not even the beginning of the end, but it is the end of the beginning.
It is a good way to quickly flag down opportunities, such as mispricings between securities and differences between the market's thinking and your fundamental analysis.
It is a great check on your analysis, those "Am I Sure?" moments that could save your career.  It is also the best way to make sure that a fund you're sold really does
what they said it would do.

### Market Implied Model

_"Come on pal, tell me something I don't know, it's my birthday. Surprise me." - Gordon Gekko_

Now let's take a closer look at the market implied model.  First a little bit about how these models came about.

Long ago (up to the 1950's), investing meant sifting through financial statements, combing through the news wires, and scuttling about for every little "butt" of information about companies.  Then in the early 1960's, a young group of
finance professors revolutionized the field by saying none of that mattered.  In fact, it didn't even matter if you knew you were investing in livestock or preferred stock.  All that mattered was how the assets you owned
moved with the overall market.  That could be summarized in a simple statistic, called the _Beta_, which could be calculated from a regression of the returns of an asset versus the returns of the market.  Once you had this Beta,
you could tell how risky an asset was, how two assets should move versus each other, and whether an asset returned enough to compensate for its risks.  

This revolutionary insight turned finance into a quantitative field.  Today few finance departments teach investing the way Ben Graham taught it to Warren Buffett.  The top traders at hedge funds are more likely to be 
physicists than accountants.  And though it is still vociferously by the "stock pickers" in the industry, the truth is that this new way of thinking, called "Modern Portfolio Theory," worked well -- in some important applications:

 * It's great for finding short-term mispricings and trade around them.  If two stocks are supposed to move together at a certain ratio with high probability, and one moves first, it's (usually) a good bet the other will move soon.
 * It's great for analyzing the performance of portfolios.  While the investment industry touts its stock picking prowess, most funds contain so many stocks, their returns could be reduced to statistical relationships versus major index returns.

But the first model of Modern Portfolio Theory, called "Capital Asset Pricing Model" with the single Beta, was just the beginning.  Over time, the quants did find that other important factors could be
statistically shown to affect returns.  For example, there are long periods where large cap stocks dominated, followed by periods where small cap stocks came out on top.  Returns were also trending -- good stocks keep going up.  There's
probably not a mirror universe where AOL and Nokia bested Google and Apple, and K-Mart is Amazon.

So in 1993, the Fama French 3-factor model was introduced to add two more parameters, one for size and one for momentum, to better explain returns.  This eventually led to the development of ever more sophisticated factor models with
ever more factors, such as the
[MSCI BARRA Multi Factor Model](http://cslt.riit.tsinghua.edu.cn/mediawiki/images/4/47/MSCI-USE4-201109.pdf).

For analyzing climate risk, we found one such model: [Carbon Risk Management (CARIMA)](https://www.uni-augsburg.de/de/fakultaet/wiwi/prof/bwl/wilkens/sustainable-finance/downloads/).  It was developed by Universtat Augsburg 
with funding from the German Federal Ministry of Education and Research.  CARIMA is a multi-factor market returns model based on the Fama French 3 Factor Model plus an additional factor for carbon risk.  We have taken the original model and created an [open source project](https://github.com/opentaps/open-climate-investing) which could be used to run it as scale and analyze large samples of stocks and portfolios over time.

What this model does is explain the sensitivity of any asset (could be a stock or a fund, or even futures on commodities -- anything that is traded would work) based on the return differential of stocks with high carbon risk (Brown) vs
those with low carbon risk (Green).  The original research paper provided a data series for the Brown Minus Green (BMG) factor until the end of 2018.  With this model, we could now get the market's measure of the climate risk of a
stock by seeing how its prices have behaved.  In other words, what do all those smart people pouring through carbon disclosures, ESG data, and running scenarios, not to mention analyzing the company's business model, assets, and 
operations, really think?

Most importantly, we have turned all those disclosures, data, and scenarios -- the vague ESG stuff that make portfolio managers say "How do I monetize this?" (and traders say
"How the f@#! am I going to make money with this s#&!" -- into something you could trade with.  You make money 
with ESG the old fashioned way -- by finding what the market missed.  And getting it right. 

Now let's see what it looks like with a few examples.

What does "market implied" mean, after all?  It means relative to other traded assets in the market.  _Relative to the other assets_, how risky is it?  Is it over- or undervalued?  And, most important of all, is the market missing something, or are you?

### Fundamental Analysis

_"The most valuable commodity I know of is information" - Gordon Gekko_

I'm going to (figuratively) bet that given the limited awareness of climate among investors, the market is probably wrong about a lot of things.  In other words, there are 
probably a lot of opportunities if you invested some time in analyzing companies' climate exposures.  So let the market implied model be a starting point, and let's dig in.

Climate change is a long-term process with a lot of uncertainty.  How it plays out, and then how that affects an actual company, could depend on a number of scenarios.  Thus
analyzing climate exposure is, in many ways, similar to analyzing mortage-backed securities:  You will need to project multiple scenarios far into the future, calculate their 
financial ipacts, and then attach probabilities to the scenarios to arrive at their expected values today.  (Now you see why I needed to tell you aobut mortgages and OAS models.)

The key steps of this anlaysis are:

 * The company's current climate exposures: How much are its Greenhouse Gas (GHG) emissions now?  What are its assets?
 * How those exposures will change: Every company talks about "sustainability" these days.  What is it reallying doing to reduce its climate exposures or "decarbonize"?
 * Overlaying scenarios: How will potential events affect the company, given its current exposures and its path to decarbonize?
 * Valuing the scenarios: Under each scenario, what is the economic impact (positive or negative) to the company?
 * Comparing versus the market: Now the market implied values come in handy.

As you can see, climate investing is not as simple as divesting from oil companies.  Just like you wouldn't buy a stock based on its current earnings, you shouldn't just rely on 
current emissions to make climate investment decisions.  Instead, you have to account for both current positions, management actions, and potential long-term scenarios.  This is
what makes investing fun!
