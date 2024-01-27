import yaml


class Quote(str):
    pass


def write_yaml(content, dst_file):
    # mark quotes
    def mark_quote(d):
        d['quote'] = Quote(d['quote'])
        return d

    for t, elms in content.items():
        content[t] = [mark_quote(item) for item in elms]

    def quote_presenter(dumper, data):
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='>')

    yaml.add_representer(Quote, quote_presenter)

    with open(dst_file, 'w') as yaml_file:
        yaml.dump(content, yaml_file, allow_unicode=True)


def get_quotes(src_file):
    with open(src_file, newline='\n', encoding="utf8") as yaml_file:
        result = yaml.safe_load(yaml_file)

    expected_keys = ['author', 'quote', 'timestring', 'title']
    for t, datasets in result.items():
        for dataset in datasets:
            for key in expected_keys:
                if key not in dataset:
                    raise Exception(f"Error: missing key in {dataset} (expected {expected_keys})")

            timestring, quote = dataset['timestring'], dataset['quote']
            if timestring not in quote:
                raise Exception(f"Error: timestring '{timestring}' not found in quote '{quote}'")

    return result
