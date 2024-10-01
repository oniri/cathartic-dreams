import os
from dotenv import load_dotenv
load_dotenv()


def env(key):
    return os.environ[key]