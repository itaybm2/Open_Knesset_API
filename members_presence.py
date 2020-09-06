import conn
import json

con = conn.connect()
cur = con.cursor()

""" Returns dict with details
 of passed mk name at passed year including his yearly presence hours """

def mk_yearly_hours(mk_name, year):

    cur.execute("SELECT \"PersonID\",\"mk_id\",\"FirstName\",\"LastName\",\"GenderDesc\",\"Email\",year,sum FROM\
        (SELECT mk_id,mk_name,year,sum(total_attended_hours) as sum FROM members_presence WHERE mk_name LIKE ('%{}%')\
         AND year = {} GROUP BY mk_id,mk_name,year) as total_hours NATURAL JOIN members_kns_person\
         WHERE total_hours.mk_name LIKE ('%' || members_kns_person.\"FirstName\" || '%')".format(year, mk_name))

    # Create dictionary containing passed mk member attendance hours sorted by year
    presence_dict = {}
    row = cur.fetchone()

    if row is None:
        raise Exception("Knesset member name error - name not found")

    while row is not None:
        key = str(row[2] + " " + row[3])
        if presence_dict.get(key) is None:
            presence_dict[key] = []
        presence_dict[key].append({"PersonID": row[0], "mk_id:": row[1],
                                      "First_Name": row[2], "Last_Name": row[3],
                                      "Gender": row[4], "Email": row[5], "Year": row[6], "Hours": row[7]})
        row = cur.fetchone()

    return presence_dict
    # return json.dumps(presence_dict, ensure_ascii=False)


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
        max_presence_dict[row[0]].append({'month': row[1], 'hours': row[2]})
        row = cur.fetchone()

    return json.dumps(max_presence_dict, ensure_ascii=False)

res = mk_yearly_hours(2016,"נתניהו")
print(res["בנימין נתניהו"])