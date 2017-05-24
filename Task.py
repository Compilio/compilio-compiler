import os
import pickle
import subprocess
import time
from zipfile import ZipFile

from TaskState import TaskState


class Task:
    TASKS_FOLDER = 'tasks/'

    def __init__(self, task_id, output_files):
        self.id = task_id
        self.output_files = output_files
        self.workspace_path = None
        self.state = TaskState.COMPILING

        self.output_log = None

    def __get_workspace_path(self):
        return Task.TASKS_FOLDER + self.id + '/workspace/'

    def save(self):
        file = open('tasks/' + self.id + '/task.obj', 'wb')
        this = self
        pickle.dump(this, file)

    def get_state(self):
        return self.state

    def change_state(self, state):
        self.state = state
        self.save()

    def save_input_files(self, input_files):
        workspace_path = self.__get_workspace_path()
        if not os.path.exists(workspace_path):
            os.makedirs(workspace_path)
        filename = input_files.name
        with open(os.path.join(workspace_path, filename), 'wb') as file:
            file.write(input_files.body)
            file.close()

        self.workspace_path = workspace_path
        self.save()

    def compile(self, bash_command):
        output_file = 'tasks/' + self.id + '/output.log'
        print('Running command : ' + bash_command)

        with open(output_file, 'wb') as writer, open(output_file, 'rb', 1) as reader:
            process = subprocess.Popen(bash_command,
                                       stdout=writer,
                                       cwd=self.workspace_path,
                                       shell=True)
            while process.poll() is None:
                print(reader.read())
                time.sleep(0.5)
            print(reader.read())

        with open(output_file, 'rb', 1) as reader:
            self.output_log = reader.read()

        with ZipFile('tasks/' + self.id + '/output.zip', 'w') as zip_file:
            zip_file.write(self.__get_workspace_path() + self.output_files, self.output_files)

        self.change_state(TaskState.SUCCESS)

    def get_output_zip(self):
        if self.state != TaskState.SUCCESS:
            return None
        return 'tasks/' + self.id + '/output.zip'

    @staticmethod
    def get_task(task_id):
        try:
            file = open('tasks/' + task_id + '/task.obj', 'rb')
            return pickle.load(file)
        except FileNotFoundError:
            return None
