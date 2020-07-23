import dropbox
from datetime import datetime
import os
import time

class TransferData:
    def __init__(self, access_token=''):
        if access_token == '':
            self.access_token = access_token = 'uIdLbZ5c1OAAAAAAAAAAbyk8y7dUYKwD4BlLXa7m7lOosadXk1GAZPyr760SCrr-'
        self.access_token = access_token
        self.dbx = dropbox.Dropbox(self.access_token)

    def download(self, folder, name):
        """Download a file.
        Return the bytes of the file, or None if it doesn't exist.
        """
        path = '/%s/%s' % (folder,  name)
        while '//' in path:
            path = path.replace('//', '/')
        try:
            md, res = self.dbx.files_download(path)
        except dropbox.exceptions.HttpError as err:
            print('*** HTTP error', err)
            return None
        data = res.content
        print(len(data), 'bytes; md:', md)
        return data

    def upload(self, fullname, folder,  name, overwrite=False):
        """Upload a file.
        Return the request response, or None in case of error.
        """
        path = '/%s/%s' % (folder, name)
        while '//' in path:
            path = path.replace('//', '/')
        mode = (dropbox.files.WriteMode.overwrite
                if overwrite
                else dropbox.files.WriteMode.add)
        mtime = os.path.getmtime(fullname)
        with open(fullname, 'rb') as f:
            data = f.read()

        try:
            res = self.dbx.files_upload(
            data, path, mode,
            client_modified=datetime(*time.gmtime(mtime)[:6]),
                 mute=True)
        except dropbox.exceptions.ApiError as err:
            print('*** API error', err)
            return None
        print('uploaded as', res.name.encode('utf8'))
        return res

    def upload_file(self, file_from=None, file_to=None):
        """upload a file to Dropbox using API v2
        """

        # files_upload(f, path, mode=WriteMode('add', None), autorename=False, client_modified=None, mute=False)

        with open(file_from, 'rb') as f:
            self.dbx.files_upload(f.read(), file_to)

            # link_settings = dropbox.sharing.SharedLinkSettings(
            #     requested_visibility=dropbox.sharing.RequestedVisibility.password,
            #     link_password='modak',
            #     expires=datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            # )
            # link = dbx.sharing_create_shared_link_with_settings(file_to, link_settings)
            try:
                link = self.dbx.sharing_create_shared_link(file_to)
            except dropbox.exceptions.ApiError as err:
                print('*** API error', err)
                return None
            url = link.url.split('?dl=')
            # url which can be shared
            return url[0]


def main():
    transferData = TransferData()

    file_from = 'scripts/enable_xla.sh'
    file_to = '/scripts/enable_xla.sh' # The full path to upload the file to, including the file name
    link = transferData.upload_file(file_from, file_to)
    print(link)

    # API v2
    # link = transferData.upload_file(file_from=file_from, file_to=file_to)
    # print(link)
    # link = transferData.upload(file_from , 'test','torque_{}.pbs'.format(datetime.now().strftime('%Y%m%d%H%M%S')))
    # print(link)
    #
    # print(transferData.download('test', 'torque_20200720123826.pbs'))



if __name__ == '__main__':
    main()
