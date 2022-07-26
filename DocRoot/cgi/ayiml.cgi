#!/usr/bin/perl

# Copyright (c) 2007 Jeff Wandling (W7BRS)
#
# Licensed under the terms of the BSD 3-Clause License
#

use strict;

use DBI;
use CGI;

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

## Thanks...


## Avoid editing below this line...

my $BigWorked = "${AYIML_HOME}/img/big-worked.png";
my $BigNotWorked = "${AYIML_HOME}/img/big-notworked.png";


## No chicanery.  We just don't deal with data that is plainly too long.

## Get ready to process the query, first get a handle to the CGI interface.
my $q = new CGI;

## Get the "callsign" if any.
my $cs = $q->param('cs');

## Get the "last check" flag if any.
my $check = $q->param('check');

## We die gracefully if the data length exceeds our limit.
## No chicanery.  We just don't deal with data that is plainly too long.
## If you think you're going to work stations with callsigns
## over 16 characters long? Adjust as necessary.

do {
	  print "Content-type: text/html\n\n";
	 exit(0);
 } if (length $cs > 16 || length $check > 16);


## Boiler plate.. we are defining strings that represent the names
## of the bands that can be worked.  Note the order. Maintain
## the order.

my @bands = (
    '160m', '80m', '40m', '30m',  '20m', '17m', '15m', '12m',
    '10m',  '6m',  '2m',  '70cm', '23cm'
);



## Handles for quering the database.
my $sth;
my $sth2;

## Attributes associated with the DB handle connection
my %attr;



my $dbh = DBI->connect( 
                 "DBI:mysql:database=$dbname;host=localhost",
                 $user, $auth, \%attr );

## Are we checking for Last QSO's?
if ($check)
{
    ## Emit the HTTP content header and then..
    print $q->header;
    ## emit the data from checking last contacts.
    &ListLast($check);
    ## We're done.
    &Quit;
}
else
{
    ## We already checked raw input is within length,
    ## but we check that the characters IN the callsign
    ## are meant to be callsign characters.  We allow
    ## a-z, A-Z, 0-9 and the '/' character. Thats it.

    if ( length($cs) < 16 && $cs =~ /([\w\/]{1,15})/ )
    {
        ## We exctract the callsign from the argument
        $cs = $1;
    }
    else
    {
        ## Not a valid callsign (too long or invalid characters)
        &NoCall;
        ## We're done, bye.
        &Quit;
    }
}

## OK so this is a temporary hash of data representing matches
## for the query per band.

my %bandplan = (
    '160m' => 0,
    '80m'  => 0,
    '40m'  => 0,
    '30m'  => 0,
    '20m'  => 0,
    '17m'  => 0,
    '15m'  => 0,
    '12m'  => 0,
    '10m'  => 0,
    '6m'   => 0,
    '2m'   => 0,
    '70cm' => 0,
    '23cm' => 0
);

