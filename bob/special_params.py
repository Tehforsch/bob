import yaml


class SingleSource(yaml.YAMLObject):
    yaml_tag = "!single_source"

    def __init__(self, val):
        self.val = val

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)
