import sys
import os

from ensap.connector import Connector

# Download all document in your ensap
def full_download():

    # Set login / password
    my_id = '<id>'
    my_password = '<password>'

    ensap = Connector()
    ensap.is_authenticate(my_id, my_password)

    years = ensap.get_years()

    for year in years:
        files = ensap.fetch_files(str(year))
        docs = ensap.parse_documents(files)
        ensap.save_file(docs, '/Users/John_Doe/Desktop/ensap_test')
    ensap.logout()


if __name__ == "__main__":
    full_download()
