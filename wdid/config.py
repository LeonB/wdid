import gi
gi.require_version('Zeitgeist', '2.0')
from gi.repository import Zeitgeist
import os

project_directories = [
    '~/Public',
    '~/Workspaces/prive',
    '~/Workspaces/werk/losse projecten',
    '~/Workspaces/werk/sites'
]

templates = [
    # Zeitgeist.Event.full(Zeitgeist.DOCUMENT),
    # Zeitgeist.Event.full(Zeitgeist.WEBSITE)
]

e1 = Zeitgeist.Event()
e1.props.interpretation = Zeitgeist.DOCUMENT
e2 = Zeitgeist.Event()
e2.props.interpretation = Zeitgeist.WEBSITE
templates = [e1, e2]

minimum_duration = 2 * 60
max_difference_between_tasks = 5 * 60

def get_project_directories_by_detail():
    projects = project_directories
    projects.sort(
            cmp=lambda x,y: cmp(x.count(os.sep), y.count(os.sep)),
            reverse=True
            )
    return projects
