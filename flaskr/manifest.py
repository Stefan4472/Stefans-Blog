import json
import typing


class Manifest:
    def __init__(
        self,
        filepath: str,
    ):
        self.filepath = filepath
        self.json_data = {}
        # print('manifest constructed with path {}'.format(self.filepath))
        # TODO: CATCH EXCEPTIONS
        try:
            with open(filepath, encoding='utf8') as manifest_file:
                json_data = json.load(manifest_file)
        except FileNotFoundError:
            # print('Creating manifest')
            # Create manifest and write blank json file
            with open(filepath, 'a', encoding='utf8') as manifest_file:
                manifest_file.write(r'{"posts":{}}')
