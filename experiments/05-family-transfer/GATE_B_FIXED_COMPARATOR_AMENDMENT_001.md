# Gate B fixed-comparator amendment 001

**Status:** prospective frozen specification. Fitting is disabled.

Grouped development closed as `FOLD_GEOMETRY_INFEASIBLE`. No alternative seed,
fold count, allocation algorithm, tuning, candidate comparison, development
prediction, or development metric will be attempted. Internal Stage 1 is closed
because its grouped validation instrument is infeasible, not because the
scientific hypothesis failed.

The historically motivated fixed comparator is fit once on all 278 discovery
proteins. Its strength is an assumption testable only on the confirmatory set.

Feature order is `length,A,C,D,E,F,G,H,I,K,L,M,N,P,Q,R,S,T,V,W,Y`. Length is the complete uppercase
sequence length. Each canonical amino-acid fraction is its count divided by
complete sequence length. Noncanonical residues remain in the denominator and
contribute to no canonical numerator. Empty sequences and sequence-hash
mismatches raise. Labels are negative=0 and positive=1.

Classifier: `sklearn.ensemble.RandomForestClassifier` under scikit-learn
`1.6.1` with parameters:

```json
{
  "bootstrap": true,
  "ccp_alpha": 0.0,
  "class_weight": null,
  "criterion": "gini",
  "max_depth": null,
  "max_features": "sqrt",
  "max_leaf_nodes": null,
  "max_samples": null,
  "min_impurity_decrease": 0.0,
  "min_samples_leaf": 2,
  "min_samples_split": 2,
  "min_weight_fraction_leaf": 0.0,
  "monotonic_cst": null,
  "n_estimators": 300,
  "n_jobs": 1,
  "oob_score": false,
  "random_state": 20260829,
  "verbose": 0,
  "warm_start": false
}
```

Joblib `1.5.3` serializes the fitted object without compression.
The runner may emit only the frozen feature table, model artifact, and
non-circular provenance. It may not call prediction, probability, scoring,
cross-validation, OOB evaluation, or inspect feature importances. Confirmatory
paths are prohibited. The artifact is not evaluated until A2 and Gate C permit
the confirmatory test.
