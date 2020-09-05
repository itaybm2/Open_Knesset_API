import conn
import json

con = conn.connect()
cur = con.cursor()

""" Returns JSON of passed mk name including his yearly presence hours """


def mk_yearly_hours(mk_name):

    cur.execute("SELECT mk_name,year,SUM(total_attended_hours) \
    FROM members_presence WHERE mk_name LIKE '%{}%' GROUP BY mk_name,year ORDER BY(mk_name,year)".format(mk_name))

    # Create dictionary containing passed mk member attendance hours sorted by year
    presence_dict = {}
    row = cur.fetchone()

    if row is None:
        raise Exception("Knesset member name error - name not found")

    while row is not None:
        if presence_dict.get(row[0]) is None:
            presence_dict[row[0]] = []
        presence_dict[row[0]].append({'year': row[1], 'hours': row[2]})
        row = cur.fetchone()

    return json.dumps(presence_dict, ensure_ascii=False)


""" Returns JSON format specifying details of most present mk member during given year/month"""

def mk_max_presence(year, month=None):

    if month is not None:
        cur.execute("WITH attendance_sum (mk_name,sum) AS\
            (SELECT mk_name, SUM(total_attended_hours) as sum\
            FROM members_presence WHERE (year='{}' AND month='{}') GROUP BY mk_name, year,month ORDER BY sum DESC)\
            SELECT * FROM attendance_sum LIMIT 1".format(year, month))
    else:
        cur.execute("SELECT mk_name,month,sum(total_attended_hours) as sum\
                    FROM (SELECT mk_name, SUM(total_attended_hours) as sum\
                    FROM members_presence WHERE year='{}' GROUP BY mk_name, year ORDER BY sum DESC LIMIT 1) AS max_attendant\
                    NATURAL JOIN (SELECT * FROM members_presence) as mem_presence\
                    GROUP BY mk_name,month,sum".format(year))

    max_presence_dict = {}
    row = cur.fetchone()
    while row is not None:
        if max_presence_dict.get(row[0]) is None:
            max_presence_dict[row[0]] = []
        max_presence_dict[row[0]].append({'month':row[1],'hours': row[2]})
        row = cur.fetchone()

    return json.dumps(max_presence_dict, ensure_ascii=False)
