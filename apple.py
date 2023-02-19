from appstoreconnect import Api, UserRole
import json
import os
import csv
import sys
from io import StringIO

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Please supply date in format of YYYY-DD")
        exit()

    report_date = sys.argv[1]
    # Correct date to apple fiscal date
    parts = report_date.split("-")
    year = int(parts[0])
    month = int(parts[1])

    # Apple is 3 months behind
    new_month = month + 3
    if new_month > 12:
        new_month = new_month - 12
        year = year + 1
    
    report_date = "{}-{:02d}".format(year, new_month)
    print("Using Apple Fiscal Month;", report_date)

    f = open('config/config.json')
    data = json.load(f)

    try:
        filters = {'vendorNumber': data['vendor_number'], 'reportDate': report_date}
        api = Api(data['key_id'], os.path.join('config', data['apple_key']), data['issuer_id'], submit_stats=False)
        result, _ = api.download_finance_reports(filters=filters, split_response=True)
        
        csvfile = StringIO(result)
        reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        au_sales = 0.0
        for row in list(reader)[1:]:
            country = row[17]
            amount = float(row[7])
            if country == "AU":
                au_sales += amount
        gst = au_sales * 0.1

        # Truncate to 2 decimal places to avoid rounding errors
        gst = int(gst * 100) / 100
        print(" ")
        print("AU Sales: ${0:.2f}".format(au_sales + gst))
        print("AU GST: ${0:.2f}".format(gst))
    except Exception as e:
        print(e)