import csv

with open("original_tracks_features.csv","rt", encoding="utf8") as source:
    rdr= csv.reader(source)
    with open("tracks_features.csv","wt") as result:
        wtr= csv.writer(result)
        for r in rdr:
            wtr.writerow( (r[0], r[1], r[2], r[3], r[4], r[5], r[8], r[16], r[17], r[26], r[27], r[28], r[29], r[30], r[31], r[32], r[33], r[34], r[35], r[36], r[54]) )
