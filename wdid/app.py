from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import *
import sys
import time
import os
from urlparse import urlparse
import re
from wdid.task import Task
import datetime as dt
from prettytable import PrettyTable

class App:

    # tasks = []
    document_tasks = []
    website_tasks = []
    document_events = None
    website_events = None

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

    minimum_duration = 2 * 60
    difference_between_tasks = 5 * 60
    # difference_between_tasks = 5
    # for websites 2 minutes?
    # difference_between_tasks = 2 * 60

    # Website alleen als er geen last_task is??..

    def list(self, start_time, end_time):
        zeitgeist = ZeitgeistClient()

        # Find all document events
        zeitgeist.find_events_for_templates(
                [self.templates[0]],
                self.on_document_events_received,
                num_events=0,
                timerange=TimeRange(start_time, end_time),
                result_type=ResultType.LeastRecentEvents
        )
        # Find all website events
        zeitgeist.find_events_for_templates(
                [self.templates[1]],
                self.on_website_events_received,
                num_events=0,
                timerange=TimeRange(start_time, end_time),
                result_type=ResultType.LeastRecentEvents
        )

    def on_document_events_received(self, events):
        self.document_events = events

        if self.document_events and self.website_events:
            tasks = self.process_events()
            self.print_tasks(tasks)

            # Stop the program
            sys.exit()

    def on_website_events_received(self, events):
        self.website_events = events

        if self.document_events and self.website_events:
            tasks = self.process_events()
            self.print_tasks(tasks)

            # Stop the program
            sys.exit()

    def process_events(self):
        self.process_document_events(self.document_events)
        self.process_website_events(self.website_events)

        tasks = self.merge_tasks(self.document_tasks, self.website_tasks)
        tasks = self.combine_tasks_based_on_project(tasks)
        tasks = self.filter_tasks(tasks)
        return tasks

    def filter_tasks(self, tasks):
        for task in tasks[:]:
            if task.duration().seconds < self.minimum_duration:
                tasks.remove(task)

        return tasks

    def print_tasks(self, tasks):
        t = PrettyTable(['description', 'start', 'end', 'duration'])
        t.align['description'] = 'r'

        for task in tasks:
            t.add_row([
                task.identifier,
                task.start_time,
                task.end_time,
                task.duration()
            ])
        #     print "------------"
        #     print "- identifier: %s" % task.identifier
        #     print "- start_time: %s" % task.start_time
        #     print "- end_time: %s" % task.end_time
        #     print "- reason: %s" % task.reason
        #     print "- duration: %s" % task.duration()
        #     # print "- uris: %s" % task.uris

        print t

        total_duration = dt.timedelta()
        for task in tasks:
            total_duration += task.duration()

        print total_duration

    def merge_tasks(self, tasks1, tasks2):
        tasks = tasks1 + tasks2
        tasks.sort(
                cmp=lambda x,y: cmp(x.start_time, y.start_time),
                )
        return tasks

    def combine_tasks_based_on_project(self, tasks):
        previous_task = None

        # Make a copy ([:]) of the list and iterate through that
        for task in tasks[:]:
            if not previous_task:
                previous_task = task
                continue

            if not task.project:
                previous_task = task
                continue

            if previous_task.project == task.project:
                previous_task.end_time = task.end_time
                tasks.remove(task)
                continue

            previous_task = task

        return tasks

    def process_document_events(self, events):
        for event in events:
            self.process_event(event, self.document_tasks)

    def process_event(self, event, tasks):
        uri = str(event.subjects[0].uri)
        identifier = self.get_identifier_from_uri(uri)
        project = self.get_project_from_uri(uri)
        event_timestamp = int(event.timestamp)/1000
        event_datetime = dt.datetime.fromtimestamp(event_timestamp)

        if not identifier:
            return None

        if len(tasks):
            last_task = tasks[-1]
        else:
            last_task = None

        # Check if the last task is the same
        if last_task and last_task.identifier == identifier:
            diff = event_datetime - last_task.end_time

            # Check if the time between the last event and this new
            # event hasn't been too long
            # If it has been too long: create new task
            if diff.seconds > self.difference_between_tasks:
                new_task = Task()
                new_task.identifier = identifier
                new_task.project = project
                new_task.start_time = event_datetime
                new_task.end_time = event_datetime
                new_task.uris.add(uri)
                new_task.reason = 'timediff'

                tasks.append(new_task)
            else:
                last_task.end_time = event_datetime
                last_task.uris.add(uri)
        else:
            new_task = Task()
            new_task.identifier = identifier
            new_task.project = project
            new_task.start_time = event_datetime
            new_task.end_time = event_datetime
            new_task.uris.add(uri)
            new_task.reason = 'identifier'

            tasks.append(new_task)

        return tasks

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

    def process_website_events(self, events):
        # Remove all events that overlap existing (document) tasks
        for event in events:
            event_timestamp = int(event.timestamp)/1000
            event_datetime = dt.datetime.fromtimestamp(event_timestamp)

            if self.has_overlap_with_existing_tasks(event_datetime,
                    self.website_tasks):
                events.remove(event)

        for event in events:
            self.process_event(event, self.website_tasks)

    def has_overlap_with_existing_tasks(self, datetime, tasks):
        for task in tasks:
            # tasks is order by times
            # so if start_time is already bigger then datetime
            # there aren't going to be any smaller ones
            if task.start_time > datetime:
                return False

            if task.start_time < datetime and task.end_time > datetime:
                return True

        # Couldn't find anything
        return False

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

    def get_project_from_uri(self, uri):
        pieces = urlparse(uri)
        project = None

        if pieces.scheme == 'file':
            identifier = self.get_identifier_from_uri_file(uri)
            if identifier:
                project = identifier.split(os.sep)[-1]
        else:
            project = self.get_identifier_from_uri_http(uri)

        if not project:
            return None
        else:
            return str(project)

    def get_identifier_from_uri_http(self, uri):
        hostname = urlparse(uri).hostname
        hostname = re.sub('www\.', '', hostname)
        return hostname

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
