# DAT-o-MATIC Crawl Scripts

This is a set of scripts to extract information from no-intro's DAT-o-MATIC (DoM).

There is a barebones shell script that curl's specified entries from DoM for a given system
and stores the HTML files into a sub-directory.

My main focus was to extract Game Boy PCB serials as there is currently no easy way to extract that info.

The HTML files are parsed and processed into a CSV file using python and beautifulsoup4.
I then extend the parsed data with serial number information from the web in order to match them to release
lists and find releases missing in DoM.
