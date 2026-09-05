import argparse
import re
import sys
from abc import ABC, abstractmethod

class BaseFile(ABC):
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self._load()

    @abstractmethod
    def _load(self):
        pass

    def read(self):
        return self.data


class ConfigFile(BaseFile):

    def __init__(self, file_path):
        super().__init__(file_path)

    def _load(self):
        self.data = [] # should be a list of tuples.

        try:
            with open(self.file_path, 'r') as f:
                for line in f:
                    line = line.strip()

                    if '=' in line:
                        key, value = line.split('=')
                        self.data.append((key.strip(), value.strip()))
        except FileNotFoundError as e:
            print(f"Error: The file '{self.file_path}' was not found.")
            raise e
        except Exception as e:
            print(f"Something went wrong while reading '{self.file_path}' file: {e}")
            raise e

    def get_config(self):
        return self.data

class TextFile(BaseFile):

    def __init__(self, file_path):
        super().__init__(file_path)

    def _load(self):
        self.data = [] # should be a list of strings.

        try:
            with open(self.file_path, 'r') as f:
                self.data = [line.strip('\n') for line in f]
        except FileNotFoundError as e:
            print(f"Error: The file '{self.file_path}' was not found.")
            raise e
        except Exception as e:
            print(f"Something went wrong while reading '{self.file_path}' file: {e}")
            raise e

    def get_text_lines(self):
        return self.data


    def replace_non_overlapping(self, config):
        results = []
        
        sorted_config = sorted(config, key=lambda x: len(x[0]), reverse=True)
        
        pattern = '|'.join(re.escape(key) for key, _ in sorted_config)
        
        def replace_match(match):
            matched = match.group(0)
            for key, value in sorted_config:
                if matched == key:
                    return value
            return matched
        
        for line in self.data:
            new_line = re.sub(pattern, replace_match, line)
            
            total_replaced = 0
            for key, _ in sorted_config:
                count = len(re.findall(re.escape(key), line))
                total_replaced += count * len(key)
            
            results.append((new_line, total_replaced))
        
        return results

    @staticmethod
    def sort_by_replaced_symbol_count(results, reverse=True):
        
        return sorted(results, key=lambda x: x[1], reverse=reverse)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config', dest='config_file', required=True, help='A configuration file')
    parser.add_argument('-t', '--text', dest='text_file', required=True, help='A text file')

    return parser.parse_args()

def main():

    args = parse_arguments()
    try:
        conf_file = ConfigFile(args.config_file)
    except Exception as e:
        print(f"Error occurred while initializing ConfigFile: {e}")
        sys.exit()

    config = conf_file.get_config()

    try:
        text_file = TextFile(args.text_file)
    except Exception as e:
        print(f"Error occurred while initializing TextFile: {e}")
        sys.exit()

    replaced_results = text_file.replace_non_overlapping(config)
    
    sorted_results = text_file.sort_by_replaced_symbol_count(replaced_results)

    print([item[0] for item in sorted_results])

main()
