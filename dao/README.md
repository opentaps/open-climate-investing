# Open Climate Investing DAO

## Goals

A DAO for creating open source climate investing analysis, including learning materials such as [the book](../book/README.md), industry specific climate analytical models (for example, energy, freight, airlines), and up to date analyses of individual companies' climate risk exposure.  

- Provide open, inclusive approach to rating companies' climate risk exposure.  "With enough eyeballs all bugs are shallow."
- Free for everybody: investors, government agencies, NGO's, and private individuals.
- Empower people everywhere with the knowledge and tools to understand what companies are doing (or not doing) about climate change.
- Create the broadest coverage of climate analysis for companies, following the Wikipedia, TripAdvisor, and Yelp models. 

This DAO will only provide climate investing analysis.  It is not a general investment analysis DAO.  It does not make investments.  It does not cover areas of Environmental, Social, Governance (ESG) or Corporate Social Responsibility (CSR) beyond climate.  It provides analysis of the climate risk exposure for investing in companies, which could be used as a gauge of the companies' climate actions.

## Why this DAO?

Analyzing companies' climate risk exposure and climate actions is complex -- see [the chapter on Analyzing Investments](../book/Analyzing-Investments.md).  Today, most of this analysis is performed by ESG vendors using proprietary data sets and models.  Only the largest institutional investors could afford detailed ESG analysis from these vendors, yet the results are often difficult to use for making investment decisions.  Furthermore, as the experience of the 2008 Credit Crisis shows, the vendors' incentives may be often aligned with those of the companies being rated rather than investors or the general public.  As a result, ESG metrics suffer from a lack of trust, and this in turn limits the incentives for companies to make climate disclosures.  

An open source approach to climate risk analysis based on openly available tools and community development creates a free data set of climate analysis which is available to anyone to use, study, and improve upon.  It could help individuals and NGO's along with institutional investors and government agencies understand what companies are doing or not doing about climate change.  By creating the largest base of potential users, we create an incentive for them to want and work for a better that is more useful for them.  As more users use it and improve upon it, it becomes more useful and draws in more users, creating a "flywheel effect."  If successful, such a community could produce the highest quality, least cost, and most inclusive source of information.

This is difficult to achieve, though, because open source projects usually under-funded and stay small.  __This is because they are too informal.__  There is an ecosystem of users and developers who symbiotically support each other, but without any formal reputation or funding schemes, there is a lot of information asymmetry which means that economically sound transactions do not happen.  For example, you might like the ideals of a project and want to contribute, but could you make at least a reasonable living do it?  Alternatively, you might be the loyal user of an open source project and would be willing to pay to support or improve it.  But whom do you pay?  It's not easy to know the skill levels of the various contributors in a project, or even if they're interested in working for pay.  And how do you know what other users will do if they paid to support the project?  Would some big corporate user pay for all the improvements anyway, so there was no need for you to pay?  Or are you the only one who would pay, so even if you paid, it wouldn't be enough?  Finally, if a group of you paid a few of the developers to do the work, who would judge if the work was satisfactory or not?

The DAO solves these problems with a formal implementation of the informal governance behind every open source project:

- The Reputation tokens let everyone see each contributor's level of expertise.
- The Activity tokens allow users to pool their resources to pay for improvements.
- A blockchain removes the need for the project to maintain a registry of these tokens.  Open source projects are small and don't need more overhead.
- The tokens are permanently owned by the members.  They don't depend on the continued existence of one contributor or company in the project.  

## Business Model

In today's financial markets, both companies looking to raise capital ("issuers") and investors pay fees to third parties such as Standard & Poor's and Moody's to rate investments.  Third-party ratings of companies' financial condition help objectively define what investments are appropriate for different group of investors.  This in turn allows companies sell securities to investors based on such ratings.  

The DAO's work similarly has value because it provides an objective, third-party rating for investors about the climate risks in companies.  The DAO provides a way for investors and companies to pay for these ratings through the purchase of tokens, which are then allocated to the community as payment for its work.  

## Mechanism

This DAO will use a combination of non-fungible Reputation, fungible Activity tokens, and badges:

- Reputation tokens represent the holder's level of expertise and cannot be transferred.  All members will start with a small balance of Reputation tokens.  They can earn more by taking some short online classes.  Most importantly, members earn more Reputation tokens by creating or improving the quality of the project's work: Its models, analyses, and training materials.  Reputation tokens gradually expire on their own, so inactive members eventually lose their standing.  
- Activity tokens can be used to pay for work by community members and can be transferred.  Members are given Activity tokens for performing work for the project, which could include building analytical models, analyzing companies, as well as writing code, maintaining content, and serving as ambassadors or community managers.  
- Badges represent the holder's specializations and cannot be transferred.  For example, they could represent specific areas of knowledge ("carbon markets", "climate accounting", "energy") or contribution ("investment analysis", "community building", "software development")  Over time they could be used to make Reputation tokens more "specific", for example identifying experts in specific areas.

Work is performed collaboratively in the DAO.  Each member contributes to a project and stakes a certain amount of Reputation tokens.  Once the required number of Reputation tokens is staked, then the project can be judged.  Each member who contributed in a project receives an allocation of the Activity tokens in proportion to the Reputation tokens they staked in the project.

All work performed by the DAO is part of the open source project.  Companies may engage the contributors "off project" to work on other jobs, and the contributors' Reputation tokens could help them get these jobs, but the results will not be certified by the DAO.  Contributors will need to stay active in the project if they want to maintain their levels of Reputation, as existing Reputation tokens expire automatically.

The DAO will eventually have a group of Judges (similar to committers or maintainers of open source projects and editors at Wikipedia) who will decide on whether to accept contribution or work for the project based on purely technical merits.  Once their work is accepted by the Judges, the members will receive Reputation tokens.  To become a Judge, a member must have a very high number of Reputation tokens.

The DAO will also have a group of Administrators to manage the project.  This group includes Judges and other members who are not technical experts (based on Reputations) but have made significant contributions based on their holdings of Activity tokens.  Each member's standing in the Administrators is determined based on 2x their holdings of Reputation tokens and 1x their holdings of Activity tokens.  A member can participate in votes of Administrators if they have at least 5% of this (2x Reputation + 1x Activity) tokens total.  Administrators will vote on a range of issues such as approve a new release or changes to the project (mundane) to revoking tokens for bad behavior (extraordinary.)  Mundane issues can be decided by a simple majority, and extraordinary issues will require super-majority (2/3) or more (80%?) 

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


## Questions

- How do we prevent the project's tokens from being used for speculation?  Should the Treasury fix the bid/ask prices of the Activity tokens with a stable coin?
- Should Reputation tokens be "staked" so each person can only work on a few projects at the same time, and do not spread themselves too thin to earn income?
- Should those who voted on the wrong answer lose Reputation tokens?
- How quickly should Reputation tokens expire?  Is 2% per month reasonable (half life of 36 months)?
- Should Activity tokens expire to discourage hoarding?  What is a reasonable rate?
- How to keep Judges honest and agreeable to working together?  
- How to prevent collusion and bad behavior, possibly off chain?
- Do we need a separate token for general standing in the community, or is the 2x Reputation + 1x Activity tokens count sufficient?
- What is the right combination of Reputation and Activity tokens to determine general standing in the community?
- Should Administrators be voted in, or just based on their Reputation and Activity tokens?  If the latter, what happens if a big holder who suddenly goes quiet?
