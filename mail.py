from bin.imapbackup.imapbackup import * 

def archive(username, password, data_dir):
    config = {
        'compress':'gzip',
        'overwrite':False,
        'usessl':True,
        'server':'imap.gmail.com',
        'user':'%s@gmail.com' % username,
        'pass': password,
        'port': 993,
        }

    """Main entry point"""
    try:
        server = connect_and_login(config)
        names = get_names(server, config['compress'])
        names.reverse()
        #for n in range(len(names)):
        #  print n, names[n]

        for name_pair in names:
            try:
                foldername, filename = name_pair
                filename = data_dir + filename
                fol_messages = scan_folder(server, foldername)
                fil_messages = scan_file(filename, config['compress'], config['overwrite'])
                new_messages = {}
                for msg_id in fol_messages:
                    if msg_id not in fil_messages:
                        new_messages[msg_id] = fol_messages[msg_id]

                #for f in new_messages:
                #  print "%s : %s" % (f, new_messages[f])

                download_messages(server, filename, new_messages, config)

            except SkipFolderException, e:
                print e

        print "Disconnecting"
        server.logout()
    except socket.error, e:
        (err, desc) = e
        print "ERROR: %s %s" % (err, desc)
        sys.exit(4)
    except imaplib.IMAP4.error, e:
        print "ERROR:", e
        sys.exit(5)

if __name__ == "__main__":
    from config import *
    archive(username, password, data_dir + 'mail/')
