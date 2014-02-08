from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import *
import sys
import time
import os
from urlparse import urlparse
import re
from wdid.task import Task
import datetime as dt

class App:

    tasks = []

    project_directories = [
        '~/Public',
        '~/Workspaces/prive',
        '~/Workspaces/werk/losse projecten',
        '~/Workspaces/werk/sites'
    ]

    templates = [
        Event.new_for_values(subject_interpretation=Interpretation.DOCUMENT),
        Event.new_for_values(subject_interpretation=Interpretation.WEBSITE)
    ]

    difference_between_tasks = 5 * 60
    # for websites 2 minutes?
    # difference_between_tasks = 2 * 60

    # Website alleen als er geen last_task is??..

    def list(self, start_time, end_time):
        zeitgeist = ZeitgeistClient()
        zeitgeist.find_events_for_templates(self.templates, self.on_events_received,
                num_events=0,
                timerange=TimeRange(start_time, end_time),
                result_type=ResultType.LeastRecentEvents
        )

    def on_events_received(self, events):
        for event in events:
            self.process_event(event)

        # if start_time == end_time: remove the last task
        self.check_last_task()

        for task in self.tasks:
            # continue
            event_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(event.timestamp)/1000.0))
            print "------------"
            print "- identifier: %s" % task.identifier
            print "- start_time: %s" % task.start_time
            print "- end_time: %s" % task.end_time
            print "- reason: %s" % task.reason
            # print "- uris: %s" % task.uris

        # Stop the program
        sys.exit()

    def process_event(self, event):
        uri = str(event.subjects[0].uri)
        identifier = self.get_identifier_from_uri(uri)
        event_timestamp = int(event.timestamp)/1000
        event_datetime = dt.datetime.fromtimestamp(event_timestamp)

        if not identifier:
            return None

        # Websites alleen processen if
        # 
        # last_task niet processen als vorige taak == file
        # èn meer dan 5 min
        if last_task and last_task.identifier == identifier:
            if diff.seconds > self.difference_between_tasks:

        # website overslaan als de vorige task een file is
        # en de volgende task minder dan 5 minuten daarop volgt
        # Je moet daarvoor wel door alle events loopen

        if len(self.tasks):
            last_task = self.tasks[-1]
        else:
            last_task = None

        # if identifier != 'imgur.com':
        #     return None

        # Check if the last task is the same
        if last_task and last_task.identifier == identifier:
            diff = event_datetime - last_task.end_time

            # Check if the time between the last event and this new
            # event hasn't been too long
            # If it has been too long: create new task
            if diff.seconds > self.difference_between_tasks:
                new_task = Task()
                new_task.identifier = identifier
                new_task.start_time = event_datetime
                new_task.end_time = event_datetime
                new_task.uris.add(uri)
                new_task.reason = 'timediff'

                self.check_last_task()
                self.tasks.append(new_task)
            else:
                last_task.end_time = event_datetime
                last_task.uris.add(uri)
        else:
            # Check if the last task can be removed
            # If it can be removed: check the event again against
            # the adjusted task list
            if self.check_last_task():
                return self.process_event(event)

            new_task = Task()
            new_task.identifier = identifier
            new_task.start_time = event_datetime
            new_task.end_time = event_datetime
            new_task.uris.add(uri)
            new_task.reason = 'identifier'

            self.tasks.append(new_task)

        return

        # print "- %s" % event
        print "------------"
        print "- actor: %s" % event.actor
        print "- Interpretation: %s" % event.interpretation
        print "- manifestation: %s" % event.manifestation
        print "- timestamp: %s" % event.timestamp
        print "- timestamp: %s" % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(event.timestamp)/1000.0))
        print "- len(subjects): %s" % len(event.subjects)
        print "- uri: %s" % event.subjects[0].uri
        print "- Interpretation: %s" % event.subjects[0].interpretation
        print "- manifestation: %s" % event.subjects[0].manifestation
        print "- origin: %s" % event.subjects[0].origin
        print "- mimetype: %s" % event.subjects[0].mimetype
        print "- text: %s" % event.subjects[0].text
        print "- storage: %s" % event.subjects[0].storage
        print "- project: %s" % project
        # print "- %s" % event.__class__

    def check_last_task(self):
        if not len(self.tasks):
            return

        last_task = self.tasks[-1]

        # If start_time == end_time (with a 1 second window): remove the task
        if (last_task.end_time - last_task.start_time).seconds < 2:
            self.tasks.remove(last_task)
            return last_task

    def get_project_directories_by_detail(self):
        projects = self.project_directories
        projects.sort(
                cmp=lambda x,y: cmp(x.count(os.sep), y.count(os.sep)),
                reverse=True
                )
        return projects

    def get_identifier_from_uri(self, uri):
        pieces = urlparse(uri)

        if pieces.scheme == 'file':
            identifier = self.get_identifier_from_uri_file(uri)
        else:
            identifier = self.get_identifier_from_uri_http(uri)

        if not identifier:
            return None
        else:
            return str(identifier)

    def get_identifier_from_uri_http(self, uri):
        hostname = urlparse(uri).hostname.split(".")
        hostname = '.'.join(len(hostname[-2]) < 4 and hostname[-3:] or hostname[-2:])
        return hostname

    def get_identifier_from_uri_file(self, uri):
        pieces = urlparse(uri)
        uri_path = pieces.path
        uri_dir = os.path.dirname(uri_path)

        for project_dir in self.get_project_directories_by_detail():
            project_dir_norm = os.path.normpath(
                    os.path.expanduser(os.path.expandvars(project_dir))
                    )

            if uri_dir.startswith(project_dir_norm):
                # return project_dir + one subdir
                # project_dir = ~/projects
                # return ~/projects/my_project

                pattern = '^' + re.escape(project_dir_norm) + os.sep + '(.*?)(\/|$)'
                m = re.match(pattern, uri_dir)

                # return original notation:
                # e.g. ~/projects instead of /home/$user/projects
                return project_dir + os.sep + m.group(1)

