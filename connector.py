from itermore import pairwise
from collections import deque

def connect_paths(root, paths, namespaces):
    open_start = dict()
    open_end = dict()
    closed = set()

    for i, e in enumerate(root.iterfind(paths, namespaces=namespaces)):
        path = deque(pairwise(map(float, e.text.split())))
        start, end = path[0], path[-1]

        # If the start is in open_start, we must reverse its orientation
        if start in open_start:
            path.reverse()
            start, end = end, start

        # If the other endpoint is also in open_start, we must reverse its orientation too.
        if start in open_start:
            o_path = open_start[start]
            o_path.reverse()
            path_start, path_end = o_path[-1], o_path[0]

            # This should not overwrite open_end, as it would've been detected when we initially connected the segment.
            open_end[path_end] = open_start.pop(path_end)
            open_start[path_start] = open_end.pop(path_start)

        # First we check if the endpoints are open_start and open_end
        # Note that we have corrected the orientation.
        if end in open_start and start in open_end:
            if open_start[end] == open_end[start]: # loop found
                closed.add(tuple(open_end[start] + path))
            else: #not loop
                open_end[start].extend(path)
                open_end[start].extend(open_start[end])
                open_end[open_end[start][-1]] = open_end[start]

            del open_end[start]
            del open_start[end]
            continue

        # Then we check if endpoints are in open_start or open_end
        # This can hypothetically be merged with the above <and>-closure
        if end in open_start:
            path.reverse() #fuck you deque
            open_start[end].extendleft(path)
            open_start[start] = open_start[end]
            del open_start[end]
            continue

        if start in open_end:
            open_end[start].extend(path)
            open_end[end] = open_end[start]
            del open_end[start]
            continue

        # If the endpoints don't exist already, we either add them to loops or open paths
        if start == end:
            closed.add(tuple(path))
        else:
            open_start[start] = open_end[end] = path

    # open_start and open_end should contain the same objects
    open_ = tuple(open_start.values())

    return closed, open_
