import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from ensap.connector import Connector

# Download all document in your ensap
def main():
    ensap = Connector()
    ensap.is_authenticate('<id>', '<password>')
    years = ensap.get_years()
    print(years)
    for year in years:
        files = ensap.fetch_files(str(year))
        docs = ensap.parse_documents(files)
        ensap.save_file(docs, '/Users/christophe/Desktop/ensap_test')
    ensap.logout()


if __name__ == "__main__":
    main()