## We're checking a callsign vs checking "last QSO"
## If we were checking Last QSO's then $cs is null, else #cs is not null.
if ( $cs ne '' )
{

    ## Alright now we're talking to the MySQL Database based on your
    ## Log4M Schema.
    ##

    ## The intent of the query:
    ##  Yield rows of data where in each row,
    ##    we emit the callsign of the QSO, how many contacts on 
    ##    each band, and the band
    ## Note: the QSO mode has to end with 'SB' which means USB, LSB, SSB etc..
    ## Your data in your MySQL Database may not have differentiated
    ## between SSB and USB   or SSB and LSB.   There will be another
    ## query for FM modes and CW modes and Digital Modes...  We're just
    ## doing the "SSB" modes first...

    my $sql =
      "SELECT DISTINCT callsign, COUNT(band), band " .
      "FROM log " .
      "WHERE callsign = '"
      . $cs
      . "' AND mode LIKE '%SB' group by band";

    ## Call it paranoia....  Probably not necessary, but safety on the
    ## query is still warranted.  This is not the best way to do this.
    if ( length($sql) > 140 ) { &NoCall; &Quit; }

    ## prepare the QSL query
    $sth = $dbh->prepare($sql);
    ## run it.
    $sth->execute;

    ## Render the results..

    ## This generates raw HTTP output.. first the HTTP header
    ## for content.
    print $q->header;

    ## Now, emit HTML.. We're using the old "Clay Tablet Printer" technique.

    ## Print everything and extrapolate variables UNTIL the statement
    ## reaches the token EOF
    print <<"EOF";
<head>
<style>

<!-- how we alternate color dark grey, light grey like old fan-fold
     paper -->
tbody tr:nth-child(odd) { background: #CCC; }
tbody tr:td.nth-child(even) { background: #DDD; }
</style>
</head>
EOF

    ## Back to the perl code...

    ## Hardwire the results...
    print "AYIML (c) Copyright 2022 Jeff Wandling<br>\n";
    print "Licensed under BSD 3-Clause License. All Rights Reserved.<br>\n";
    print "<p>Results for <b>", uc($cs), "</b><br>\n";

    ## The results go into a TABLE

    ## Across the top, the header row
    ##   the names of the bands..  Note sizes -- they match
    ##   the size of the icons used for Yes or No.
    print "<table style=\"border-collapse: collapse;\">\n",
      "<tr>\n",
      "<th style=\"background-color:\#CCCCCC;",
      "background-repeat:no-repeat;width:43px; height:27px;\"></th>",
      "<th style=\" background-color:\#CCCCCC;",
      "background-repeat: no-repeat; width:43px;height:27px;\">160m</th>",
      "<th style=\" background-color:\#CCCCCC;",
      "background-repeat: no-repeat; width:43px;height:27px;\">80m</th>",
      "<th style=\" background-color:\#CCCCCC;",
      "background-repeat: no-repeat; width:43px;height:27px;\">40m</th>",
      "<th style=\" background-color:\#CCCCCC;",
      "background-repeat: no-repeat; width:43px;height:27px;\">30m</th>",
      "<th style=\" background-color:\#CCCCCC;",
      "background-repeat: no-repeat; width:43px;height:27px;\">20m</th>",
      "<th style=\" background-color:\#CCCCCC;",
      "background-repeat: no-repeat; width:43px;height:27px;\">17m</th>",
      "<th style=\" background-color:\#CCCCCC;",
      "background-repeat: no-repeat; width:43px;height:27px;\">15m</th>",
      "<th style=\" background-color:\#CCCCCC;",
      "background-repeat: no-repeat; width:43px;height:27px;\">12m</th>",
      "<th style=\" background-color:\#CCCCCC;",
      "background-repeat: no-repeat; width:43px;height:27px;\">10m</th>",
      "<th style=\" background-color:\#CCCCCC;",
      "background-repeat: no-repeat; width:43px;height:27px;\">6m</th>",
      "<th style=\" background-color:\#CCCCCC;",
      "background-repeat: no-repeat; width:43px;height:27px;\">2m</th>",
      "<th style=\" background-color:\#CCCCCC;",
      "background-repeat: no-repeat; width:43px;height:27px;\">70cm</th>",
      "<th style=\" background-color:\#CCCCCC;",
      "background-repeat: no-repeat; width:43px;height:27px;\">23cm</th>",
      "</tr>\n",
      ## Done printing the header row of the TABLE...
    
      ## We're going to print our first row of data.. the SSB data
      "<tr>\n",
      "<td style=\" background-color:\#CCCCCC\">SSB</td>\n";

      ## Remember that query?  Let's peel off the results..
      if ( $sth->rows > 0 )
      {
        for ( my $i = 0 ; $i < $sth->rows ; $i++ )
        {
            my @x = $sth->fetchrow_array;
 
            ## $x[2] is the 3rd field of the results.
            ## the third field of the results is...
            ## (reminder:  "SELECT DISTINCT callsign, COUNT(band), band ")
            ##  ... the band ..
            ## We cache (key is the band), with the value of the band..
            ##  Eg $bandplan{"17m"} = "17m"
            ## If there is no match for some $bandplan{band} it's 0.

            $bandplan{ $x[2] } = "$x[2]";
        }
     }

    ## for all known bands

    foreach my $xx (@bands)
    {
        ## if we caught a hit on that band (ie., not 0)
        if ( $bandplan{$xx} )
        {
            ## We emit the HTML to put the "worked" icon
            ## Note the size. It matches the size of the graphic
            ## and the table cells defined.
            ## If you do fiddle around with different graphics
            ## take note of the size and adjust accordingly.
            print "<td style=\"width:43px;height:27px;",
              "background-repeat:no-repeat;",
              "background:url(${BigWorked});\">";
        }
        else
        {
            ## We emit the HTML to put the "not worked" icon
            print "<td style=\"width:43px;height:27px;",
              "background-repeat:no-repeat;",
              "background:url(${BigNotWorked});\">";
        }
        print "</td>\n";
    }

    ## End the row for all of the SSB modes matched.
    print "</tr>\n\n",

    ## Now we're doing "CW" mode...

      "<tr>\n",
      "<td style=\"background-color:\#CCCCCC\">CW</td>\n";

    ## Differnet query...
    my $sql =
      "SELECT DISTINCT callsign, COUNT(band), band " .
      "FROM log " .
      "WHERE callsign = '"
      . $cs
      . "' and mode = 'CW' group by band";

    # Paranoia...
    if ( length($sql) > 140 ) { &NoCall; &Quit; }

    ## prepare it.
    $sth = $dbh->prepare($sql);

    ## run it.
    $sth->execute;

    ## reset the temp hash for new results..

    my %bandplan = (
        '160m' => 0,
        '80m'  => 0,
        '40m'  => 0,
        '30m'  => 0,
        '20m'  => 0,
        '17m'  => 0,
        '15m'  => 0,
        '12m'  => 0,
        '10m'  => 0,
        '6m'   => 0,
        '2m'   => 0,
        '70cm' => 0,
        '23cm' => 0
    );

    ## Same as before.. we populate new hits on working
    ## that "cs" station on any band in the mode of CW
    if ( $sth->rows > 0 )
    {
        for ( my $i = 0 ; $i < $sth->rows ; $i++ )
        {
            my @x = $sth->fetchrow_array;
            $bandplan{ $x[2] } = "$x[2]";
        }
    }

    ## Same as before.. we emit cells with "worked" or "not worked"
    ## Icon.

    foreach my $xx (@bands)
    {
        if ( $bandplan{$xx} )
        {
            print "<td style=\"width:43px;height:27px;",
              "background-repeat:no-repeat;",
              "background:url(${BigWorked});\">";
        }
        else
        {
            print "<td style=\"width:43px;height:27px;",
              "background-repeat:no-repeat;",
              "background:url(${BigNotWorked});\">";
        }
        print "</td>\n";
    }

    ## Done with CW Mode
    print "</tr>\n\n",


    ## Now do the same with FM Mode...
      "<tr>\n",
      "<td style=\" background-color:\#CCCCCC\">FM</td>\n";


    my $sql =
      "SELECT distinct callsign, count(band), band FROM log where callsign = '"
      . $cs
      . "' and mode = 'FM' group by band";

    if ( length($sql) > 140 )
    {
        &NoCall;
        &Quit;
    }

    $sth = $dbh->prepare($sql);
    $sth->execute;

    my %bandplan = (
        '160m' => 0,
        '80m'  => 0,
        '40m'  => 0,
        '30m'  => 0,
        '20m'  => 0,
        '17m'  => 0,
        '15m'  => 0,
        '12m'  => 0,
        '10m'  => 0,
        '6m'   => 0,
        '2m'   => 0,
        '70cm' => 0,
        '23cm' => 0
    );

    if ( $sth->rows > 0 )
    {
        for ( my $i = 0 ; $i < $sth->rows ; $i++ )
        {
            my @x = $sth->fetchrow_array;
            $bandplan{ $x[2] } = "$x[2]";
        }
    }

    foreach my $xx (@bands)
    {
        if ( $bandplan{$xx} )
        {
            print "<td style=\"width:43px;height:27px;",
              "background-repeat:no-repeat;",
              "background:url(${BigWorked});\">";
        }
        else
        {
            print "<td style=\"width:43px;height:27px;",
              "background-repeat:no-repeat;",
              " background:url(${BigNotWorked});\">";
        }
        print "</td>\n";
    }

    print "</tr>\n\n",

    ## Done with FM Mode... Now..

    ## Do another row for "Digital" modes.

      "<tr>\n",
      "<td style=\" background-color:\#CCCCCC\">DIGI</td>\n";

    ## The Log4M Database will store "digital" modes as
    ## "FT8", or "FT4", etc.. This is one area that could be
    ## imrpoved because there are just too many digital modes...
    ## I don't do a lot of digital modes so I don't care to make
    ## the effort here, but a different query wouldn't be that
    ## hard to make -- the clause would change to something that
    ## covers all digital modes (or all modes that are NOT SSB  and NOT FM
    ## and NOT CW)...  which ever way is simpler...

    my $sql =
      "SELECT distinct callsign, count(band), band FROM log where callsign = '"
      . $cs
      . "' and mode regexp 'FT8|FT4|JS8|JT%' group by band";

    if ( length($sql) > 140 )
    {
        &NoCall;
        &Quit;
    }

    $sth = $dbh->prepare($sql);
    $sth->execute;

    ## Again, reset the temporary hash map for results.

    my %bandplan = (
        '160m' => 0,
        '80m'  => 0,
        '40m'  => 0,
        '30m'  => 0,
        '20m'  => 0,
        '17m'  => 0,
        '15m'  => 0,
        '12m'  => 0,
        '10m'  => 0,
        '6m'   => 0,
        '2m'   => 0,
        '70cm' => 0,
        '23cm' => 0
    );

    if ( $sth->rows > 0 )
    {
        for ( my $i = 0 ; $i < $sth->rows ; $i++ )
        {
            my @x = $sth->fetchrow_array;
            $bandplan{ $x[2] } = "$x[2]";
        }
    }

    foreach my $xx (@bands)
    {
        if ( $bandplan{$xx} )
        {
            print "<td style=\"width:43px;height:27px;",
              "background-repeat:no-repeat;",
              "background:url(${BigWorked});\">";
        }
        else
        {
            print "<td style=\"width:43px;height:27px;",
              "background-repeat:no-repeat;",
              " background:url(${BigNotWorked});\">";
        }
        print "</td>\n";
    }

    print "</tr>\n\n", "</table>\n";

    ## We're done with all of the modes. We are done filling out
    ## matrix chart for Yes or No

    ## The next phase for looking up a specific call sign is getting
    ## meta data about each contact.  

    ## The matrix above showed that we worked or did not work a station.
    ## But if we worked a station, the matrix doesn't show how many times
    ## or when we worked it, etc...

    ## This next query enumerates all of the instances we actually
    ## worked that station..

    ## This query depends on the schema of the Log4M database.
    ## we get the qso date from "qsodate" but we reformat it to DD-MM-YYYY

    ## we try to get the RST we sent them, the RST they sent us.
    ## we also get the band, the mode....

    ## subtle but important -- the "order by band" must yield
    ## results in the SAME order as the array we define in this
    ## script for each band.  Yes, it can be converted into
    ## an associative array and all that.. But this is simpler. Maybe..

    my $sql2 =
     "SELECT distinct callsign, date_format(qsodate, \"%e-%b-%Y\"), " 
      .      "rstsent, rstrcvd, band, mode "
      . "FROM log "
      . "WHERE callsign = '"
      . $cs
      . "' order by band, mode";
    $sth2 = $dbh->prepare($sql2);
    $sth2->execute;

    if ( $sth2->rows > 0 )
    {
        ## Only if we had results...  Print the header of a new
        ## table...
        print "<br>\n",
          "<br>\n",
          "<b>QSO Details:</b><br>\n",
          "<table border=\"0\">\n",
          "<tbody>\n",
          "<tr>",
          "<th>Call</th>",
          "<th>QSO Date</th>",
          "<th>RST Sent</th>",
          "<th>RST Rcvd</th>",
          "<th>Band</th>",
          "<th>Mode</th>",
          "</tr>\n";

        ## and results...
        for ( my $i = 0 ; $i < $sth2->rows ; $i++ )
        {
            my @det = $sth2->fetchrow_array;
            print "<tr><td align=\"right\"> ",
                  join( "</td><td align=\"right\">", 
                        @det ), 
                  "</td></tr>\n";
        }
        print "</tbody>\n", "</table><p>\n";
    }
    print "<p>\n";

    ## and that's the end of the line for detail about working
    ## a specific station...
}


## We're done with this script..
&Quit;

# Nothing else can execute ... 



#####


## these are functions called during flow of execution above
## if the point is to query for the last "W"-land QSO
## or last "DX"-land QSO...

sub ListLast
{
    my $flag = shift;
    print <<"EOFLAST";
<head>
<style>
tbody tr:nth-child(odd) { background: #DDD; }
tbody tr:td.nth-child(even) { background: #CCC; }
</style>
</head>
EOFLAST
    my $sql;

    if ( $flag eq 'dx' )
    {

        ## Our query is just getting the essential metrics for
        ## last QSO that are NOT with stations in the ${AYIML_YOUR_ENTITY_ID}

        ## Two queries nested.  It selects the DXCC entity
        ## information for those contacts you've made for each entity
        ## in your log that is in the past ${AYIML_DAYS} from the moment
        ## the query runs.
        $sql =
            "SELECT dxcc, country, callsign, band, mode, "
            . "DATE_FORMAT(qsodate, \"%e-%b-%Y\") "
            . "FROM ( SELECT * "
            . "       FROM log "
            . "       WHERE block IS NULL AND "
            . "       dxcc <> ${AYIML_YOUR_ENTITY_ID} AND qsodate >= NOW() - "
            . "       INTERVAL ${AYIML_DAYS} DAY "
            . "ORDER BY qsodate desc) SUB ORDER BY qsodate DESC";

    }
    else
    {
        ## Our query is just getting the essential metrics for
        ## last QSO that ARE with stations in the ${AYIML_YOUR_ENTITY_ID}
        ## Same as above except when the DXCC entity is in
        ## in ${AYIML_YOUR_ENTITY_ID}
        $sql =
            "SELECT dxcc, country, callsign, band, mode, "
            . "DATE_FORMAT(qsodate, \"%e-%b-%Y\") "
            . "FROM ( SELECT * "
            . "       FROM log "
            . "       WHERE block IS NULL AND "
            . "       dxcc = ${AYIML_YOUR_ENTITY_ID} AND qsodate >= NOW() - "
            . "       INTERVAL ${AYIML_DAYS} DAY "
            . "ORDER BY qsodate desc) SUB ORDER BY qsodate DESC";
    }
    $sth = $dbh->prepare($sql);
    $sth->execute;


    if ( $sth->rows == 0 )
    {
        print "<br>\n", "No QSOs in last 7 days\n", "<p>\n";
    }

    if ( $sth->rows > 0 )
    {
        print "<br><b>Last 7 days</b><br>\n",
          "<table border=\"0\">\n", "<tbody>\n",
          "<tr>",
          "<th>Country</th>",
          "<th>Callsign</th>",
          "<th>Band</th>",
          "<th>Mode</th>",
          "<th>QSO Date</th>",
          "</tr>\n";

        for ( my $i = 0 ; $i < $sth->rows ; $i++ )
        {
            my @det  = $sth->fetchrow_array;
            my $dxid = shift @det;

            ## Couple things here.. We like flags.
            ## So, based on the country code of the station
            ## worked, show the flag.
            $det[0] =
                "<img style=\"border: 1px solid grey;\" "
                . "src=\"${AYIML_HOME}/flags/${dxid}.png\"> $det[0]";

            ## Also, for a bit of spice, for each callsign last worked,
            ## emit a LINK to the same lookup to show the meta-data
            ## for working that station....
            $det[1] = "<a href=\"/cgi-bin/ayiml.cgi?cs=$det[1]\">$det[1]</a>";

            print "<tr><td valign=\"center\"> ",
              join( "</td><td align=\"center\">", @det ), "</td></tr>\n";
        }
        print "</tbody>\n", "</table>\n";
    }
}


## Utility functions..
sub NoCall
{
    print $q->header;
    print "No record<p>\n";
}
sub Quit
{
    $sth = undef;
    if ($dbh)
    {
        $dbh = undef;
    }
    exit;
}

## end of script.

