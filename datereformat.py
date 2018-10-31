def datereformat(date):
    split_date = date.split('/')
    reformatted_date = split_date[2] + '-' + split_date[1] + '-' + split_date[0]
    return reformatted_date
