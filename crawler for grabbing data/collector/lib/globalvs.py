import os

# ------------------------------- Common Space ---------------------------------
# All temporary stuff dumped here
DUMP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "dumps/"))

# Curb the number of worker processes a user tries to create
LIMIT_WORKFORCE = 20

# Max number of elements to hold for the multiprocessing Queue
QUEUE_MAX_SIZE = 50

# Databases used to save information
DB_NAME = "wiki_editors"
PAGES_EDITS_TABLE = "pages_editors"
EDITORS_TABLE = "editors"

# ------------------------------ Wiki crawler ----------------------------------
# A dump of all titles present in en Wikipedia
TITLES_DUMP = "https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-all-titles-in-ns0.gz"

# HTML pages for wikis
URL_TEMPLATE = "https://en.wikipedia.org/w/index.php?title={t}&action=history&limit=500"
URL_BASE = "https://en.wikipedia.org{u}"

# All file paths for storing temporary information
ALL_TITLES = os.path.join(DUMP_PATH, "all_titles")
TITLES_MARK = os.path.join(DUMP_PATH, "crawled_till")
FAILED_TITLES = os.path.join(DUMP_PATH, "failed_crawling_titles")

#------------------------------- Editors Crawler -------------------------------
# Entries expire after these many days
EXPIRE_AFTER = 365 # 1 year

FAILED_CRAWLING_EDITORS = os.path.join(DUMP_PATH, "failed_crawling_editors")
