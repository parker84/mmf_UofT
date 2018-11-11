
"""
http://scikit-learn.org/stable/modules/cross_validation.html

- class imbalance: http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html#sklearn.model_selection.StratifiedKFold
- time series: http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html#sklearn.model_selection.TimeSeriesSplit
    - not iid cant use normal cv
    - if you do you'll be leaking information into the testing set by training on data from after the testing data occurred
    - you'll have inflated correlation between training and testing data
        - consider sampling data in the following way d0,d1,d2,d3,d4 d2 goes to testing rest goes to training
        - d2 is going to very correlated with the data in training then
            - for both the dependent and features
        - which will increase/inflate performance on testing set beyond reality
- grouped data: http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html#sklearn.model_selection.GroupKFold
    - not iid, cant use normal cv
    - ex: medical patients, want to see how we do on new groups => dont want to mix info from testing group into training data

CV explained: https://www.openml.org/a/estimation-procedures/1
"""