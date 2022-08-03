# A way to simulate trading stocks

You must have:

 - cs50
 - Flask
 - Flask-Session
 - requests

For CS50
 - pip3 install cs50

For flask
 - pip install Flask

For Flask-Session:
 - pip install Flask-Session

____________________________________________________________________________
MAKE SURE TO RESTART ALL APPS REQUIRING THESE LIBRARIES/ENVIROMENT VARIABLES
____________________________________________________________________________

You must register for an API key in order to query IEX's data:

 - Visit iexcloud.io/cloud-login#/register/
 - Select the “Individual” account type, then enter your name, email address, and a password, and click “Create account”.
 - Once registered, scroll down to “Get started for free” and click “Select Start plan” to choose the free plan.
 - Once you’ve confirmed your account via a confirmation email, visit https://iexcloud.io/console/tokens
 - Copy the key that appears under the Token column (it should begin with pk_)
 - In your terminal window, execute:
    UNIX/MAC : export API_KEY=value
    WINDOWS  : set    API_KEY=value
 where value is that (pasted) value, without any space immediately before or after the =

____________________________
How to run
____________________________

Type
  - flask run

into the terminal, then click on the link and you're set!

  
