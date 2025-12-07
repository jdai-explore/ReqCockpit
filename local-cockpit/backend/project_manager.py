import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.schema import create_database, Project

class ProjectManager:
    def __init__(self, app_data_dir):
        self.app_data_dir = app_data_dir
        self.recent_projects_file = os.path.join(app_data_dir, 'recent_projects.json')
        if not os.path.exists(self.app_data_dir):
            os.makedirs(self.app_data_dir)

    def create_project(self, name, path):
        db_path = os.path.join(path, f"{name}.sqlite")
        if os.path.exists(db_path):
            raise FileExistsError(f"Database file already exists: {db_path}")

        create_database(db_path)

        engine = create_engine(f'sqlite:///{db_path}')
        Session = sessionmaker(bind=engine)
        session = Session()

        new_project = Project(name=name)
        session.add(new_project)
        session.commit()
        session.close()

        self._add_to_recent_projects(name, db_path)
        return db_path

    def open_project(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Project file not found: {path}")

        project_name = os.path.splitext(os.path.basename(path))[0]
        self._add_to_recent_projects(project_name, path)
        return True

    def list_recent_projects(self):
        if not os.path.exists(self.recent_projects_file):
            return []

        with open(self.recent_projects_file, 'r') as f:
            return json.load(f)

    def _add_to_recent_projects(self, name, path):
        recent_projects = self.list_recent_projects()
        recent_projects = [p for p in recent_projects if p['path'] != path]
        recent_projects.insert(0, {'name': name, 'path': path})
        recent_projects = recent_projects[:10]

        with open(self.recent_projects_file, 'w') as f:
            json.dump(recent_projects, f, indent=4)
