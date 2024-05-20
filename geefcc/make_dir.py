"""Make new directory."""

import os


def make_dir(newdir):
    """Make new directory.

        * Already exists, silently complete.
        * Regular file in the way, raise an exception.
        * Parent directory(ies) does not exist, make them as well.

    :param newdir: Directory path to create.

    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError(
            ("A file with the same name as the desired "
             f"dir, '{newdir}', already exists.")
        )
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            make_dir(head)
        # print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)
