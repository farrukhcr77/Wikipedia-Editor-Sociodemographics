REMOVE_CHARS_LIST = ["\xa0", # &nbsp;
		             "\u200e", # &lrm;
		             "\u200f", # &rlm;
		            ]
ANY_BRACKETS = {"{" : "}", "[" : "]", "(" : ")"}
IGNORE_IN_BRACKET = ["edit", "talk", "verify", "", "direct link", "disambiguation"]


def clean_editor_content(data):
    clean_data = ""
    data_len = len(data)
    index = 0
    while index < data_len:
        c = data[index]
        # Don't require these characters.
        if c in REMOVE_CHARS_LIST:
            c = " "
        elif c in ANY_BRACKETS.keys():
            ending_br_indx = data.find(ANY_BRACKETS[c], index + 1)
            if ending_br_indx != -1:
                enclosed_in_bracket = data[index + 1 : ending_br_indx].strip().lower()
                if any([enclosed_in_bracket in IGNORE_IN_BRACKET,
                        enclosed_in_bracket.isdigit()]):
                    # Ignore certain keywords
                    # Ignore all the numbers, they are just citings
                    c = ""
                    index = ending_br_indx

        clean_data += c
        index += 1
    return clean_data
