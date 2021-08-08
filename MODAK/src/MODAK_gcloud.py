import logging

import google.cloud.exceptions
from google.cloud import storage


class TransferData:
    def __init__(self, google_cred="../conf/modak-f305a35c96dc.json"):
        # Explicitly use service account credentials by specifying the private key
        # file.
        logging.info("Initialising gcloud storage")
        try:
            self.storage_client = storage.Client.from_service_account_json(google_cred)
            self.bucket = self.storage_client.get_bucket("modak-bucket")
        except google.cloud.exceptions as err:
            logging.error(str(err))
            raise RuntimeError(str(err))

    def upload_file(self, file_from=None, file_to=None):
        """Upload data to a bucket"""
        try:
            blob = self.bucket.blob(file_to)
            blob.upload_from_filename(file_from)
            logging.info("Added {} to storage : {}".format(file_from, blob.public_url))
            # returns a public url
            return blob.public_url
        except google.cloud.exceptions as err:
            logging.error(str(err))
            raise RuntimeError(str(err))


def main():
    transferData = TransferData()
    link = transferData.upload_file("scripts/enable_xla.sh", "test/enable_xla.sh")
    print(link)


if __name__ == "__main__":
    main()
