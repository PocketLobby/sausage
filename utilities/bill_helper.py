"""Some utility functions to help with sorting and general formatting"""

import re
import configparser
from bs4 import BeautifulSoup

class BillHelper():

    @classmethod
    def _bill_matcher(cls, bill_name):
        "find the prefix for the bill and return a pretty printed version"
        return re.search(r"(hconres|sconres|hjres|sjres|hres|sres|hr|s)(\d{1,})", bill_name)

    @classmethod
    def bill_fs_location(cls, bill_name):
        """
        Find the location on the filesystem where details about the bill can
        be extracted

        TODO: in the future, I imagine this will be incorporated between some
        sort of messaging system
        """

        # TODO: move this out into a proper environment class
        config = configparser.ConfigParser()
        config.read('../sausage_config.conf')
        config = config['test']

        bill_matcher = cls._bill_matcher(bill_name)

        bill_location = ""
        bill_location += config['congress_data_fs_root']
        bill_location += "115/bills/"
        bill_location += bill_matcher[1] + "/" + bill_matcher[0]
        bill_location += "/data.json"

        return bill_location

    @classmethod
    def linkify_bill(cls, bill_name):
        """Takes in a bill like hr123 and converts it to an external link to the
        full text of the bill. WARNING - this is hard coded for the 115 congress"""

        bill_matcher = cls._bill_matcher(bill_name)

        bill_prefix_mapper = {
                "hr" : "house-bill/",
                "s"  : "senate-bill/",
                "hjres" : "house-joint-resolution/"

                }

        base_url = "https://www.congress.gov/bill/115th-congress/"
        base_url += bill_prefix_mapper[bill_matcher[1]]
        base_url += bill_matcher[2]
        base_url += "/text"
        return base_url

    @classmethod
    def convert_bill_name(cls, bill_name):
        """Converts billnames like hr123-115 into their proper display: H.R. 123"""

        bill_type_splitter = {
            "hr" : "H.R. ",
            "s"  : "S. ",
            "hjres" : "H. J. Res. ",
        }

        bill_matcher = cls._bill_matcher(bill_name)
        new_bill_name = re.sub(bill_matcher[1],
                bill_type_splitter[bill_matcher[1]],
                bill_name)

        new_bill_name = re.sub("-115", "", new_bill_name)

        return new_bill_name

    @classmethod
    def sort_vote_match_columns(cls, df_columns):
        """Sorts Vote Tally Table according to our business rules

        Our business rules are Rep, Sen, Sen. Luckily, that's alphabetical
        order. If that changes, this is the place to change that.
        """
        return df_columns

    @classmethod
    def convert_html_table_to_email_style(cls, table_html):
        """Convert a pandas created HTML table and format it for email"""

        table_mod = BeautifulSoup(table_html, 'html.parser')
        table_mod.table['border'] = 2
        table_mod.table['cellpadding'] = "10px"
        table_mod.table['cellspacing'] = "2px"
        table_mod.table['width'] = "100%"
        table_mod.table.tr['style'] = "text-align: center;"
        table_mod.table.tbody['align'] = "center"

        # NOTE: this is very brittle right now. Be careful if the words we
        # use to describe a match, no match etc change
        for tag in table_mod.find_all("td"):
            if "Match" in tag:
                tag['style'] = "color: #014f25;"
            if "No vote" in tag:
                tag['style'] = "color: #BCBCBC;"
            if "No match" in tag:
                tag['style'] = "color: #7a0808;"

        return table_mod
