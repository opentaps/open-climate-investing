# Open Climate Investing DAO

## Goals

- Provide open, inclusive approach to rating companies' climate risk exposure.  "With enough eyeballs all bugs are shallow."
- Free for everybody: investors, government agencies, NGO's, and private individuals.
- Empower people everywhere with the knowledge and tools to understand what companies are doing (or not doing) about climate change.
- Create the broadest coverage of climate analysis for companies, following the Wikipedia, TripAdvisor, and Yelp models. 

This DAO will only provide climate investing analysis.  It is not a general investment analysis DAO.  It does not make investments.  It does not cover areas of Environmental, Social, Governance (ESG) or Corporate Social Responsibility (CSR) other than climate.  It provides analysis of the climate risk exposure for investing in companies, which could be used as a gauge of the companies' climate actions.

## Mechanism

The DAO is a formal implementation of open source project management.  It is designed to help the Project to scale up and build out learning materials such as [the book](../book/README.md), industry specific climate analytical models (for example, energy, freight, airlines), and produce up to date analyses of individual companies' climate risk exposure.  

It will use a combination of non-fungible Reputation, fungible Activity tokens, and badges:

- Reputation tokens represent the holder's level of expertise and cannot be transferred.  All members will start with a small balance of Reputation tokens.  They can earn more by taking some short online classes.  Most importantly, members earn more Reputation tokens by creating or improving the quality of the project's work: Its models, analyses, and training materials.  Reputation tokens gradually expire on their own, so inactive members eventually lose their standing.  
- Activity tokens can be used to pay for work by community members and can be transferred.  Members are given Activity tokens for performing work for the project, which could include building analytical models, analyzing companies, as well as writing code, maintaining content, and serving as ambassadors or community managers.  
- Badges represent the holder's specializations and cannot be transferred.  For example, they could represent specific areas of knowledge ("carbon markets", "climate accounting", "energy") or contribution ("investment analysis", "community building", "software development")  Over time they could be used to make Reputation tokens more "specific", for example identifying experts in specific areas.

Work is performed collaboratively in the DAO.  Each member contributes to a project and stakes a certain amount of Reputation tokens.  Once the required number of Reputation tokens is staked, then the project can be judged.  Each member who contributed in a project receives an allocation of the Activity tokens in proportion to the Reputation tokens they staked in the project.

All work performed by the DAO is part of the open source project.  Companies may engage the contributors "off project" to work on other jobs, and the contributors' Reputation tokens help them get these jobs, but the results will not be certified by the DAO.  Contributors will need to stay active in the project if they want to maintain their levels of Reputation, as existing Reputation tokens expire automatically.

The DAO will eventually have a group of Judges (similar to committers or maintainers of open source projects and editors at Wikipedia) who will decide on whether to accept contribution or work for the project based on purely technical merits.  Once their work is accepted by the Judges, the members will receive Reputation tokens.  To become a Judge, a member must have a high number of Reputation tokens.

The DAO will also have a group of Administrators to manage the project.  They may be the same persons as the Judges.

The DAO will have a Treasury which sells and redeems Activity tokens for stablecoins.  Customers could buy Activity tokens to sponsor work in the project.  Contributors could redeem Activity tokens to get cash payments for the work they did.  The bid/ask spread of Activity tokens provides a permanent source of revenue to support the project.     

Activity tokens will only pay for the work and not its outcome.  There is no way to tie outcome to payment.  This is to ensure objectivity and quality. 

## Examples

Members will get Reputation tokens for doing the following:

```
Joining                      100
Read Article and Pass Test   100
Report a bug                 200
Fix a bug                   1000
Author Article/Chapter      1000
Contribute Model            5000
Analyze Company             5000
```

A sample project could be: "Rate the Climate Risk Exposure of Company X":

- A quorum of at least 10,000 Reputation tokens is required.
- The project period is 10 days
- 30,000 Activity tokens are allocated 
- 3,000 Activity tokens (10%) are allocated to Judges to certify the results
- 5,000 Reputation tokens are allocated
- Judges must stake 5,000 Reputation tokens (a maximum of X per Judge?) 

Work is done by 4 developers who each stake their Reputation tokens:

```
Arun            5,000
Barak           2,000
Chip           12,000
Duong          11,000

TOTAL          30,000
```

Then 3 Judges vote:

```
Farooz - YES    2,000
Gita - YES      2,000
Harold - NO     1,000
```

The project is accepted.  The payout of Reputation tokens to the contributors is `(Reputation tokens staked / Total reputation tokens staked) * Reputation tokens allocated`:

```
Arun              833
Barak             333
Chip             2000
Duong            1833
```

The payout of Activity tokens to the contributors is `Reputation tokens staked / Total reputation tokens staked) * Activity tokens allocated to contributors`:

```
Arun            5,000
Barak           2,000
Chip           12,000
Duong          11,000
```

The payout of Activity tokens to the Judges is `Reputation tokens staked / Total reputation tokens staked) * Activity tokens allocated to Judges`:

```
Farooz          1,200
Gita            1,200
Harold            600
```

## Advantages

Analyzing companies' climate risk exposure and climate actions is complex -- see [the chapter on Analyzing Investments](../book/Analyzing-Investments.md)  Today, most of this analysis is performed by ESG vendors using proprietary data sets and models.  Only the largest institutional investors could afford detailed ESG analysis from these vendors, yet the results are often difficult to use for making investment decisions.  Furthermore, ESG metrics from different vendors could give conflicting recommendations.  Finally, as the experience of the 2008 Credit Crisis shows, their incentives are often aligned with those of the companies rather than investors or the general public.  

An open source approach to climate risk analysis based on openly available tools and community development creates a free data set 

At the same time, though, open source projects tend to be small and poorly funded because they are informal.  There is an ecosystem of users and developers who symbiotically support each other, but without any formal reputation or funding schemes, there is a lot of information asymmetry which means that economically sound transactions do not happen.  For example, you might be the loyal user of an open source project, and you would be willing to pay a small amount to support or improve it.  But whom do you pay?  It's not easy to know the skill levels of the various contributors in a project, or even if they're interested in working for pay.  And how do you know what other users will do if they paid to support the project?  Would some big corporate user pay for all the improvements anyway, so there was no need for you to pay?  Or are you the only one who would pay, so even if you paid, it wouldn't be enough?  Finally, if a group of you paid a few of the developers to do the work, who would judge if the work was satisfactory or not?

The DAO solves these problems:

- The Reputation tokens let everyone see each contributor's level of expertise.
- The Activity tokens allow users to pool their resources to pay for improvements.
- A blockchain removes the need for the project to maintain a registry of these tokens.  Open source projects are small and don't need more overhead.
- The tokens are permanently owned by the members.  They don't depend on the continued existence of one contributor or company in the project.  

## Questions

- How do we prevent the project's tokens from being used for speculation?  Should the Treasury fix the bid/ask prices of the Activity tokens with a stable coin?
- Should Reputation tokens be "staked" so each person can only work on a few projects at the same time, and do not spread themselves too thin to earn income?
- Should those who voted on the wrong answer lose Reputation tokens?
- How quickly should Reputation tokens expire?  Is 2% per month reasonable (half life of 36 months)?
- How to keep Judges honest and agreeable to working together?  
