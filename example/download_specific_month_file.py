import sys
import os
from datetime import datetime

from ensap.connector import Connector

# Download all document in your ensap for the last month
def download_lm():

    # Set login / password
    my_id = '<id>'
    my_password = '<password>'

    # Set date parameter
    current_date = datetime.now()
    current_year = current_date.year
    last_month = current_date.month - 1 if current_date.month > 1 else 12
    ensap = Connector()
    ensap.is_authenticate(my_id, my_password)

    years = ensap.get_years()

    if current_year in years :
        files = ensap.fetch_files(str(current_year))
        docs = ensap.parse_documents(files)
        doc_filter = ensap.filter_by_month(docs, last_month)
        ensap.save_file(doc_filter, '/Users/John_Doe/Desktop/ensap_test')
        ensap.logout()


if __name__ == "__main__":
    download_lm()
