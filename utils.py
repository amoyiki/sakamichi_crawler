import os
import datetime

def get_for_file(file):
    pool = []
    with open(file, 'r') as f:
        for line in f:
            pool.append(line)
    return pool

sankisei = {
    u"伊藤理々杏": u"伊藤理々杏",
    u"伊藤 理々杏": u"伊藤理々杏",
    u"岩本蓮加": u"岩本蓮加",
    u"岩本 蓮加": u"岩本蓮加",
    u"梅澤美波": u"梅澤美波",
    u"梅澤 美波": u"梅澤美波",
    u"大園桃子": u"大園桃子",
    u"大園 桃子": u"大園桃子",
    u"久保史緒里": u"久保史緒里",
    u"久保 史緒里": u"久保史緒里",
    u"阪口珠美": u"阪口珠美",
    u"阪口 珠美": u"阪口珠美",
    u"佐藤楓": u"佐藤楓",
    u"佐藤 楓": u"佐藤楓",
    u"中村麗乃": u"中村麗乃",
    u"中村 麗乃": u"中村麗乃",
    u"向井葉月": u"向井葉月",
    u"向井 葉月": u"向井葉月",
    u"山下美月": u"山下美月",
    u"山下 美月": u"山下美月",
    u"吉田綾乃クリスティー": u"吉田綾乃クリスティー",
    u"吉田綾乃 クリスティー": u"吉田綾乃クリスティー",
    u"吉田 綾乃 クリスティー": u"吉田綾乃クリスティー",
    u"与田祐希": u"与田祐希",
    u"与田 祐希": u"与田祐希"
}


def datetime_offset_by_month(datetime1, n=1):
    # create a shortcut object for one day
    one_day = datetime.timedelta(days=1)

    # first use div and mod to determine year cycle
    q, r = divmod(datetime1.month + n, 12)

    # create a datetime2
    # to be the last day of the target month
    datetime2 = datetime.datetime(
        datetime1.year + q, r + 1, 1) - one_day

    '''
       if input date is the last day of this month
       then the output date should also be the last
       day of the target month, although the day
       www.iplaypy.com
       may be different.
       for example:
       datetime1 = 8.31
       datetime2 = 9.30
    '''

    if datetime1.month != (datetime1 + one_day).month:
        return datetime2

    '''
        if datetime1 day is bigger than last day of
        target month, then, use datetime2
        for example:
        datetime1 = 10.31
        datetime2 = 11.30
    '''

    if datetime1.day >= datetime2.day:
        return datetime2

    '''
     then, here, we just replace datetime2's day
     with the same of datetime1, that's ok.
    '''

    return datetime2.replace(day=datetime1.day)