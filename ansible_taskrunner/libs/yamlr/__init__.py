from functools import reduce


class YamlReader:

    def __init__(self):
        pass

    def deep_get(self, data_input, keys, default=None):
        """Recursively retrieve values from a dictionary object"""
        result = ''
        if isinstance(data_input, dict):
            result = reduce(lambda d, key: d.get(key, default) if isinstance(
                d, dict) else default, keys.split('.'), data_input)
        return(result)

    def get(self, yaml_input, dict_path, default_data=''):
        """Interpret wildcard paths for retrieving values from a dictionary object"""
        try:
            ks = dict_path.split('.*.')
            if len(ks) > 1:
                path_string = ks[0]
                ds = self.deep_get(yaml_input, path_string)
                for d in ds:
                    path_string + '.{dd}.{dv}'.format(dd=d, dv=ks[1])
                    data = self.deep_get(yaml_input, path_string)
                    return data
            else:
                data = self.deep_get(yaml_input, dict_path)
                if not isinstance(data, dict):
                    data = {'data': data}
                return data
        except Exception as e:
            raise(e)
        else:
            return default_data
