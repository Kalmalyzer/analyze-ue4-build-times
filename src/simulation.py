import logging

logger = logging.getLogger(__name__)

def can_binary_be_built(processed_binaries, remaining_binaries, binary):
    return binary.dependent_binary_import_libraries.isdisjoint(remaining_binaries)

def find_next_binary_to_build(processed_binaries, remaining_binaries):

    for binary in remaining_binaries:
        if (can_binary_be_built(processed_binaries, remaining_binaries, binary)):
            return binary

    return None

def simulate_build(build_graph):

    # for binary in build_graph:
    #     if ("Core" in binary.name):
    #         print(binary)

    processed_binaries = set()
    remaining_binaries = build_graph.copy()

    while len(remaining_binaries) > 0:

        binary = find_next_binary_to_build(processed_binaries, remaining_binaries)

        logger.info("Building binary %s" % binary.name)

        remaining_binaries.remove(binary)
        processed_binaries.add(binary)
