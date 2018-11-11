from lib.ML.fit_model_eval_and_save_model import FitEvalSaveModel
from lib.operational.read_write_helpers import ReadWriteData
from sklearn.ensemble import RandomForestClassifier
from lib.ML.eval import EvalBinaryClassifier
from sklearn.model_selection import KFold

class FitEvalCreditModel(FitEvalSaveModel):

    def __init__(self):
        import ipdb; ipdb.set_trace() # walk through to understand whats going on
        # (s is step into, r is step out of, n is next line)
        self.conn = ReadWriteData()
        dfs = {"train":
                    self.conn.query_psql_table("select * from final_feature_table")}
        feat_names = [c for c in dfs['train'].columns
                      if c != "TARGET"]
        print(f"features in model: {feat_names}")
        FitEvalSaveModel.__init__(dfs, feat_names, ["TARGET"])

    def cv_random_forest(self):
        rf = RandomForestClassifier()
        self.cross_validate_train(rf, EvalBinaryClassifier, nfolds=3, fold_func=KFold)

if __name__ == "__main__":
    fitEvalCreditModel = FitEvalCreditModel()
    fitEvalCreditModel.cv_random_forest()