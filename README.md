CMPUT404-project-socialdistribution
===================================

Build
============
Run the app locally for development:
```shell
docker build -t deadly-bird .      
docker run -p 8000:8000 deadly-bird
```

Deployment
============
To deploy the application via heroku:
```shell
heroku apps:create thedeadlybird    # This should only be run once to create the app
heroku container:login
heroku container:push web -a thedeadlybird
heroku container:release web -a thedeadlybird
```

Contributing
============

Send a pull request and be sure to update this file with your name.

Contributors / Licensing
========================

Generally everything is LICENSE'D under the Apache 2 license by Abram Hindle.

All text is licensed under the CC-BY-SA 4.0 http://creativecommons.org/licenses/by-sa/4.0/deed.en_US

Contributors:

    Karim Baaba
    Ali Sajedi
    Kyle Richelhoff
    Chris Pavlicek
    Derek Dowling
    Olexiy Berjanskii
    Erin Torbiak
    Abram Hindle
    Braedy Kuzma
    Nhan Nguyen 
    William Qi
    Justin Meimar
    Ritwik Rastogi
    Irene Sun
    Chase Johnson
