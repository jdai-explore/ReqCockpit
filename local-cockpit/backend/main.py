import sys
import json
from project_manager import ProjectManager
from sqlalchemy import create_engine

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command provided."}))
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == 'list_recent_projects':
            if len(sys.argv) != 3:
                raise ValueError("Usage: list_recent_projects <app_data_dir>")
            app_data_dir = sys.argv[2]
            pm = ProjectManager(app_data_dir)
            print(json.dumps(pm.list_recent_projects()))

        elif command == 'create_project':
            if len(sys.argv) != 5:
                raise ValueError("Usage: create_project <app_data_dir> <name> <path>")
            app_data_dir = sys.argv[2]
            name = sys.argv[3]
            path = sys.argv[4]
            pm = ProjectManager(app_data_dir)
            print(pm.create_project(name, path))

        else:
            raise ValueError(f"Unknown command: {command}")

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == '__main__':
    main()
