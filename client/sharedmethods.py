from datetime import datetime

class SharedMethods():
    def rp(rs):
        return int(100*float(rs))

    def pr(p):
        return float(p)/100

    def m0915(h,m):
        return (h-9)*60+m-14

    def tm0915(m):
        tm = datetime.strptime('{:02d}:{:02d}'.format(*divmod(m+60*9+14, 60)),'%H:%M')
        now = datetime.now()
        tme = now.replace(hour=tm.hour, minute=tm.minute, second=0, microsecond=0)
        return tme