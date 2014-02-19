from zeitgeist.datamodel import *
import os

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
max_difference_between_tasks = 5 * 60

def get_project_directories_by_detail():
    projects = project_directories
    projects.sort(
            cmp=lambda x,y: cmp(x.count(os.sep), y.count(os.sep)),
            reverse=True
            )
    return projects
