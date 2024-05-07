import pandas as pd
import numpy as np
from scipy.stats import boxcox
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder

# Custom transformers for DAYS_BIRTH and DAYS_ID_PUBLISH
class BirthAnonymizer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X['DAYS_BIRTH'] = (-X['DAYS_BIRTH'] // 365).apply(lambda x: f"{(x//10)*10}s")
        return X

class PublishCategorizer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        def categorize_days(days):
            if days < -3650:
                return 'More than 10 years'
            elif days < -1825:
                return '5-10 years'
            elif days < -365:
                return '1-5 years'
            else:
                return 'Less than 1 year'
        
        X = X.copy()
        X['DAYS_ID_PUBLISH'] = X['DAYS_ID_PUBLISH'].apply(categorize_days)
        return X

# Custom transformer for ORGANIZATION_TYPE
class OrgTypePseudonymizer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        self.org_type_mapping_ = {org: f"Org_{i+1}" for i, org in enumerate(X['ORGANIZATION_TYPE'].unique())}
        return self

    def transform(self, X):
        X = X.copy()
        X['ORGANIZATION_TYPE'] = X['ORGANIZATION_TYPE'].map(self.org_type_mapping_)
        return X

# ID Anonymization Transformer
class IDAnonymizer(BaseEstimator, TransformerMixin):
    def __init__(self, mod_value=100000):
        self.mod_value = mod_value

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X = X.applymap(lambda x: hash(x) % self.mod_value)
        return X

# BoxCox transformation for selected numeric features
class BoxCoxTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, columns=None):
        self.columns = columns
        self.lambdas_ = {}

    def fit(self, X, y=None):
        for col in self.columns:
            data = X[col].dropna()
            if data.min() > 0 and len(data.unique()) > 1:
                _, fitted_lambda = boxcox(data)
                self.lambdas_[col] = fitted_lambda
        return self

    def transform(self, X):
        X = X.copy()
        for col in self.columns:
            if col in self.lambdas_:
                lam = self.lambdas_[col]
                X[col] = X[col].apply(lambda x: boxcox(x + 1, lam) if x > 0 else x)
        return X


# Pipelines for preprocessing
numeric_transformer = Pipeline(steps=[
    ('abs', FunctionTransformer(np.abs, validate=False)),
    ('boxcox', BoxCoxTransformer(columns=['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3'])),
    ('imputer', SimpleImputer(strategy='mean'))
])

combined_transformer = Pipeline(steps=[
    ('birth_anonym', BirthAnonymizer()),
    ('publish_cat', PublishCategorizer()),
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),  # Imputes missing values with 'missing'
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

org_transformer = Pipeline(steps=[
    ('org_pseudo', OrgTypePseudonymizer()),
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

id_transformer = Pipeline(steps=[
    ('anonymize', IDAnonymizer())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])
