from tree_sitter import Language, Parser
from pathlib import Path
import yaml


Language.build_library(
  # Store the library in the `build` directory
  'build/my-languages.so',

  # Include one or more languages
  [
    'vendor/tree-sitter-python'
  ]
)

PY_LANGUAGE = Language('build/my-languages.so', 'python')

parser = Parser()
parser.set_language(PY_LANGUAGE)


class ParsedComponent():
    def __init__(self, info):
        self.component_identifier = info.get('identifier')
        self.props = info.get('props')
        self.description = info.get('description')
        self.methods = {'methods': {k:v for k,v in zip(info.get('methods'), info.get('method_arguments'))}} if info.get('methods') is not None else None

    def to_dict(self):
        return {self.component_identifier: {
            'description': self.description,
            'props': self.props,
            'methods': self.methods,
        }}


query_scm = '''
(class_definition
  name: (identifier) @ComponentName
  (block
      (
          (expression_statement) @ComponentDescription
          (#match? @ComponentDescription "^(?:(?![:=]).)*$")
          (expression_statement) @Prop
          (#match? @Prop "(\w*:\w*)")
          (decorated_definition
          (function_definition
           name: (identifier) @Method
           parameters: (parameters) @MethodArguments))* 
      )
  )
)
(class_definition
  name: (identifier) @ComponentName
  (block
      (
          (expression_statement) @Prop
          (#match? @Prop "(\w*:\w*)")
          (decorated_definition
          (function_definition
           name: (identifier) @Method
           parameters: (parameters) @MethodArguments))* 
      )
  )
)

(class_definition
  name: (identifier) @ComponentName
  (block
      (
          (expression_statement) @ComponentDescription
          (#match? @ComponentDescription "^(?:(?![:=]).)*$")
          (decorated_definition
          (function_definition
           name: (identifier) @Method
           parameters: (parameters) @MethodArguments))*
      )
  )
)
  '''


def deduplicate(captures: list):
    temp_list = captures[:]
    for index, capture in enumerate(temp_list):
        if capture in temp_list[index+1:]:
            captures.remove(capture)


def components_from_captures(captures):
    captures = list(captures)
    deduplicate(captures)
    info = {}
    components = []
    for node, type in captures:
        node_text = node.text.decode().replace('\n', '').strip()
        if type == 'ComponentName':
            if len(info) > 0:
                components.append(ParsedComponent(info))
                info.clear()
            info['identifier'] = node_text
        elif type == 'ComponentDescription':
            info['description'] = node_text
        elif type == 'Prop':
            info.setdefault('props', []).append(node_text)
        elif type == 'Method':
            info.setdefault('methods', []).append(node_text)
        elif type == 'MethodArguments':
            info.setdefault('method_arguments', []).append(node_text)
        else:
            raise ValueError(f"Unkown type : {type}")
        # print(node.text[:100], node.type, type)

    if len(info) > 0:
        components.append(ParsedComponent(info))
        info.clear()
    return components


def parse_code(code):
    tree = parser.parse(bytes(code, "utf8"))
    query = PY_LANGUAGE.query(query_scm)
    captures = query.captures(tree.root_node)
    components = components_from_captures(captures)
    return [component.to_dict() for component in components]


def generate_yaml_file(components, glob):
    with open(f'skeletons/{glob.parent}/{glob.name.replace(".py", ".yaml")}', 'w') as f:
        yaml.dump(components, f)


def create_yaml_files():
    components_dir = Path('nextpy/components')
    for glob in components_dir.rglob("*.py"):
        print(f'started parsing {glob}')
        base_path = Path(f'skeletons/{glob.parent}')
        base_path.mkdir(parents=True, exist_ok=True)
        code = glob.read_text()
        components = parse_code(code)
        generate_yaml_file(components, glob)
        print(f'finished parsing {glob}')


if __name__ == '__main__':
    create_yaml_files()