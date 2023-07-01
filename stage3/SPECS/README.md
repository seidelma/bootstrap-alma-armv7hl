# Stage 3 RPM Specfiles
This directory contains RPM specfiles with modifications necessary to get stage3 built (and Mock working correctly for stage 4). Typically this involves excluding documentation, turning off optional features, or preventing installation of unnecessary files (like emacs lisp integration). If a file exists in this directory for a package in stage 3, it will automatically be used over the vanilla specfile.

# Viewing changes
The process for adding specfiles to this repo is as follows:
 - Copy the vanilla specfile and `git add`; `git commit`
 - Iterate on changes to the spec and rebuild the package until it is tested and works
 - `git add`; `git commit` the changes.

Therefore, a `git blame <filename>` should show exactly what's changed between vanilla and stage3 versions.
