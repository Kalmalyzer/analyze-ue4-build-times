
import json
import logging
import os.path
import unittest

logger = logging.getLogger(__name__)

from src.build_graph import create_build_graph, Module

class TestBuildGraph(unittest.TestCase):

    def test_create_small_build_graph(self):

        build_graph_json = None
        with open(os.path.join(os.path.dirname(__file__), 'small_build_graph.json'), 'rt') as json_file:
            build_graph_json = json.load(json_file)

        build_graph = create_build_graph(build_graph_json)

        self.assertEqual(len(build_graph_json["Binaries"]), len(build_graph))

        # Ensure build graph contains the expected binary items

        build_graph_list = list(build_graph)
        build_settings_binary = next(binary for binary in build_graph_list if "UE4Editor-BuildSettings" in binary.name)
        trace_log_binary = next(binary for binary in build_graph_list if "UE4Editor-TraceLog" in binary.name)
        core_binary = next(binary for binary in build_graph_list if "UE4Editor-Core" in binary.name)
        self.assertTrue(build_settings_binary)
        self.assertTrue(trace_log_binary)
        self.assertTrue(core_binary)

        # Ensure build graph contains the expected module items

        core_module = next(module for module in core_binary.modules if "Core" in module.name)
        zlib_module = next(module for module in core_binary.modules if "zlib" in module.name)
        intel_tbb_module = next(module for module in core_binary.modules if "IntelTBB" in module.name)
        intel_vtune_module = next(module for module in core_binary.modules if "IntelTBB" in module.name)
        icu_module = next(module for module in core_binary.modules if "ICU" in module.name)
        self.assertTrue(core_module)
        self.assertTrue(zlib_module)
        self.assertTrue(intel_tbb_module)
        self.assertTrue(intel_vtune_module)
        self.assertTrue(icu_module)
        self.assertEqual(5, len(core_binary.modules))

        build_settings_module = next(module for module in build_settings_binary.modules if "BuildSettings" in module.name)
        self.assertTrue(build_settings_module)
        self.assertEqual(1, len(build_settings_binary.modules))

        trace_log_module = next(module for module in trace_log_binary.modules if "TraceLog" in module.name)
        self.assertTrue(trace_log_module)
        self.assertEqual(1, len(trace_log_binary.modules))

        # Ensure modules are of the right type

        self.assertEqual(Module.Type.CPlusPlus, core_module.type)
        self.assertEqual(Module.Type.External, zlib_module.type)
        self.assertEqual(Module.Type.External, intel_tbb_module.type)
        self.assertEqual(Module.Type.External, intel_vtune_module.type)
        self.assertEqual(Module.Type.External, icu_module.type)
        self.assertEqual(Module.Type.CPlusPlus, build_settings_module.type)
        self.assertEqual(Module.Type.CPlusPlus, trace_log_module.type)

        # Ensure build binary dependencies are set appropriately

        self.assertEqual(1, len(build_settings_binary.dependencies))
        self.assertEqual(1, len(trace_log_binary.dependencies))
        self.assertEqual(3, len(core_binary.dependencies))

        self.assertTrue(any("UE4Editor-BuildSettings.lib" in action.name for action in build_settings_binary.dependencies))

        self.assertTrue(any("UE4Editor-TraceLog.lib" in action.name for action in trace_log_binary.dependencies))

        self.assertTrue(any("UE4Editor-BuildSettings.lib" in action.name for action in core_binary.dependencies))
        self.assertTrue(any("UE4Editor-TraceLog.lib" in action.name for action in core_binary.dependencies))
        self.assertTrue(any("UE4Editor-Core.lib" in action.name for action in core_binary.dependencies))

    def test_create_large_build_graph(self):

        build_graph_json = None
        with open(os.path.join(os.path.dirname(__file__), 'UE4Editor.json'), 'rt') as json_file:
            build_graph_json = json.load(json_file)

        build_graph = create_build_graph(build_graph_json)

        # Ensure the build graph contains the appropriate number of binaries

        self.assertEqual(len(build_graph_json["Binaries"]), len(build_graph))

        # Ensure each binary in the build graph has a name

        for binary in build_graph:
            self.assertIsNotNone(binary.name, 'Binary has a None name: %s' % (binary,))

        # Ensure each binary in the build graph has at least one module

        for binary in build_graph:
            self.assertNotEqual(0, len(binary.modules), 'Binary %s has an empty module ref list: %s' % (binary.name, binary))

        # Ensure each dependency in the build graph is nonzero

        for binary in build_graph:
            for action in binary.dependencies:
                self.assertIsNotNone(action, 'Binary %s has a None ref in its dependency list: %s' % (binary.name, binary))

if __name__=='__main__':
    unittest.main()
