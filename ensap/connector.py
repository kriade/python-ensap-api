# coding: utf-8

# Standard library
from typing import Dict, List
import os

# Additionnal library
from requests import Session
import dateparser


# Constant
URL = {
    'LOGIN'         :   'https://ensap.gouv.fr/authentification',
    'LOGOUT'        :   'https://ensap.gouv.fr/prive/deconnexion/v1',
    'HOME'          :   'https://ensap.gouv.fr/prive/accueilconnecte/v1',
    'REMUNERATION'  :   'https://ensap.gouv.fr/prive/remunerationpaie/v1?annee=',
    'DOWNLOAD'      :   'https://ensap.gouv.fr/prive/telechargerremunerationpaie/v1?documentUuid=',
    'HABILITATION'  :   'https://ensap.gouv.fr/prive/initialiserhabilitation/v1'
}

CODE_AUTH = {
    60  :   'Login successful',                    # Login/password ok
    61  :   'Connexion error',                     # Login and/or password incorrect
    68  :   'Authentification required'            # No login and password
}


class Connector:

    def __init__(self):
        self.s = Session()
        self.s.keep_alive = False

    def __formatLogin(self, user: str, password: str) -> Dict:
        """Return login and password in dictionnary data

        Args:
            user (str): NIR number (no_secu)
            password (str): associated password

        Returns:
            Dict: formated data
        """
        data_dict = dict([
            ('identifiant', user),
            ('secret', password)
        ])
        return data_dict

    def is_authenticate(self, user: str, password: str) -> bool:
        """Is log in to ensap.gouv.fr

        Args:
            user (str): NIR number (no_secu)
            password (str): associated password

        Returns:
            bool: authenticate or not
        """
        login = self.__formatLogin(user, password)

        response = self.s.post(URL['LOGIN'], data=login)
        response_code = response.json()['code']

        for key, value in CODE_AUTH.items():
            if key == response_code:
                return True
            else:
                return False

    def logout(self) -> None:
        """Log out to ensap.gouv.fr
        """
        self.s.get(URL['LOGOUT'])
        self.s.close()
        print("Connexion close")

    def get_years(self) -> List:
        """Get all remunation year available in account

        Returns:
            List: Array of string with year available
        """
        req = self.s.get(URL['HOME'])
        return sorted(req.json()['listeAnneeRemuneration'])

    def fetch_files(self, year: str) -> List:
        """Gets the information about the remuneration for the given year

        Args:
            year (str) : Given year

        Returns:
            List: data json of get request
        """
        liste_year = self.s.get(URL['REMUNERATION'] + year)
        # print(liste_year.json())
        return liste_year.json()

    def parse_documents(self, files: List) -> List:
        """Gets the document parsed informations and format in list

        Args:
            files (List): Raw information of document
        Returns:
            List: Formated informations
        """

        docs = []
        for file in files:
            doc = {}

            uuid = file['documentUuid']

            fileurl = URL['DOWNLOAD'] + uuid

            # Format name file
            filename = file['nomDocument'].replace('_AF_', '_Attestation_fiscale_')
            filename = filename.replace('_BP_', '_Bulletin_de_paie_')
            filename = filename.replace('_DR_', '_Décompte_de_rappel_')

            doc['download_url'] = fileurl
            doc['filename'] = filename
            doc['year'] = file['annee']

            # Create tag key
            if not file['libelle3']:
                doc['tag'] = 'AF'
                doc['month'] = ''
            else:
                doc['tag'] = 'BP'
                month = file['libelle1'].split()[0].upper()
                datetime_object = dateparser.parse(month)
                doc['month'] = datetime_object.month

            docs.append(doc)
        return docs

    def save_file(self, docs: List, dest_folder: str) -> None:
        """Save file in specific directory

        Args:
            docs (List): Array of documents to save
            dest_folder (str): Path to directory
        """
        for doc in docs:
            # get document information
            download_url = doc['download_url']
            filename = doc['filename']
            year = str(doc['year'])
            month = str(doc['month'])
            tag = doc['tag']

            dir_path = os.path.join(dest_folder, year, month, tag)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)  # create folder if it does not exist

            file_path = os.path.join(dir_path, filename)

            req = self.s.get(download_url, stream=True)
            if req.ok:
                print("saving to", os.path.abspath(file_path))
                # save file
                with open(file_path, 'wb') as f:
                    for chunk in req.iter_content(chunk_size=1024 * 8):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                            os.fsync(f.fileno())
            else:  # HTTP status code 4XX/5XX
                print("Download failed: status code {}\n{}".format(req.status_code, req.text))

    def filter_by_month(self, docs: List, month: int) -> Dict:
        """Get list of document filter by specific month

        Args:
            docs (List): List of information document
            month (str): dat

        Returns:
            Dict: [description]
        """
        res = []
        for doc in docs:
            if doc['month'] == month :
                res.append(doc)
        return res
