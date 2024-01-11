from userinterface.templatetags.numbers import parseHumanizedTime, humanizeTime
import re

def calculateTime(issue, text):
    regex_pattern = r'\[(?P<kind>spend|spent|estimate|estimated) (?P<mode>add|subtract|set) (?P<duration>\d+[wdhmsWDHMS]*(?:\s*\d+[wdhmsWDHMS]*)*)\]'
    matches = re.finditer(regex_pattern, text.replace('\\',''))
    
    time_stats_time_estimate = 0
    time_stats_total_time_spent = 0
    
    for match in matches:
        kind = match.group('kind')
        mode = match.group('mode')
        total_minutes = parseHumanizedTime(match.group('duration'))

        if issue:

            if kind in ['estimate', 'estimated']:
                if mode == 'add':
                    issue.time_stats_time_estimate += total_minutes
                elif mode == 'subtract':
                    issue.time_stats_time_estimate -= total_minutes
                elif mode == 'set':
                    issue.time_stats_time_estimate = total_minutes
            elif kind in ['spend', 'spent']:
                if mode == 'add':
                    issue.time_stats_total_time_spent += total_minutes
                elif mode == 'subtract':
                    issue.time_stats_total_time_spent -= total_minutes
                elif mode == 'set':
                    issue.time_stats_total_time_spent = total_minutes

        else:

            if kind in ['estimate', 'estimated']:
                if mode == 'add':
                    time_stats_time_estimate += total_minutes
                elif mode == 'subtract':
                    time_stats_time_estimate -= total_minutesAgr
            elif kind in ['spend', 'spent']:
                if mode == 'add':
                    time_stats_total_time_spent += total_minutes
                elif mode == 'subtract':
                    time_stats_total_time_spent -= total_minutes

    if issue:

        issue.time_stats_human_time_estimate = humanizeTime(issue.time_stats_time_estimate)
        issue.time_stats_human_total_time_spent = humanizeTime(issue.time_stats_total_time_spent)
            
        return issue

    else:
        return (time_stats_time_estimate, time_stats_total_time_spent)