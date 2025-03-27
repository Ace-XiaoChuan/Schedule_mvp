from controllers.task_controller import TaskController


def main():
    app = TaskController()
    try:
        app.run()
    finally:
        app.shutdown()


if __name__ == "__main__":
    main()
