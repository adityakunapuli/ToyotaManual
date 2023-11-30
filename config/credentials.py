import yaml


def read_credentials_yaml(path='/Users/maradmin/toyota.yml') -> dict:
    """
    Credentials yaml file contain the following values (at min):
    username: <YOUR LOGIN EMAIL>
    password: <YOUR PASSWORD>
    :param path: path to the credentials yaml
    :return: dictionary
    """
    with open(path, 'r') as f:
        credentials = yaml.safe_load(f)
    # convert all values to string
    credentials = {k: str(v) for k, v in credentials.items()}
    return credentials


INFO = read_credentials_yaml()
