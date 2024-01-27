import re

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


def get_quotes(src_file, collect_errors=False, fix_timestring_case=False):
    with open(src_file, newline='\n', encoding="utf8") as yaml_file:
        result = yaml.safe_load(yaml_file)

    exceptions = []
    expected_keys = ['author', 'quote', 'timestring', 'title']
    for t, datasets in result.items():
        for dataset in datasets:
            for key in expected_keys:
                if key not in dataset:
                    e = Exception(f"Missing key in {dataset} (expected {expected_keys})")
                    if collect_errors:
                        exceptions.append(e)
                    else:
                        raise e

            timestring, quote = dataset['timestring'], dataset['quote']
            if timestring not in quote:
                if fix_timestring_case:
                    search_result = re.search(timestring, quote, re.IGNORECASE)
                    if search_result:
                        dataset['timestring'] = search_result.group()
                else:
                    e = Exception(f"Timestring '{timestring}' not found in quote '{quote}'")
                    if collect_errors:
                        exceptions.append(e)
                    else:
                        raise e

    if not exceptions or fix_timestring_case:
        return result

    es = '\n'.join([str(e) for e in exceptions])
    raise Exception(f"{len(exceptions)} Errors in quotes:\n{es}")

def minute_to_timestr(minute: int):
    h, m = divmod(minute, 60)
    return f"{h:02d}:{m:02d}"
