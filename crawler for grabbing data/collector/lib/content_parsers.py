import logging
from bson import objectid
from datetime import datetime
from html.parser import HTMLParser

from lib.globalvs import EDITORS_TABLE, PAGES_EDITS_TABLE, URL_BASE


class EditorInfoParser(HTMLParser):
    def __init__(self, log_handler=None):
        self.logger = logging.getLogger(__name__)
        if log_handler:
            self.logger.addHandler(log_handler)
        self.raw_data = ""
        self.start_saving = False
        self.temp_pause_saving = False
        self.has_userbox_page = False
        self.html_elems_stack = []
        self.in_mid_sentence = False
        super(EditorInfoParser, self).__init__()

    def handle_starttag(self, tag, attrs):
        self.html_elems_stack.append(tag)
        if tag == "div":
            for (atr_type, atr_value) in attrs:
                if atr_type == "id" and atr_value == "mw-content-text":
                    self.start_saving = True
                elif atr_type == "class" and atr_value == "printfooter":
                    self.start_saving = False
                elif atr_type == "id" and atr_value == "catlinks":
                    self.start_saving = True
                elif atr_type == "id" and atr_value == "mw-navigation":
                    self.start_saving = False
        elif tag == "a":
            for (atr_type, atr_value) in attrs:
                if atr_type == "href" and atr_value == "Userboxes":
                    self.has_userbox_page = True
        elif tag == "style":
            # Ignore all style tags
            self.temp_pause_saving = True

    def handle_endtag(self, tag):
        if self.html_elems_stack:
            if tag.lower() == self.html_elems_stack[-1].lower():
                self.html_elems_stack.pop()
            if not self.html_elems_stack and self.in_mid_sentence:
                if self.raw_data and self.raw_data[-1].rstrip() != ".":
                    # Ending the sentence where possible fullstop is missing
                    self.raw_data += ". "
                    self.in_mid_sentence = False
        if tag == "style":
            self.temp_pause_saving = False

    def handle_data(self, data):
        if self.start_saving and not self.temp_pause_saving:
            data = data.strip()
            if data:
                self.raw_data += "{} ".format(data)
                if not self.in_mid_sentence:
                    self.html_elems_stack = self.html_elems_stack[-1:]
                    self.in_mid_sentence = True
                if data[-1] == ".":
                    # Sentence is possibly ending
                    self.in_mid_sentence = False

    def get_data(self):
        return self.raw_data

    def reset(self):
        self.raw_data = ""
        self.html_elems_stack = []
        self.in_mid_sentence = False
        self.start_saving = False
        self.has_userbox_page = False
        super(EditorInfoParser, self).reset()


class WikiRevisionHistoryParser(HTMLParser):
    def __init__(self, db_api, log_handler=None):
        self.db_api = db_api
        self.page_title = None
        self.editors_list = {}
        self.logger = logging.getLogger(__name__)
        if log_handler:
            self.logger.addHandler(log_handler)
        super(WikiRevisionHistoryParser, self).__init__()

    def push_to_db(self):
        editors_list = list(self.editors_list.items())
        save_editors_oids = []
        self.editors_list = {}
        old_editors, new_editors = 0, 0
        for editor_name, editor_link in editors_list:
            editor_full_link = URL_BASE.format(u=editor_link)
            res = self.db_api.find(table_name=EDITORS_TABLE,
                                   query={"id" : editor_name},
                                   return_cols=["_id"])
            if not res:
                oid = objectid.ObjectId()
                self.db_api.insert(table_name=EDITORS_TABLE,
                                   data={"_id" : oid, "id" : editor_name,
                                         "link" : editor_full_link,
                                         "last_updated" : datetime.fromtimestamp(0)})
                save_editors_oids.append(oid)
                new_editors += 1
            else:
                for r in res:
                    save_editors_oids.append(r["_id"])
                    old_editors += 1
        self.db_api.insert(table_name=PAGES_EDITS_TABLE,
                           data={"page_title" : self.page_title,
                                 "editors_list" : save_editors_oids})
        self.logger.info("Pushed {} old and {} new editor details against title {} ... ".
                    format(old_editors, new_editors, self.page_title))

    def set_title(self, title):
        self.page_title = title

    def handle_starttag(self, tag, attrs):
        if (tag == "a"):
            save_title = None
            save_link = None
            is_user = False
            for (item_type, item_value) in attrs:
                if item_type == "title":
                    save_title = item_value
                elif item_type == "href":
                    save_link = item_value
                if item_type == "class" and item_value == "mw-userlink":
                    is_user = True
            if is_user:
                self.editors_list[save_title] = save_link

    def reset(self):
        self.page_title = None
        self.editors_list = {}
        super(WikiRevisionHistoryParser, self).reset()
