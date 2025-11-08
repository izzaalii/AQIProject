import os
try:
    import hopsworks
    from hopsworks import featurestore
except Exception:
    hopsworks = None

class HopsworksClient:
    def __init__(self):
        host = os.getenv('HOPSWORKS_HOST')
        api_key = os.getenv('HOPSWORKS_API_KEY')
        project = os.getenv('HOPSWORKS_PROJECT', 'default')
        if not host or not api_key:
            raise RuntimeError('Hopsworks credentials not set')
        self.conn = hopsworks.login(api_key_value=api_key, host=host)
        self.fs = featurestore.FeatureStore(self.conn.get_feature_store())

    def push_features(self, df, feature_group_name='aqi_features'):
        fg = self.fs.get_or_create_feature_group(name=feature_group_name, version=1, primary_key=['timestamp'])
        fg.insert(df)
