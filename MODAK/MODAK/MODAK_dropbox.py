import os
import time
from datetime import datetime

import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect

from .settings import Settings


class TransferData:
    def __init__(self):
        self.access_token = Settings.dropbox_access_token
        self.dbx = dropbox.Dropbox(self.access_token)

    def login_dropbox(self):
        """
        Authorize dropbox using Oauth2
        Follow instructions and authorise your dropbox account to app.
        """
        APP_KEY = "0ntzsx9e42ezvjp"
        APP_SECRET = "k9erv6t8zcx7jto"

        auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

        authorize_url = auth_flow.start()
        print("1. Go to: " + authorize_url)
        print('2. Click "Allow" (you might have to log in first).')
        print("3. Copy the authorization code.")
        auth_code = input("Enter the authorization code here: ").strip()
        try:
            oauth_result = auth_flow.finish(auth_code)
        except Exception as e:
            print(f"Error: {e}")
        return oauth_result

    def download(self, folder, name):
        """Download a file.
        Return the bytes of the file, or None if it doesn't exist.
        """
        path = f"/{folder}/{name}"
        while "//" in path:
            path = path.replace("//", "/")
        try:
            md, res = self.dbx.files_download(path)
        except dropbox.exceptions.HttpError as err:
            print("*** HTTP error", err)
            return None
        data = res.content
        print(len(data), "bytes; md:", md)
        return data

    def upload(self, fullname, folder, name, overwrite=False):
        """Upload a file.
        Return the request response, or None in case of error.
        """
        path = f"/{folder}/{name}"
        while "//" in path:
            path = path.replace("//", "/")
        mode = (
            dropbox.files.WriteMode.overwrite
            if overwrite
            else dropbox.files.WriteMode.add
        )
        mtime = os.path.getmtime(fullname)
        with open(fullname, "rb") as f:
            data = f.read()

        try:
            res = self.dbx.files_upload(
                data,
                path,
                mode,
                client_modified=datetime(*time.gmtime(mtime)[:6]),
                mute=True,
            )
        except dropbox.exceptions.ApiError as err:
            print("*** API error", err)
            return None
        print("uploaded as", res.name.encode("utf8"))
        return res

    def upload_file(self, file_from=None, file_to=None):
        """upload a file to Dropbox using API v2"""

        # files_upload(f, path, mode=WriteMode('add', None),
        #              autorename=False, client_modified=None, mute=False)

        with open(file_from, "rb") as f:
            self.dbx.files_upload(f.read(), file_to)

            try:
                link = self.dbx.sharing_create_shared_link(file_to)
            except dropbox.exceptions.ApiError as err:
                print("*** API error", err)
                return None
            url = link.url.split("?dl=")
            # url which can be shared
            return url[0]


def main():
    transferData = TransferData()
    # transferData.login_dropbox()

    file_from = "scripts/set_default_cirrus.sh"
    # The full path to upload the file to, including the file name:
    file_to = "/scripts/set_default_cirrus.sh"
    link = transferData.upload_file(file_from, file_to)
    print(link)

    # API v2
    # link = transferData.upload_file(file_from=file_from, file_to=file_to)
    # print(link)
    # link = transferData.upload(
    #     file_from , 'test',
    #     'torque_{}.pbs'.format(datetime.now().strftime('%Y%m%d%H%M%S')))
    # print(link)
    #
    # print(transferData.download('test', 'torque_20200720123826.pbs'))


if __name__ == "__main__":
    main()
