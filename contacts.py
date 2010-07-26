import atom
import gdata.contacts
import gdata.contacts.service
import gdata.contacts.client
from bin.googlesharedcontactsclient.sharedcontactsprofiles import *

import pickle

arbitrarily_large_max_results = 100000

def OpenOutputCsv(file_name, option_name, description):
    if file_name:
        try:
            csv_file = open(file_name, 'wb')
            return csv_file
        except IOError, e:
            parser.error('Unable to open %s\n%s\nPlease set the --%s command-line'
                ' option to a writable file.' % (file_name, option_name, e))
    else:
        return None

def archive(username, password, data_dir):
    gd_client = gdata.contacts.service.ContactsService()
    gd_client.ClientLogin(username, password)
    query = gdata.contacts.service.ContactsQuery()
    # set an arbitrarily large max_results
    query.max_results = arbitrarily_large_max_results
    feed = gd_client.GetContactsFeed(query.ToUri())

    data_file = data_dir + '/google_contacts_feed.pickle'
    # for now, let's just pickle the feed, which almost certainly contains all of the information.
    file = open(data_file, 'w')
    pickle.dump(feed, file)


    
    # I was tryin to make this work with the googlesharedcontacts library thing, but it was getting complicated.
    #export_csv_file_name = data_dir + 'contacts.csv'
    #export_csv_file = OpenOutputCsv(export_csv_file_name, 'export', 'Export')
    #contacts_manager = ContactsManager(gd_client)
    #contacts_manager.ExportMsOutlookCsv(feed.entry, export_csv_file)



'''
    contacts_client = gdata.contacts.service.ContactsService(
        email = username + "@gmail.com",
        password = password,
    )
    contacts_client.ProgrammaticLogin()
#    contacts_manager = ContactsManager(contacts_client, '')


    contacts_manager = ContactsManager(gd_client, '')

    export_csv_file_name = data_dir + 'contacts.csv'

    export_csv_file = OpenOutputCsv(export_csv_file_name, 'export', 'Export')
    contact_entries = contacts_manager.GetAllContacts()
    profile_entries = contacts_manager.GetAllProfiles()
    contacts_manager.ExportMsOutlookCsv(contact_entries, profile_entries, export_csv_file)
    export_csv_file.close()
'''



if __name__ == "__main__":
    from config import *
    archive(username, password, data_dir + 'contacts/')


