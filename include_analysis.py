import os
import re
from dataclasses import dataclass

import matplotlib.pyplot as plt
import networkx as nx

import config


@dataclass
class Dependency:
    name: str
    system: bool
    abs_path: str = None


class DependencyAnalyze:

    def __init__(self, project_root):
        self.dependencies = {}
        self.scan_source_files(project_root)
        self.parse_all_include_path()

    def non_self_contained_header(self):
        """
        扫描源代码文件的头文件依赖，将源代码中引入的头文件同步添加到后面引入的头文件的include中
        :return:
        """
        extra_includes = {}
        for src, all_includes in self.dependencies.items():
            _, ext = os.path.splitext(src)
            if ext not in config.source_ext:
                continue
            has_includes = []
            for cur_include in all_includes:
                if cur_include.system:
                    continue
                added = extra_includes.setdefault(cur_include.abs_path, [])
                for hicld in has_includes:
                    if hicld in self.get_includes_recursive(cur_include.abs_path):
                        print(f'需添加 {hicld}')
                    else:
                        added.append(hicld)
                        print(f'源文件 {src}')
                        print(f'头文件 {cur_include.name}')
                        print(f'已引入 {has_includes}')
                        print(f'需添加 {hicld}')
                        print(f'===========')

                has_includes.append(cur_include.abs_path)
        return extra_includes

    def create_whole_include_graph(self):
        """
        创建整个项目的头文件依赖图，不包括系统头文件
        :return:
        """
        G = nx.DiGraph()
        for src, includes in self.dependencies.items():
            G.add_node(src)
            for icd in includes:
                if icd.system:
                    continue
                G.add_node(icd.abs_path)
                G.add_edge(src, icd.abs_path)
        return G

    def create_include_graph(self, from_file, g=nx.DiGraph()):
        """
        创建给定文件的头文件依赖图，不包括系统头文件
        :param from_file:
        :param g:
        :return:
        """
        from_file = os.path.abspath(from_file)
        g.add_node(from_file)
        for icd in self.dependencies[from_file]:
            if icd.system:
                continue
            g.add_node(icd.abs_path)
            g.add_edge(from_file, icd.abs_path)
            self.create_include_graph(icd.abs_path, g)
        return g

    def get_includes_recursive(self, file, result=[]):
        """
        递归获取文件依赖的所有头文件（排除系统头文件）
        :param file:
        :param result:
        :return: 头文件列表
        """
        file = os.path.abspath(file)
        for icd in self.dependencies[file]:
            if icd.system:
                continue
            result.append(icd)
            self.get_includes_recursive(icd.abs_path, result)
        return result

    @staticmethod
    def draw_dependency(graph):
        # layout = nx.spring_layout(graph)
        nx.draw(graph, with_labels=True)
        plt.show()

    @staticmethod
    def find_loop(graph):
        return list(nx.simple_cycles(graph))

    def scan_source_files(self, path):
        """
        扫描项目源文件，生成源文件->依赖头文件 的字典
        :param path: 要扫描的目录
        :return:
        """
        for root, dirs, files in os.walk(path):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext not in config.source_ext + config.include_ext:
                    continue
                src_path = os.path.abspath(os.path.join(root, file))
                includes = self.parse_source_file(src_path)
                self.dependencies[src_path] = includes
            for d in dirs:
                self.scan_source_files(d)

    def parse_source_file(self, path):
        """
        解析给定源文件的include依赖
        :param path: 源文件路径
        :return:
        """
        with open(path, 'r') as f:
            includes = []
            data = f.read()
            for x in re.finditer(r'\s*#include\s+(("(\w+(\.\w+)?)")|(<(\w+(\.\w+)?)>))', data):
                ext_include = x.group(3)
                sys_include = x.group(6)
                if ext_include:
                    includes.append(Dependency(ext_include, False))
                if sys_include:
                    includes.append(Dependency(sys_include, True))
            return includes

    def parse_all_include_path(self):
        """
        解析整个项目中源文件的include依赖关系
        :return:
        """
        for src, includes in self.dependencies.items():
            for include in includes:
                self.parse_includes_to_abspath(include)

    def parse_includes_to_abspath(self, include: Dependency):
        """
        将头文件依赖路径解析为绝对路径
        :param include: 待解析的头文件依赖
        :return:
        """
        for base in config.project_include_paths:
            path = os.path.join(config.project_root, base, include.name)
            abs_include = os.path.abspath(path)
            if abs_include in self.dependencies.keys():
                include.abs_path = abs_include


if __name__ == '__main__':
    ana = DependencyAnalyze(config.project_root)
    # ana.draw_dependency(ana.create_include_graph(from_file=r'D:\code\workflow-0.10.4\src\server\WFServer.cc'))
    # ana.draw_dependency(ana.create_include_graph(r'D:\code\workflow-0.10.4\src\algorithm\DnsRoutine.cc'))
    dep = ana.get_includes_recursive(r'D:\code\workflow-0.10.4\src\algorithm\DnsRoutine.cc')
    dep = ana.non_self_contained_header()
    print(dep)
