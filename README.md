# Python script to print current monzo balances to command line

This is a basic script that can be used to fetch your current personal and joint account balances from Monzo and print them to your command line. 

This is based on Monzo's work at https://github.com/monzo/reference-receipts-app. The readme, oauth2.py and config.py lean heavily on that repo. 

## Getting Started

You need a Monzo account to register and manage your OAuth2 API clients. If you don't yet have a Monzo account, you can [open an account](https://monzo.com) on your phone now -- it takes no more than a few minutes with an ID on hand. Search for `Monzo` in App Store and Play Store.

To register your API client, head to [developers.monzo.com](http://developers.monzo.com), and select `Sign in with your Monzo account`. You'll receive an email sign in link, as the Developers Portal itself is an OAuth application. Once you've logged in, go to `Client`, and click on `New OAuth Client`. You'll need to provide the following information to register a client:

* **Name**: The name of your application. You will see it when redirected to auth.monzo.com to sign in.
* **Logo URL**: A link to the logo image of your application, although this is not used in this application.
* **Redirect URLs**: The callback URLs to your application. In this example application, we don't actually handle a callback, but only parse the temporary auth code returned. Therefore we use one fake local URL of `https://localhost`. A real application will ideally handle auth flows automatically, and an internet-accessible callback endpoint will be needed here instead.
* **Description**: A short description on the purpose of your application. Feel free to put anything here.
* **Confidentiality**: A confidential API client will keep the OAuth2 secret from your user, and hence will be allowed to [refresh](https://docs.monzo.com/#refreshing-access) access tokens with a refresh token. While a non-confidential client may expose its OAuth2 secrets to the client, such as embedded in the JavaScript of a web application. As our simple client will be kept locally for now, feel free to set it as `Confidential` here. This app might not work if it is not set as confidential.

## Set Up the Repo

Once you have registered your API client, you will have received a Client ID and a Client Secret. The next step is to clone this repository:
```
git clone https://github.com/jyaffe/monzo.git
cd monzo
```

Now we need to configure the client:
```
cp config-example.py config.py
```
And edit `config.py` with your favourite editor to set `MONZO_CLIENT_ID` and `MONZO_CLIENT_SECRET`. 

The example client is written in Python3. You will ideally need Python3.6 and `pip`. We need to install some dependencies, preferably in a virtual environment. We will be using `pyenv` [article](https://opensource.com/article/19/6/python-virtual-environments-mac) and `virtualenvwrapper` in this example:
```
mkvirtualenv monzo
workon monzo
pip install -r requirements.txt
```

## Running the Client

Your client should now be ready to use. To see a quick demo of this example client, simply run the `main.py` script and follow the authentication flow as prompted.

When the script asks you for the callback link, it is looking for the link that Monzo ask you to visit in the email they send to you after providing your address to the developer site.

The client should print out a list of your personal and joint account balances, including those of any live pots. 

## Please Note - Authentication

As your account authentication details are stored locally with the ability to refresh the tokens, the script includes a function to log out of your account and reset the config file to make sure that any future access requires the strong authentication process of going through the developer site and approving on the Monzo app. This function is included in the script initially but can be excluded by deleting or commenting out the line at the end of `main.py` as so: `# client.log_out()`

You should keep the log out function if you are working on a shared device or do not want to leave access to your account open for a period of time as the details can be used to access the full set of Monzo APIs.

If you choose to remove the log out function, the main access code will expire after a period of time, but the refresh code will allow you to obtain a new one without going through the strong authentication process. 