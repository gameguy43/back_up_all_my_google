from bin.gdatacopier.gcp import *

def archive(username, password, data_dir):
    source_path = '%s@gmail.com:/docs/all/*' % username
    class Options:
        def __init__(self):
            self.password = password
            self.silent = False
            self.update = False
            self.overwrite = False
            self.add_document_id = False
            self.create_user_dir = False
            #self.password_file  = ''
            #self.format = 'oo'
    options = Options()

    export_documents(source_path, data_dir, options)

if __name__ == "__main__":
    from config import *
    archive(username, password, data_dir + 'docs/')
