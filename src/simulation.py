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

    processed_binaries = set()
    remaining_binaries = build_graph.copy()

    while len(remaining_binaries) > 0:

        binary = find_next_binary_to_build(processed_binaries, remaining_binaries)

        if binary == None:
            logger.info("")
            logger.info("No binary is available to be built. Remaining binaries:")
            for binary2 in remaining_binaries:
                logger.info("  %s" % (binary2.name,))
                unfulfilled_dependencies = binary2.dependent_binary_import_libraries.intersection(remaining_binaries)
                for binary3 in unfulfilled_dependencies:
                    logger.info("     Depends on: %s" % (binary3.name,))
            return

        logger.info("Building binary %s" % binary.name)

        remaining_binaries.remove(binary)
        processed_binaries.add(binary)
