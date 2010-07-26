import docs
import mail
from config import *

def backup_everything():
    mail.archive(username, password, data_dir + 'mail/')
    docs.archive(username, password, data_dir + 'docs/')
    contacts.archive(username, password, data_dir + 'contacts/')

if __name__ == "__main__":
    backup_everything()
