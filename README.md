# Cat-e-log Web Application
Cat-e-log is a fictional online marketplace where people can post items for sale. This project was used as a learning experience to get an understanding of what building a web application entails, from database to front end. The database `catelog` is a mock database of a fictional online marketplace, containing three tables `users`,`ad` and `categories`. Users can publiclly view the ads posted on Cat-e-log, with each ad containing a `name`, `price` and `description` along with the correspinding `category` in which the ad is listed under. Users can also create a profile which gives them the ability to `post` ads themselves (and `edit` and `delete`). To do so users must have a google account, as this is the only way to sign in. Please note the app is meant to for desktops online, and the UI is best viewed with viewport of 1200px of larger. The next version will be responsive and meant for all devices. 

# Requirements 
The requirements for this project are as follows:
-Virtual Box  
-Vagrant  
-Python `2.7.13`  
-PostgreSQL `2.7.3`  

# Setting up the Project
1. Install VirtualBox and Vagrant.
2. Clone or download the [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) 
3. Clone or download [this](https://github.com/andrew-hart/catalog_app) repository (make sure you do create this directory inside the `catalog` folder which is in the `vagrant` folder in the `fullstack-nanodegree-vm` repository  
4. Launch the Vagrant VM from inside the vagrant directory which is in in the fullstack-nanodegree-vm repository with the following command: `vagrant up`
5. Log in with the following command: `vagrant ssh`  
6. Navigate to the `vagrant` directory with the following command: `cd /vagrant`

# Setting up the database
1. Navigate to the `catalog` directory with the following command: `cd /catalog`
2. Populate the database by running `populate_catelog_db.py` with the following command: `python populate_catelog_db.py` (Note it is not necessary to to do this but if you want to view the app with some ad's then this step is necessary)

# Running the Project
1. Open a web browser and go to `localhost:5000`
2. From the command line run `application.py` 

Doing so will take you to the public homepage. If you have a google account you can click the `Login` button which will allow you to login using your Google account credentials. Doing so will create a profile for you and allow you to ad, edit and delete your own ads.

# Issues with Logging Out
To ensure that you can properly log out of the app, it is best to clear you cache before running the app. If this doesn't work try running the app in an incognito window.
