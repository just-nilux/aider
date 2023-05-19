import os
import json
import sys
import subprocess

# from aider.dump import dump


def get_tags_map(filenames, root_dname=None):
    if not root_dname:
        root_dname = os.getcwd()

    tags = []
    for filename in filenames:
        tags += get_tags(filename, root_dname)
    if not tags:
        return

    tags = sorted(tags)

    output = ""
    last = [None] * len(tags[0])
    tab = " "
    for tag in tags:
        tag = list(tag)
        common_prefix = [tag_i for tag_i, last_i in zip(tag, last) if tag_i == last_i]
        num_common = len(common_prefix)
        indent = tab * num_common
        rest = tag[num_common:]
        for item in rest:
            output += indent + item + "\n"
            indent += tab
        last = tag

    return output


def split_path(path, root_dname):
    path = os.path.relpath(path, root_dname)
    path_components = path.split(os.sep)
    res = [pc + os.sep for pc in path_components[:-1]]
    res.append(path_components[-1])
    return res


def get_tags(filename, root_dname):
    yield split_path(filename, root_dname)

    cmd = ["ctags", "--fields=+S", "--output-format=json", filename]
    output = subprocess.check_output(cmd).decode("utf-8")
    output = output.splitlines()

    for line in output:
        tag = json.loads(line)
        path = tag.get("path")
        scope = tag.get("scope")
        kind = tag.get("kind")
        name = tag.get("name")
        signature = tag.get("signature")

        last = name
        if signature:
            last += " " + signature

        res = split_path(path)
        if scope:
            res.append(scope)
        res += [kind, last]

        yield res


if __name__ == "__main__":
    res = get_tags_map(sys.argv[1:])
    print(res)