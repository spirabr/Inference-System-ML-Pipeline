import mlflow
from git import Repo
import os


def register_model_in_database(name, topic):
  import requests
  import json
  token_response = requests.post(os.environ["AUTH_ENDPOINT"])
  response_dict = json.loads(token_response.text)
  token = response_dict["access_token"]

  requests.post(os.environ["MODEL_CREATION_ENDPOINT"], headers={"Authorization: Bearer" + token}, data={"name": name, "publishing_channel": topic})

def register_model_in_mlflow():
  from model import ModelTemplate
  mlflow.set_tracking_uri(os.environ["MLFLOW_CONN_URL"])
  model = ModelTemplate()
  mlflow.pyfunc.log_model(
    artifact_path=os.environ["MLFLOW_BUCKET_NAME"],
    registered_model_name=model_name,
    python_model=model
  )

def register_model_in_database(name, topic):
  import requests
  import json
  token_response = requests.post(os.environ["AUTH_ENDPOINT"])
  response_dict = json.loads(token_response.text)
  token = response_dict["access_token"]

  requests.post(os.environ["MODEL_CREATION_ENDPOINT"], headers={"Authorization: Bearer" + token}, data={"name": name, "publishing_channel": topic})


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
  model_name = os.environ["MODEL_NAME"]
  model_topic_name = os.environ["MODEL_TOPIC"]

  register_model_in_database(model_name,model_topic_name)
  register_model_in_mlflow()

  model_path = "models:/"+model_name+"/Production"
  directory = "./" + model_name + "/"

  Repo.clone_from(os.environ["REPOSITORY_URL"], directory)

  substitute_occurence_in_file('your-model-name-here', model_name, directory,"docker-compose.server.yml")
  substitute_occurence_in_file('your-model-name-here', model_name, directory,"build-server.sh")
  substitute_occurence_in_file('your-model-name-here', model_name, directory,"stop-server.sh")
  substitute_occurence_in_file('/path-to-project/', "/home/spira-inference-system/model-deploys/" + model_name + "/", directory,"docker-compose-model@.service")
  substitute_occurence_in_file('your-model-topic-here', model_topic_name, directory,"example.env",new_filename = ".env")
  substitute_occurence_in_file('your-model-mlflow-path-here', model_path, directory,".env")