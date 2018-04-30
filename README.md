Usage:

    -Run django server
    -Populate database by calling web_scraper:
        -Send a POST request to /api/scraper/ with the fields 'username' and 'password', these being the acct. credentials for AISIS
    -Create Schedule db entry
        -Send a POST request to /api/sched/ with the fields 'name' and 'sections' with them being an arbitrary name and a list including atleast one entry respectively
            -Quickstart sample:

            {
                "name": "MySchedule",
                "sections":[
                    1
                ]
            }

    -Access front-end at /site/