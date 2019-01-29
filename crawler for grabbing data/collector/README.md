# The Collector

Two independent Crawlers -
* **crawl_wikis.py :** Crawls the Wiki pages and builds a database of wiki pages and their editors list.
  ```
  crawl_wikis.py [-v] [-w num_workers] [-lf /log/path] [-f force_level]
  ```
  * v for verbose logs
  * w for number of worker parallel processes to use (max. 20)
  * lf for specifying the file to dump all logs
  * f to mention level of force in program to re-fetch certain information.
    * 0 : Start from scratch
    * 1 : Start from building the database of wiki pages and their editors list

* **crawl_editors.py :** Crawls the editor pages as found by *crawl_wikis* and builds editorial database.
  ```
  crawl_editors.py [-v] [-f] [-w num_workers] [-lf /log/path]
  ```
  * v for verbose logs
  * f for forcing a refresh of editors information
  * w for number of worker parallel processes to use (max. 20)
  * lf for specifying the file to dump all logs

---

**Before using -**
* Install mongodb (>= v3.0) in your system
* Install pip3 requirements
