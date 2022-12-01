import os


def get_raw_sql_query(script_name:str):
  with open(os.path.join(os.path.dirname(__file__),f"queries/{script_name}")) as f:
    return f.read()