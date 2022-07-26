# You Edit This

This script will not work for you until you fix it!

* I don't know your setup for where you want to place this
in your site.
* I don't know how many days you want the "last lookup" to query.
* I don't know your QTH entity code.
* I don't know your Database access credentials...

Edit `ayiml.cgi`


```
## READ ME FIRST
# Four things you need to edit.

## 1.  This is the path, relative to your DocumentRoot
##     where the HTML lookup page is located and
##     the place where all of the flag-images and
##     Yes/No icons are located.
##     No trailing '/' character, please.
my $AYIML_HOME = "/lookup";

## 2.  How many days since now you want to look back for "past QSO"
my $AYIML_DAYS = 7;

## 3.  Your QTH DXCC entity
##     Consult list to find your ID number
##     The latest list:  http://www.arrl.org/country-lists-prefixes
##     (default is Mainland USA aka 291)
my $AYIML_YOUR_ENTITY_ID = 291;

## 4. Your MySQL Connection information
my $user   = 'dbuser';
my $auth   = 'dbpassword';
my $dbname = 'dbname';
```

