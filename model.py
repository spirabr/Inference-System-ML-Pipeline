from typing import List, Tuple
from mlflow.pyfunc import PythonModel


class ModelTemplate(PythonModel):

    def load_context(self, context) -> None:
      pass

    def predict(self, context, model_input) -> Tuple[List[float],str]:
      pass