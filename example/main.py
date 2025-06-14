import os
import json
import time
import psutil
import argparse

from sent import sent
from crud import CRUD
from orm.session import Session
from models.model import Users, Followers, Posts, Likes, Comments

parser = argparse.ArgumentParser(description="Run tests with environment configurations")
parser.add_argument("--cpu", type=float, default=os.getenv("CPU", 1), help="Number of CPU cores")
parser.add_argument("--size", type=float, default=os.getenv("SIZE", 100), help="Size of data")
parser.add_argument("--memory", type=float, default=os.getenv("MEMORY", 1024), help="Memory allocation in MB")
parser.add_argument("--database", type=str, default=os.getenv("DATABASE", "sqlite"), help="Database URL")
args = parser.parse_args()
    
config = {}
if args.database == 'sqlite':
    from connection.sqlite import DatabaseConnection
    config ={'database':"socialmedia.db"}
if args.database == 'postgresql':
    from connection.psql import DatabaseConnection
    config = {'database': 'socialmedia', 'user': 'testing', 'password': 'testing', 'host': 'postgres-socialmedia', 'port': 5432}
if args.database == 'mysql':
    from connection.mysql import DatabaseConnection
    config = {'database': 'socialmedia', 'user': 'testing', 'password': 'testing', 'host': 'mysql-socialmedia', 'port': 3306}

connection = DatabaseConnection(config)
crud = CRUD()


class Test:
    def __init__(self, size, cpu, memory, database):
        self.cpu = cpu
        self.size = size
        self.memory = memory
        self.database = database
        self.results = {}

    def measure_resources(func):
        def wrapper(self, model_name, *args, **kwargs):
            process = psutil.Process()
            cpu_before = process.cpu_percent(interval=None)
            mem_before = process.memory_info().rss
            start_time = time.time()
            result = func(self, model_name, *args, **kwargs)
            end_time = time.time()
            cpu_after = process.cpu_percent(interval=None)
            mem_after = process.memory_info().rss
            cpu_usage = cpu_after - cpu_before
            mem_usage = (mem_after - mem_before) / (1024 * 1024)
            exec_time = end_time - start_time

            if model_name not in self.results:
                self.results[model_name] = []

            self.results[model_name].append({
                "function": func.__name__,
                "response_time": exec_time,
                "cpu_usage": cpu_usage,
                "memory_usage": mem_usage
            })

            return result

        return wrapper

    @measure_resources
    def create(self, model_name, model, data):
        with Session(connection) as db:
            return crud.create(db=db, model=model, data=data)

    @measure_resources
    def bulk_create(self, model_name, model, datas):
        with Session(connection) as db:
            return crud.bulk_create(db=db, model=model, data=datas)

    @measure_resources
    def get_list(self, model_name, model):
        with Session(connection) as db:
            return crud.get_list(db=db, model=model)

    @measure_resources
    def get_by_id(self, model_name, model, id: int):
        with Session(connection) as db:
            return crud.get_by_id(db=db, model=model, id=id)

    @measure_resources
    def update(self, model_name, model, id: int, **data):
        with Session(connection) as db:
            return crud.update(db, model, {"id": id}, **data)

    @measure_resources
    def delete(self, model_name, model, id: int):
        with Session(connection) as db:
            return crud.delete(db, model, {"id": id})

    def show_results(self):
        data = {
            "framework":"jitorm",
            "cpu": self.cpu,
            "size": self.size,
            "memory": self.memory,
            "result": self.results,
            "database": self.database
        }
        print(data)
        sent(data=data)


if __name__ == '__main__':
    test = Test(size=args.size, cpu=args.cpu, memory=args.memory, database=args.database)

    # Load JSON data for testing
    with open(f'data/{int(args.size)}/users.json', 'r') as json_file:
        users = json.load(json_file)
    with open(f'data/{int(args.size)}/followers.json', 'r') as json_file:
        followers = json.load(json_file)
    with open(f'data/{int(args.size)}/posts.json', 'r') as json_file:
        posts = json.load(json_file)
    with open(f'data/{int(args.size)}/likes.json', 'r') as json_file:
        likes = json.load(json_file)
    with open(f'data/{int(args.size)}/comments.json', 'r') as json_file:
        comments = json.load(json_file)

    # Testing Users model
    test.create("Users", Users, users[0])
    test.bulk_create("Users", Users, users[1:])
    test.get_by_id("Users", Users, id=1)
    test.get_list("Users", Users)
    test.update("Users", Users, id=1, name="Updated Name")

    # Testing Followers model
    test.create("Followers", Followers, followers[0])
    test.bulk_create("Followers", Followers, followers[1:])
    test.get_by_id("Followers", Followers, id=1)
    test.get_list("Followers", Followers)

    # Testing Posts model
    test.create("Posts", Posts, posts[0])
    test.bulk_create("Posts", Posts, posts[1:])
    test.get_by_id("Posts", Posts, id=1)
    test.get_list("Posts", Posts)

    # Testing Likes model
    test.create("Likes", Likes, likes[0])
    test.bulk_create("Likes", Likes, likes[1:])
    test.get_by_id("Likes", Likes, id=1)
    test.get_list("Likes", Likes)

    # Testing Comments model
    test.create("Comments", Comments, comments[0])
    test.bulk_create("Comments", Comments, comments[1:])
    test.get_by_id("Comments", Comments, id=1)
    test.get_list("Comments", Comments)
    test.update("Comments", Comments, id=1, comment="Updated Comment")

    test.delete("Comments", Comments, id=comments[-1].get("id"))
    test.delete("Likes", Likes, id=likes[-1].get("id"))
    test.delete("Posts", Posts, id=posts[-1].get("id"))
    test.delete("Followers", Followers, id=followers[-1].get("id"))
    test.delete("Users", Users, id=users[-1].get("id"))
    
    # Show results
    test.show_results()
