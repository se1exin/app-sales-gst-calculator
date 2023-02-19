import json
import sys
import os
import csv
import zipfile
from google.cloud import storage

def download_from_google(date):
    f = open('config/config.json')
    data = json.load(f)

    bucket_name = data["bucket_name"]
    client = storage.Client.from_service_account_json(
        os.path.join('config', data['google_key'])
    )
    blobs = client.list_blobs(bucket_name, prefix="earnings/earnings_" + date)
    for blob in blobs:
        filename = blob.name.replace("earnings/", "")        
        blob.download_to_filename(filename)

        with zipfile.ZipFile(filename, "r") as zip_ref:
            zip_ref.extractall()

        os.unlink(filename)
        return "PlayApps_" + date + ".csv"

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Please supply date in format of YYYYDD")
        exit()

    date = sys.argv[1]

    filename = download_from_google(date)

    total_sales = 0.0
    au_sales = 0.0
    international_sales = 0.0
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in list(reader)[1:]:
            country = row[12]
            amount = float(row[19])
            
            total_sales += amount
            if country == 'AU':
                 au_sales += amount
            else:
                international_sales += amount
    gst = au_sales / 11

    print("Total Sales: ${0:.2f}".format(total_sales))
    print("International Sales: ${0:.2f}".format(international_sales))
    print("AU Sales: ${0:.2f}".format(au_sales))
    print("AU GST: ${0:.2f}".format(gst))
    os.unlink(filename)
    