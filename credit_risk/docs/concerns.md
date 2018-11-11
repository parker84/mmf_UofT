#### bias in DAYS_EMPLOYED
- uncovered in eda_app_table.ipynb

#### Why aren't there much more previous ids than current?
- "the table has (#loans in sample * # of relative previous credit cards * # of months where we have some history observable for the previous credit card"
- could be they were just missing history on these?

```python
>>> (cc_balance.SK_ID_PREV.unique().shape,
     cc_balance.SK_ID_CURR.unique().shape,
     cc_balance.shape)
((104307,), (103558,), (3840312, 23))
```