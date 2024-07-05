#!/bin/bash

# Add changes to git
git add templates/index.html

# Commit your changes
git commit -m "Update"

# Push to Heroku
git push heroku main

# Restart your Heroku app
heroku restart -a alluring-zion-33627
