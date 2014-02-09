from zeitgeist.datamodel import Interpretation
import datetime as dt
from urlparse import urlparse
import os
import wdid.config
import re
import sys
from zeitgeist.datamodel import Symbol

class Task:
    end_time = None
    event_type = ''
    identifier = None
    project = None
    reason = ''
    start_time = None
    uris = set()

    @classmethod
    def from_event(cls, event):
        interpretation = event.subjects[0].interpretation

        if Symbol.uri_is_child_of(interpretation, Interpretation.DOCUMENT):
            task = DocumentTask()
        elif Symbol.uri_is_child_of(interpretation, Interpretation.WEBSITE):
            task = WebsiteTask()
        else:
            print interpretation
            sys.exit()
            task = Task()

        event_type = task.get_event_type(event)
        event_timestamp = int(event.timestamp)/1000
        uri = str(event.subjects[0].uri)
        identifier = task.get_identifier_from_uri(uri)
        project = task.get_project_from_uri(uri)

        task.start_time = dt.datetime.fromtimestamp(event_timestamp)
        task.end_time = dt.datetime.fromtimestamp(event_timestamp)
        task.event_type = event_type
        task.identifier = identifier
        task.project = project
        task.uri = uri

        return task

    def get_identifier_from_uri_http(self, uri):
        hostname = urlparse(uri).hostname
        hostname = re.sub('www\.', '', hostname)
        return hostname

        hostname = urlparse(uri).hostname.split(".")
        hostname = '.'.join(len(hostname[-2]) < 4 and hostname[-3:] or hostname[-2:])
        return hostname


    def get_event_type(self, event):
        interpretation = event.subjects[0].interpretation

        for i in dir(Interpretation):
            value = str(getattr(Interpretation, i))
            if value == interpretation:
                return i

        return None

    def duration(self):
        return self.end_time - self.start_time

class DocumentTask(Task):
    def get_identifier_from_uri(self, uri):
        pieces = urlparse(uri)
        uri_path = pieces.path
        uri_dir = os.path.dirname(uri_path)

        for project_dir in wdid.config.get_project_directories_by_detail():
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

    def get_project_from_uri(self, uri):
        project = None
        identifier = self.get_identifier_from_uri(uri)
        if identifier:
            project = identifier.split(os.sep)[-1]

        return project

class WebsiteTask(Task):
    def get_identifier_from_uri(self, uri):
        hostname = urlparse(uri).hostname
        hostname = re.sub('www\.', '', hostname)
        return hostname

        hostname = urlparse(uri).hostname.split(".")
        hostname = '.'.join(len(hostname[-2]) < 4 and hostname[-3:] or hostname[-2:])
        return hostname

    def get_project_from_uri(self, uri):
        return self.get_identifier_from_uri_http(uri)
