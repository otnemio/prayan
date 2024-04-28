import os, requests, csv, sqlite3, zipfile
from io import BytesIO
from datetime import date, timedelta, datetime
def initialize():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

def download(single_date):
        conn = sqlite3.connect('bhav_eq_database.db',check_same_thread=False)
        c = conn.cursor()
        c.execute('''SELECT count(*) FROM sqlite_master WHERE type='table' AND name='bhav';
                    ''')
        if c.fetchone()[0]==1:
            c.execute('SELECT COUNT(*) FROM bhav WHERE day=? AND month=? AND year=?',
                      (single_date.day,single_date.month,single_date.year))
            if c.fetchone()[0]>0:
                print(f"Bhav data is already available for {single_date.strftime('%Y-%m-%d')}. No need to download.")    
                return
        else:
            c.execute('''CREATE TABLE bhav (
            symbol TEXT,
            openp INTEGER,
            highp INTEGER,
            lowp INTEGER,
            closep INTEGER,
            day INTEGER,
            month INTEGER,
            year INTEGER,
            tradeqty INTEGER,
            PRIMARY KEY (symbol,year,month,day)
        )''')
        month = date(single_date.year,single_date.month,single_date.day).strftime("%b").upper()
        date_file = date(single_date.year,single_date.month,single_date.day).strftime("%d%b%Y").upper()
        file_name = f'cm{date_file}bhav.csv'
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f'https://nsearchives.nseindia.com/content/historical/EQUITIES/{single_date.year}/{month}/{file_name}.zip'

        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            print(f"Bhav data downloaded from web for {single_date.strftime('%Y-%m-%d')}")
        elif r.status_code == 404:
            print(f"Bhav data not available for {single_date.strftime('%Y-%m-%d')}")
            return

        zf = zipfile.ZipFile(BytesIO(r.content))
        
        zf.extractall('.')

        # Open the CSV file
        with open(file_name, 'r') as f:
            reader = csv.reader(f)
            csv_heading=next(reader)
            assert (csv_heading[0],csv_heading[1],csv_heading[2],csv_heading[3],
                    csv_heading[4],csv_heading[5],csv_heading[8],csv_heading[10],
                    ) == ('SYMBOL', 'SERIES', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'TOTTRDQTY', 'TIMESTAMP')
            # Iterate over the rows in the CSV file
            for row in reader:
                # Insert the data into the database
                date_row = datetime.strptime(row[10],'%d-%b-%Y')
                if row[1]=='EQ':
                    c.execute('''INSERT OR IGNORE INTO bhav (symbol, openp, highp, lowp, closep, tradeqty, day, month, year) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (row[0], int(100*float(row[2])),int(100*float(row[3])),int(100*float(row[4])),int(100*float(row[5])),
                           int(row[8]),date_row.day,date_row.month,date_row.year))
        os.remove(file_name)
        # Commit the changes
        conn.commit()
        print("Data successfully updated.")

def download_data():
    today = datetime.today()
    start_date = date(2024, 3, 1)
    end_date = date(today.year, today.month, today.day)
    for single_date in daterange(start_date, end_date):
        download(single_date)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

#check if data not already available only then download
if __name__ == '__main__':
    initialize()
    download_data()