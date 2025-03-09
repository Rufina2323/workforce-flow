# First project checkpoint

The goal of the first phase was to extract people pages from LinkedIn.

### Main Steps

1. [LinkedIn API](https://github.com/tomquirk/linkedin-api) from GitHub repository

Despite the fact that the API repository has 2.6K stars and many contributors, it turns out that not all endpoints in it are working. The endpoints for searching people by university name turned out not to be fully functional.

 ![Alt text](images/api_problems.png)

 For the following problem in comments users shared that they had faced the same problem.

  ![Alt text](images/api_problems_2.png)

2. Check other APIs

 - official [LinkedIn API ](https://learn.microsoft.com/es-es/linkedin/shared/api-guide/concepts?context=linkedin%2Fconsumer%2Fcontext)

 There is a need to create a company page but linkedIn does not allow to do it. Maybe it's because the account is not very popular


 ![Alt text](images/company_page.png)

The other APIs have a trial period and offer to try their functionality, but the number of credits issued for free is insufficient for our purposes.
 - [Proxycurl](https://nubela.co/proxycurl/docs?python#school-api): given amount of credits 10, the minimum needed number is 30 😅

 3. Selenium

Selenium helped to obtain information on 993 users who had connection to Innopolis University, including their area of work and LinkedIn profile link.

The code for data collection can be found in `scrape_linkedin.py`. 


### Future Steps

In the next phase, we plan to clean, explore and analyze data. Moreover, we are thinking about additional data collection.



