import os.path
import importlib
import inspect


class Data:
    def __init__(self, name):
        self.name = name
        m = importlib.import_module(name)
        dirname = os.path.dirname(inspect.getsourcefile(m))
        self.dirname = os.path.abspath(dirname)

    def push(self, subpath):
        """
        Change the data object to a path relative to the module.
        """
        dirname = os.path.normpath(os.path.join(self.dirname, subpath))
        ret = Data(self.name)
        ret.dirname = dirname
        return ret

    def path(self, path):
        """
        Returns a path to the package data housed at 'path' under this
        module.Path can be a path to a file, or to a directory.

        This function will raise ValueError if the path does not exist.
        """
        fullpath = os.path.normpath(os.path.join(self.dirname, path))
        if not os.path.exists(fullpath):
            raise ValueError("dataPath: %s does not exist." % fullpath)
        return fullpath


pkg_data = Data(__name__).push("..")


def dict_to_value(data: dict, keys):
    val = data
    if isinstance(keys, list):
        for key in keys:
            try:
                if val:
                    if isinstance(key, int):
                        try:
                            val = val[key]
                        except:
                            val = val.get(str(key))
                    elif isinstance(key, str):
                        if key.startswith('$'):
                            new_key = key[1:]
                            if val.get(new_key) is not None:
                                val = val.get(new_key)
                            else:
                                val = val.get(key)
                        else:
                            val = val.get(key)
                    if val == data:
                        break
                else:
                    break
            except Exception as e:
                print(key, data)
                raise Exception(e)

    if isinstance(keys, str) and '.' in keys:
        if '[' in keys:
            keys = keys.replace('[', '.')
        if ']' in keys:
            keys = keys.replace(']', '')
        keys = keys.split('.')
        for key in keys:
            try:
                try:
                    key = int(key)
                except:
                    pass
                if val:
                    if isinstance(key, int):
                        try:
                            val = val[key]
                        except:
                            val = val.get(str(key))
                    elif isinstance(key, str):
                        if key.startswith('$'):
                            new_key = key[1:]
                            if val.get(new_key) is not None:
                                val = val.get(new_key)
                            else:
                                val = val.get(key)
                        else:
                            if val.get(key) is not None:
                                val = val.get(key)
                            else:
                                val = val.get('${}'.format(key))
                    if val == data:
                        break
                else:
                    break
            except Exception as e:
                print(key, data)
                raise Exception(e)
    elif isinstance(keys, str):
        val = val.get(keys)

    return val