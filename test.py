import unittest

import config
from include_analysis import DependencyAnalyze


class Test(unittest.TestCase):

    def setUp(self):
        self.an = DependencyAnalyze(config.project_root)

    def test1(self):
        self.an.draw_dependency(
            self.an.create_include_graph(r'D:\code\workflow-0.10.4\src\server\WFServer.cc'))

    def test2(self):
        self.an.draw_dependency(
            self.an.create_whole_include_graph())

    def test3(self):
        dep = self.an.get_includes_recursive(r'D:\code\workflow-0.10.4\src\server\WFServer.cc')
        for d in dep:
            print(d)

    def test4(self):
        dep = self.an.non_self_contained_header()
        for d in dep.items():
            print(d)


if __name__ == '__main__':
    unittest.main()
