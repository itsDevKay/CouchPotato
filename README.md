# CouchPotato
CouchPotato was an online movie streaming platform that utilized a truly free streaming experience with a 95% Ad Free Experience.

## Performance Issues
CouchPotato was initally a very small project only capable of movies stored on an SQLite3 database file. Overtime, the database 
grew with the capability to handle TV Shows as well as movies. 

However, by still only utilizing an SQLite3 database instead of a MySQL database, there were some performance issues.

These performance issues were not only due to the database but as well to the jinja2 functions that were executed during the 
the website and movie/shows pages.

These issues can definitely be solved using AJAX and intersectionObserver, (more info on how to do that can be found here,
[Lazy Loading Ajax Flask & Python](https://pythonise.com/articles/infinite-lazy-loading)

I had to take down the site due to lack of time to maintain this. Unlike other movie streaming websites where they utilize a WordPress 
plugin and theme to get the job done, I decided to build one completely from scratch. In return, there was much more maintenance on 
my end needed than pressing 'update'.

Being as this was a completely free site that I didn't monetize in any way, (even my own donation buttons brought nothing my way)
There was never anything I could do to put aside the time and maintain this project.

****
Here are the average load times without the above fixes in accordance with Google Analytics: 
```
**Page**                **Avg. Page Load Time (sec)**  
------------------------------------------------------
/                                   21.68  
/entity/fifty-shades-freed          18.56  
/alphabet/f                         8.87  
/tv                                 11.42  
/alphabet/a                         2.62  
/alphabet/b                         0.0  
```
****  

## Where is the movie database file?
For copyright reasons, I will not post that here. However, if you read through the code, and pay attention to the notes you should easily found out how simple everything has been set in place to generate your own, If you have questions or issues, please open a ticket and I will get back to you as soon as I can.

## Screenshots
![homepage desktop](https://github.com/KeanuAaron/CouchPotato/blob/master/screenshots/homepage-desktop.png)

![homepage search](https://github.com/KeanuAaron/CouchPotato/blob/master/screenshots/search-desktop-fullscreen.png)

![mobile view](https://github.com/KeanuAaron/CouchPotato/blob/master/screenshots/homepage-mobile-notfullscreen.png)

![video page mobile](https://github.com/KeanuAaron/CouchPotato/blob/master/screenshots/Screen%20Shot%202020-05-21%20at%2018.30.38-fullpage.png)
