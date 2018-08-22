"""
Bill categories are also called subjects of bills
"""
import glob
import json
from utilities.db import DB
from utilities.configurator import Configurator
from utilities.bill_helper import BillHelper


class BillCategory:
    """class responsible for importing a bill category"""

    #notest
    @classmethod
    def all_bill_categories(cls):
        """
        Traverse every piece of legislation and produce a total
        `set` of categories

        :returns set of strings indicating all subjects considered in the US legislator
        """


        # NOTE: all bills are stored in a json format as data.json. Eventually,
        # it will move into some service or something that will provide this
        # information to avoid dependencies on any one filesystem

        # FIXME: this is going to break in the new congress (116)
        config = Configurator().config
        bills_root = config['congress_data_fs_root']
        datas = glob.glob(bills_root + "/115/bills/*/*/data.json")
        categories = []

        for bill_file in datas:
            with open(bill_file) as f:
                data = json.load(f)
                for category in data['subjects']:
                    categories.append(category.lower())

        return set(categories)

    # notest
    @classmethod
    def persist_all_bill_categories(cls):
        """Save all bill categories to the database

        NOTE: this saves every record as a separate transaction. The performance
        characteristics at this level of scale seem to be okay. YMMV
        """

        categories = cls.all_bill_categories()
        for category in categories:
            cls._db().execute("""
                INSERT INTO bill_categories (category_name)
                VALUES (%s)
                --- We may have inserted this category before
                ON CONFLICT (category_name) DO NOTHING
            """, (category,))


    #notest
    @classmethod
    def populate_bill_category_join_records(cls):
        """Updates join table for bills <=> bill_categories

        This is really inefficient. It was written in a way so that future us
        can figure out WTF I was trying to do. Again, the performance
        characteristics aren't that bad for our level of scale. We're not sure
        how we'll use this data so I think it's better to have a one-command
        way of populating this data reliably and then figure out how valuable
        this opp is.
        """

        all_bills = cls._db().fetch_records("""
            SELECT id, bill_id FROM bills
        """)

        for bill in all_bills:
            data_file_location = BillHelper.bill_fs_location(bill[1])
            with open(data_file_location, 'r') as f:
                bill_data = json.load(f)

                for category in bill_data['subjects']:
                    category_record = cls._db().fetch_one("""
                                                    SELECT id, category_name
                                                    FROM bill_categories
                                                    WHERE category_name = %s
                                                """, (category.lower(),))
                    cls._db().execute("""
                        INSERT INTO bill_categories_join
                        (bill_id, bill_category_id)
                        VALUES (%s, %s)
                        ON CONFLICT (bill_id, bill_category_id) DO NOTHING""",
                                      (bill[0], category_record[0]))


    @classmethod
    def _db(cls):
        return DB()


if __name__ == '__main__':
    BillCategory.persist_all_bill_categories()
    BillCategory.populate_bill_category_join_records()