import yaml


class SingleSource(yaml.YAMLObject):
    yaml_tag = "!explicit"

    def __init__(self, val):
        self.val = val

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)


class SingleSourceOld(yaml.YAMLObject):
    yaml_tag = "!single_source"

    def __init__(self, val):
        self.val = val

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)


class ReadGrid(yaml.YAMLObject):
    yaml_tag = "!read"

    def __init__(self, val):
        self.val = val

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)


class ConstructGrid(yaml.YAMLObject):
    yaml_tag = "!construct"

    def __init__(self, val):
        self.val = val

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)


class FromIcs(yaml.YAMLObject):
    yaml_tag = "!from_ics"

    def __init__(self, val):
        self.val = val

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)