# zeitgeist = ZeitgeistClient()

# def on_events_received(events):
#     print len(events)
#     # sys.exit(2)
#     for event in events:
#         # print "- %s" % event
#         print "------------"
#         print "- actor: %s" % event.actor
#         print "- Interpretation: %s" % event.interpretation
#         print "- manifestation: %s" % event.manifestation
#         print "- timestamp: %s" % event.timestamp
#         print "- timestamp: %s" % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(event.timestamp)/1000.0))
#         print "- len(subjects): %s" % len(event.subjects)
#         print "- uri: %s" % event.subjects[0].uri
#         print "- Interpretation: %s" % event.subjects[0].interpretation
#         print "- manifestation: %s" % event.subjects[0].manifestation
#         print "- origin: %s" % event.subjects[0].origin
#         print "- mimetype: %s" % event.subjects[0].mimetype
#         print "- text: %s" % event.subjects[0].text
#         print "- storage: %s" % event.subjects[0].storage
#         # print "- %s" % event.__class__

#     # if events:
#     #     song = events[0]
#     #     print "Last song: %s" % song.subjects[0].uri
#     # else:
#     #     print "You haven't listened to any songs."

# # template = Event.new_for_values(subject_interpretation=Interpretation.AUDIO)
# templates = [
#     Event.new_for_values(subject_interpretation=Interpretation.DOCUMENT),
#     Event.new_for_values(subject_interpretation=Interpretation.WEBSITE)
# ]

# # templates = [
# #     Event.new_for_values(actor='application://thunderbird.desktop')
# # ]

# # from dateutil import parser
# # from_time = int(parser.parse("2014-02-07").strftime('%s'))*1000
# # to_time = int(parser.parse("2014-02-08").strftime('%s'))*1000

# # see list() in hamster-cli
# times = None
# start_time, end_time = parse_datetime_range(" ".join(times or []))
# start_time = start_time or dt.datetime.combine(dt.date.today(), dt.time())
# end_time = end_time or start_time.replace(hour=23, minute=59, second=59)

# start_time = int(start_time.strftime('%s'))*1000
# end_time = int(end_time.strftime('%s'))*1000

# template = Event.new_for_values()
# zeitgeist.find_events_for_templates(templates, on_events_received,
#         num_events=1,
#         timerange=TimeRange(start_time, end_time),
#         result_type=ResultType.LeastRecentEvents
#         # timerange=TimeRange.from_seconds_ago(3600*24*30*3)
# )

# # def on_events_received(events):
# #     for event in events:
# #         print "- %s" % event.subjects[0].uri

# # tmpl1 = Event.new_for_values(subject_interpretation=Interpretation.AUDIO)
# # tmpl2 = Event.new_for_values(subject_interpretation=Interpretation.VIDEO)
# # zeitgeist.find_events_for_templates([tmpl1, tmpl2],
# #                                     on_events_received, num_events=5)

