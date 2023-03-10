import mlflow
from git import Repo
import os
from dotenv import load_dotenv
from typing import List, Tuple
from mlflow.pyfunc import PythonModel
import re

class ModelTemplate(PythonModel):

    def load_context(self, context) -> None:
      pass

    def predict(self, context, model_input) -> Tuple[List[float],str]:
      # model predict method should be implemented here
      pass

def register_model(model_name, model_topic_name):
  register_model_in_database(model_name, model_topic_name)
  register_model_in_mlflow()

def register_model_in_mlflow():
  print("registering model in mlflow...")
  mlflow.set_tracking_uri(os.environ["MLFLOW_CONN_URL"])
  model = ModelTemplate()

  mlflow.pyfunc.log_model(
    artifact_path=os.environ["MLFLOW_BUCKET_NAME"],
    registered_model_name=model_name,
    python_model=model
  )

  print("model successfully registered in mlflow!")

def register_model_in_database(name, topic):
  print("registering model in database...")
  import requests
  import json
  token_response = requests.post(os.environ["AUTH_ENDPOINT"],data={"username": os.environ["ACCESS_USER"], "password": os.environ["ACCESS_KEY"]})
  response_dict = json.loads(token_response.text)
  token = response_dict["access_token"]

  requests.post(os.environ["MODEL_CREATION_ENDPOINT"], headers={"Authorization": "Bearer " + token, "Content-Type": "application-json"}, data=json.dumps({"name": name, "publishing_channel": topic}))
  print("model successfully registered in database!")

def substitute_occurence_in_file(occurence, replacement, dir, filename, new_filename = ""):
  fin = open(dir + filename, "rt")
  fout = open(dir + "/tmp", "wt")
  for line in fin:
    fout.write(line.replace(occurence, replacement))
  fin.close()
  fout.close()

  if new_filename != "":
    os.remove(dir + filename)
    os.rename(dir + "/tmp",dir + new_filename)
  else:
    os.remove(dir + filename)
    os.rename(dir + "/tmp",dir + filename)

if __name__=="__main__":
  load_dotenv()
  model_name = input("name of the new model:")
  
  if not bool(re.match(r"[a-zA-Z0-9\-\_]+\Z",model_name)):
    print("Model name should be a string matching the regex [a-zA-Z0-9\-\_]+")
    raise SystemExit

  model_topic_name = model_name + "-topic"

  register_model(model_name,model_topic_name)

  model_path = "models:/"+model_name+"/Production"
  directory = os.environ["PATH_TO_PROJECT"] + "/" + model_name + "/"

  print("creating model server repository...")

  Repo.clone_from(os.environ["REPOSITORY_URL"], directory)
  substitute_occurence_in_file('your-model-name-here', model_name, directory,"docker-compose.server.yml")
  substitute_occurence_in_file('your-model-name-here', model_name, directory,"build-server.sh")
  substitute_occurence_in_file('your-model-name-here', model_name, directory,"stop-server.sh")
  substitute_occurence_in_file('/path-to-project/', directory, directory,"docker-compose-model@.service")
  substitute_occurence_in_file('your-model-topic-here', model_topic_name, directory,"example.env", new_filename=".env")
  substitute_occurence_in_file('your-model-mlflow-path-here', model_path, directory,".env")

  print("model server setup is complete.")
  print("WARNING: do not forget to change model version in MLFlow to Production and start the service!")