"""
On PythonAnywhere and similar WSGI servers, you can do either of the following
in your WSGI configuration file:

    - Import the `app` object from run.py. For example, in PythonAnywhere's
        WSGI file, set the final line to `from run import app as application`.

    - Import the `app` object directly from the `loginapp` module. For example,
        in PythonAnywhere's WSGI file, set the final line to `from loginapp
        import app as application`. This method doesn't require run.py.

Because there are so many ways to start a Python/Flask web app, and many of
them bypass run.py entirely, don't put any of your application code in here.
Think of run.py as a "shortcut" or "launcher" used to run your Flask app,
rather than a core part of the app itself.
"""
from app import app

# If run.py was actually executed (run), not just imported into another script,
# then start our Flask app on a local development server. To learn more about
# how we check for this, refer to https://realpython.com/if-name-main-python/.
if __name__ == "__main__":
    app.run(debug=True)