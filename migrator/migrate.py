#!/usr/bin/env python

# stdlib
import sys
import os
import time
import zipfile
import tempfile
import shutil
import re

# clint
from clint.textui import puts, indent, colored
from clint.textui.cols import console_width
from clint.arguments import Args

def migrate(argv = sys.argv):
    args = Args(argv)

    puts(colored.blue(
        "This program will guide you through migrating your Cloud 9 workspace "
        "onto the school's servers."))
    puts()

    # Try to figure out if we're on one of the lab machines. It is unlikely
    # that someone would have their user's home directory mounted on their
    # local system.
    home_path = os.environ["HOME"]
    if "--force-on-lab" not in args and not os.path.ismount(home_path):
        raise RuntimeError("You are not on a lab machine.")

    downloads = lambda: os.listdir(os.path.join(os.environ["HOME"],
        "Downloads"))
    if "--use-old-zip" not in args and "cs010_assignments.zip" in downloads():
        puts(colored.red("You have an old cs010_assignments.zip file in your "
            "downloads directory, delete it."))
        puts()

        puts("Waiting...", newline = False)
        while "cs010_assignments.zip" in downloads():
            sys.stdout.flush()
            time.sleep(4)
            puts(".", newline = False)
        puts(" Done.")

    puts(colored.blue(
        "The first thing you need to do is download your entire Cloud 9 "
        "workspace. To do this..."))
    with indent(4):
        puts("1. Go into your private workspace: " +
            colored.green("cs010_assignments"))
        puts("2. Click File->Download Project")
        puts("3. Make sure it saves into your Downloads folder as "
            + colored.green("cs010_assignments.zip"))
    puts()

    puts("Waiting...", newline = False)
    while "cs010_assignments.zip" not in downloads():
        sys.stdout.flush()
        time.sleep(4)
        puts(".", newline = False)
    puts(" Done.")

    # Inspect the zip file and make sure the assignments are there.
    zip_path = os.path.join(home_path, "Downloads", "cs010_assignments.zip")
    zipped = zipfile.ZipFile(zip_path)
    desired_files = ["assignment0%d/" % (i, ) for i in xrange(10)] + \
        ["assignment10/"]
    if "--ignore-bad-zip" not in args and \
            not all(i in zipped.namelist() for i in desired_files):
        puts(colored.red("Files in zip file: " + str(zipped.namelist())))
        raise RuntimeError("Bad zip file found.")
    zipped.close()

    # Make a backup of the zip file
    backup_file = tempfile.NamedTemporaryFile(prefix = "assignments-backup",
        dir = home_path, delete = False)
    shutil.copyfileobj(open(zip_path, "rb"), backup_file)
    puts(colored.green("Created backup of assignments at " + backup_file.name))
    puts()
    backup_file.close()

    puts(colored.blue(
        "Now you have to delete your private workspace on Cloud 9."))
    with indent(4):
        puts("1. Click your cs010_assignments workspace.")
        puts("2. Click delete on the right middle of the page.")
        puts(colored.red("Note that we're ONLY delete the one private "
            "workspace, no others."))
    puts()

    while raw_input("Have you done this? [y/n]: ") != "y":
        pass
    puts()

    puts(colored.blue("Now you must create your new workspace."))
    with indent(4):
        puts("1. Click Create New Workspace->Create New Workspace")
        puts("2. Select SSH (has a little red beta above it)")
        puts("3. Type " + colored.green("hammer.cs.ucr.edu") +
            " for the hostname")
        puts("4. Type your UCR username (ex: mine is jsull003)")
        puts("5. Copy and paste all of the text under " +
            colored.green("Your SSH key") + " into the prompt below")
    puts()

    KEY_RE = re.compile("ssh-rsa \S{300,} [A-Za-z0-9]+@*.")
    while True:
        ssh_key = raw_input("Paste Your SSH Key: ").strip()
        if "--ignore-bad-key" not in args and KEY_RE.match(ssh_key) is None:
            puts(colored.red("This is not your SSH key, try again."))
        else:
            break

    key_path = "/extra/si/%s/pub.key" % (os.environ["LOGNAME"], )
    open(key_path, "wb").write(ssh_key + "\n")
    puts(colored.blue("All done! Key saved to " + key_path))

def main():
    try:
        migrate()
    except Exception as e:
        puts(colored.red(str(e)))
        puts(colored.red("-" * console_width({})))
        raise

if __name__ == "__main__":
    main()
