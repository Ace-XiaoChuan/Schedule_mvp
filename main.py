from controllers.task_controller import TaskController
from view import MainView


def main():
    view = MainView()
    app = TaskController(view)
    try:
        app.run()
    finally:
        app.shutdown()


if __name__ == "__main__":
    main()
