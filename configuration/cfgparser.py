import yaml

def load_config(fname):
    with open(fname, 'r') as config_file:
        config = yaml.safe_load(config_file)
    return config

def print_all_cfg(data, indent=0):
    """
    Recursively prints all keys and values in the YAML data.
    """
    for key, value in data.items():
        # Handle indentation
        print('  ' * indent + f"{key}: ", end='')

        if isinstance(value, dict):
            print()  # Print key and go deeper for nested dict
            print_all_cfg(value, indent + 1)
        else:
            print(f"{value}")  # Print key and value if not a dict

if __name__ == '__main__':

    # Example usage:
    config = load_config('pipeline.yaml')
    print_all_cfg(config)
