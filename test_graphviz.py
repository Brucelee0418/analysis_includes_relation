from graphviz import Digraph
import os
import re


class AnalysisIncludes(object):
    module_includes = {}
    root_path = ""
    pattern = re.compile(r'include[\s]*["<]([\w\.]*)[">]')

    def __init__(self, root_path):
        self.root_path = root_path

    def get_module_includes(self):
        for root, _, files in os.walk(self.root_path):
            for file in files:
                (module, ext) = os.path.splitext(file)
                if ext in [".h", ".c", ".cpp"]:
                    includes = self.get_includes(root, file)
                    if module not in self.module_includes.keys():
                        self.module_includes[module] = includes
                    else:
                        self.module_includes[module] |= includes
                    if module in self.module_includes[module]:
                        self.module_includes[module].remove(module)

    def get_includes(self, root, file):
        includes = set()
        file_path = os.path.join(root, file)
        with open(file_path, encoding="utf-8", errors="ignore") as lines:
            for line in lines:
                result = self.pattern.findall(line)
                if result:
                    (name, _) = os.path.splitext(result[0])
                    includes.add(name)
        # print("includes: " + str(includes))
        return includes

    def generate_label(self, module):
        label = "<%s> module %s" % (module, module)
        for include in self.module_includes[module]:
            label += " | <%s> %s;" % (include, include)
        return label

    def generate_includes_graph(self):
        g = Digraph("Includes Graph", format="png")
        g.attr(rankdir="LR", ranksep=".75", pad="1", margin="0,0")
        g.attr(
            "node",
            shape="record",
            charset="UTF-8",
            fontname="Microsoft YaHei",
            fontsize="14",
        )
        g.attr(
            "edge",
            style="dashed",
            charset="UTF-8",
            fontname="Microsoft YaHei",
            fontsize="11",
        )
        for module in self.module_includes:
            g.node(name=module, label=self.generate_label(module))
        for module in self.module_includes:
            for include in self.module_includes[module]:
                if include in self.module_includes.keys():
                    g.edge(module + ":" + include, include + ":" + include)
        g.save()
        g.render()


if __name__ == "__main__":
    ais = AnalysisIncludes(os.getcwd())
    ais.get_module_includes()
    ais.generate_includes_graph()
    print("finish!")
