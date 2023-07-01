import os
import pickle
import subprocess
import sys

DEBUG_ENABLED = False

OPTION_REQUIRES  = '--requires'
OPTION_PROVIDES  = '--provides'

OPTION_NOSIGS    = '--nosignature'
OPTION_LISTFILES = '--list'

OPTION_QUERY_INSTALLED  = '-qa'
OPTION_QUERY_PKGFILE    = '-qp'

RPM_COMMAND         = '/usr/bin/rpm'

SRCREQS_PICKLEFILE  = 'srcreqs.pickle'
SRCPROVS_PICKLEFILE = 'srcprovs.pickle'

STAGE3_PICKLEFILE   = 's3provs.pickle'

SRCREPO    = '/mnt/alma/src/all'
STAGE3REPO = '/mnt/alma/stage3/rpms'
STAGE4REPO = '/mnt/alma/mock-stage4/rpms'

def load_from_pickle(picklefile):
    with open(picklefile, 'rb') as f:
        return pickle.load(f)

def save_to_pickle(data, picklefile):
    with open(picklefile, 'wb') as f:
        pickle.dump(data, f)

def print_debug(dbg: str):
    if DEBUG_ENABLED:
        print(dbg)

def get_all_packages_in_repo(repo_root: str) -> list:
    pkgs = []
    for root, dirs, files in os.walk(repo_root):
        for name in files:
            # Not ideal, but I don't feel like relying on file-magic being installed
            if name[-4:] == '.rpm':
                pkgs.append(os.path.join(root, name))
        for name in dirs:
            pass
    return pkgs

def get_dependencies_by_packages(pkgs: list,
                                 deptype: str,
                                 include_files: bool=True) -> dict:
    deps_by_pkg = {}
    for pkg in pkgs:
        print_debug(f"Getting {deptype} dependencies for {pkg}:")
        deps = get_package_dependencies(pkg, deptype, include_files)
        print_debug(f"    {deps}")
        deps_by_pkg[pkg] = deps
    return deps_by_pkg

def package_requirements_satisfied(pkg_reqs: list, provides_avail: list) -> bool:
    satisfied = True
    for req in pkg_reqs:
        if req not in provides_avail:
            print_debug(f"Requirement not available: {req}")
            satisfied = False
    return satisfied

def get_package_dependencies(pkg_path: str, deptype: str, include_files: bool=True) -> list:
    """Return a list of dependencies and files provided or
     required by a given source/binary RPM"""
    if not os.path.exists(pkg_path):
        raise FileNotFoundError(pkg_path)
    args = [RPM_COMMAND, OPTION_QUERY_PKGFILE, deptype, OPTION_NOSIGS, pkg_path]
    if include_files:
        args.append(OPTION_LISTFILES)
    p = subprocess.Popen(args=args, stdout=subprocess.PIPE)
    return _parse_rpm_output(p.stdout.read())

def get_repo_dependencies(repo_path: str, deptype: str, include_files: bool=True) -> list:
    """Return a list of dependencies and files provided or
     required by a whole repo path"""
    if not os.path.exists(repo_path):
        raise FileNotFoundError(repo_path)
    out = []
    for root, dirs, files in os.walk(repo_path):
        for name in files:
            if name[-4:] == '.rpm':
                out += get_package_dependencies(os.path.join(root, name),
                                                deptype,
                                                include_files)
    return out

def get_system_dependencies(deptype: str, include_files: bool=True) -> list:
    """Return a list of dependencies and files provided or required
    by the installed packages in the system"""
    args = [RPM_COMMAND, OPTION_QUERY_INSTALLED, OPTION_NOSIGS, deptype]
    if include_files:
        args.append(OPTION_LISTFILES)
    p = subprocess.Popen(args=args, stdout=subprocess.PIPE)
    return _parse_rpm_output(p.stdout.read())

