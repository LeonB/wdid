# from zeitgeist.client import ZeitgeistClient
# from zeitgeist.datamodel import *
import gi
gi.require_version('Zeitgeist', '2.0')
from gi.repository import Zeitgeist

import sys
import time
import os
from wdid.task import Task
from wdid.lib.prettytable import PrettyTable
import wdid.config
import datetime as dt
from operator import attrgetter

class App:

    # tasks = []
    document_tasks = []
    website_tasks = []
    document_events = None
    website_events = None

    def list(self, start_time, end_time):
        log = Zeitgeist.Log.get_default()
        tr = Zeitgeist.TimeRange.new(start_time, end_time)

        # Find all document events
        log.find_events(
            tr,
            [wdid.config.templates[0]],
            Zeitgeist.StorageState.ANY,
            0,
            Zeitgeist.ResultType.LEAST_RECENT_EVENTS,
            None,
            self.on_document_events_received,
            None
        )

        # Find all website events
        log.find_events(
            Zeitgeist.TimeRange.anytime(),
            [wdid.config.templates[1]],
            Zeitgeist.StorageState.ANY,
            0,
            Zeitgeist.ResultType.LEAST_RECENT_EVENTS,
            None,
            self.on_website_events_received,
            None
        )

    # def on_document_events_received(self, events):
    def on_document_events_received(self, source_object, result, user_data):
        result_set = source_object.find_events_finish(result)

        self.document_events = []
        for i in range(result_set.size()):
            event = events.next_value()
            self.document_events.append(event)

        if self.document_events != None and self.website_events != None:
            tasks = self.process_events()
            self.print_tasks(tasks)

            # Stop the program
            sys.exit()

    def on_website_events_received(self, source_object, result, user_data):
        result_set = source_object.find_events_finish(result)

        self.website_events = []
        for i in range(result_set.size()):
            event = events.next_value()
            self.website_events.append(event)

        if self.document_events != None and self.website_events != None:
            tasks = self.process_events()
            self.print_tasks(tasks)

            # Stop the program
            sys.exit()

    def process_events(self):
        self.process_document_events(self.document_events)
        self.process_website_events(self.website_events)

        # Merge the two different kind of tasks in one list
        tasks = self.merge_tasks(self.document_tasks, self.website_tasks)
        # First filter
        tasks = self.filter_tasks(tasks)
        # Then combine
        tasks = self.combine_tasks_based_on_project(tasks)
        return tasks

    def filter_tasks(self, tasks):
        for task in tasks[:]:
            if task.duration().seconds < wdid.config.minimum_duration:
                tasks.remove(task)

        return tasks

    def print_tasks(self, tasks):
        t = PrettyTable(['description', 'start', 'end', 'duration'])
        t.footer = True
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

        total_duration = dt.timedelta()
        for task in tasks:
            total_duration += task.duration()

        # Add footer with total duration
        t.add_row([
            '',
            '',
            '',
            total_duration
        ])

        print(t)

    def merge_tasks(self, tasks1, tasks2):
        tasks = tasks1 + tasks2
        tasks = sorted(tasks, key=attrgetter('start_time'))
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
        new_task = Task.from_event(event)

        if not new_task.identifier:
            return None

        if len(tasks):
            last_task = tasks[-1]
        else:
            last_task = None

        # Check if the last task is the same
        if last_task and last_task.identifier == new_task.identifier:
            diff = new_task.start_time - last_task.end_time

            # Check if the time between the last event and this new
            # event hasn't been too long
            # If it has been too long: create new task
            if diff.seconds > wdid.config.max_difference_between_tasks:
                # new_task.uris.add(uri)
                new_task.reason = 'timediff'
                tasks.append(new_task)
            else:
                last_task.end_time = new_task.start_time
                # last_task.uris.add(uri)
        else:
            # new_task.uris.add(uri)
            new_task.reason = 'identifier'
            tasks.append(new_task)

        return tasks

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