def _parse_rpm_output(obytes: bytes) -> list:
    s = obytes.decode()
    # Last element is empty so remove it
    l = s.split('\n')[:-1] 
    # Strip off versions of things; this is all from RHEL 9 so we know
    #  that the versions are compatible
    # We also know all packages require rpmlib stuff, you're not interesting
    out = []
    for elem in l:
        print_debug("checking element: " + elem)
        if elem[:6] != 'rpmlib':
            print_debug("appending element: " + elem.split(' ')[0])
            out.append(elem.split(' ')[0])
    return out 

if __name__ == "__main__":
    # Source dependency data doesn't change,
    #  and can take several minutes to generate,
    #  so only do it once
    src_pkgs = get_all_packages_in_repo(SRCREPO)
    srcreqs = []
    srcprovs = []
    if (os.path.exists(SRCREQS_PICKLEFILE) and 
            os.path.exists(SRCPROVS_PICKLEFILE)):
        srcreqs  = load_from_pickle(SRCREQS_PICKLEFILE)
        srcprovs = load_from_pickle(SRCPROVS_PICKLEFILE)
    if (len(srcreqs) == len(src_pkgs) and
            len(srcprovs) == len(src_pkgs)):
        print_debug(f"Source package pickles ok, package count: {len(src_pkgs)}") 
    else:
        print(f"Source repo size ({len(src_pkgs)}) differs from "
              f"picklefile size ({len(srcreqs)}), recalculating",
              file=sys.stderr)
        srcreqs  = get_dependencies_by_packages(src_pkgs, OPTION_REQUIRES, include_files=False)
        srcprovs = get_dependencies_by_packages(src_pkgs, OPTION_PROVIDES, include_files=False)
        save_to_pickle(srcreqs, SRCREQS_PICKLEFILE)
        save_to_pickle(srcprovs, SRCPROVS_PICKLEFILE)

    s3_pkgs = get_all_packages_in_repo(STAGE3REPO)
    s3provs_by_pkg = {}
    s3provs = []
    s4provs = []

    if os.path.exists(STAGE3_PICKLEFILE):
        s3provs_by_pkg = load_from_pickle(STAGE3_PICKLEFILE)


    print_debug(f"Checking stage3 pickle package count")
    if (len(s3_pkgs) > 0 and (len(s3_pkgs) == len(s3provs_by_pkg))):
        for pkg in s3provs_by_pkg:
            s3provs += s3provs_by_pkg[pkg]
    else:
        print(f"Stage3 repo size ({len(s3_pkgs)}) differs from "
              f"picklefile size ({len(s3provs_by_pkg)}), recalculating",
              file=sys.stderr)
        print_debug("Getting stage3 provides")
        s3provs_by_pkg = get_dependencies_by_packages(s3_pkgs, OPTION_PROVIDES, include_files=True)
        for pkg in s3provs_by_pkg:
            print_debug(f"Adding provides from package {pkg}")
            for dep in s3provs_by_pkg[pkg]:
                s3provs.append(dep)
        save_to_pickle(s3provs_by_pkg, STAGE3_PICKLEFILE)
        
    print_debug("Getting stage4 provides")
    s4provs = get_repo_dependencies(STAGE4REPO, OPTION_PROVIDES)
    print_debug(f"Got {len(s4provs)} dependencies for stage 4")

    # If all a source package's requires are listed in
    #  available provides, we can build it
    avail_provides = s3provs + s4provs
    
    # However, if our source package has provides that
    #  also show up in stage4 provides, we know it's
    #  already been built and don't need to rebuild it

    for pkg in src_pkgs:
        for provide in srcprovs[pkg]:
            if provide in s4provs:
                print_debug(f"Removing {pkg} from build candidate list: Provides {provide} found in Stage4 repo")
                src_pkgs.remove(pkg)
                break
    # For any source package whose requires all appear in avail_provides,
    #  we can build it
    build_pkgs = []
    for pkg in src_pkgs:
        for req in srcreqs[pkg]:
            if req not in avail_provides:
                print_debug(f"Removing {pkg} from build candidate list: nothing provides requirement {req}")
                break
        else:
            build_pkgs.append(pkg)

    for pkg in build_pkgs:
        print(pkg)


