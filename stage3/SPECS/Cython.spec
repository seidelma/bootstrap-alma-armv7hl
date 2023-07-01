# Disable tests on RHEL9 as to not pull in the test dependencies
# Specify --with tests to run the tests e.g. on EPEL
%bcond_with tests

# This bcond allows to ship a non-compiled version
# Slower, but sometimes necessary with alpha Python versions
%bcond_without cython_compile

Name:           Cython
Version:        0.29.22
Release:        7%{?dist}
Summary:        Language for writing Python extension modules

License:        ASL 2.0
URL:            http://www.cython.org
Source:         https://github.com/cython/cython/archive/%{version}/Cython-%{version}.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

%if %{with tests}
BuildRequires:  gcc-c++
BuildRequires:  python3-numpy
BuildRequires:  python3-jedi
%endif

%if %{with cython_compile}
BuildRequires:  gcc
%global python3_site %{python3_sitearch}
%else
BuildArch:      noarch
%global python3_site %{python3_sitelib}
%endif

%global _description %{expand:
The Cython language makes writing C extensions for the Python language as easy
as Python itself. Cython is a source code translator based on Pyrex,
but supports more cutting edge functionality and optimizations.

The Cython language is a superset of the Python language (almost all Python
code is also valid Cython code), but Cython additionally supports optional
static typing to natively call C functions, operate with C++ classes and
declare fast C types on variables and class attributes.
This allows the compiler to generate very efficient C code from Cython code.

This makes Cython the ideal language for writing glue code for external C/C++
libraries, and for fast C modules that speed up the execution of Python code.}

%description %{_description}


%package -n python3-Cython
Summary:        %{summary}
Provides:       Cython = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       Cython%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       cython = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       cython%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
%py_provides    python3-cython

# A small templating library is bundled in Cython/Tempita
# Upstream version 0.5.2 is available from https://pypi.org/project/Tempita
# but the bundled copy is patched and reorganized.
# Upstream homepage is inaccessible.
Provides:       bundled(python3dist(tempita))

%description -n python3-Cython %{_description}


#%package -n emacs-cython-mode
#Summary:        A major mode for editing Cython source files in Emacs
#BuildArch:      noarch
#BuildRequires:  emacs
#Requires:       emacs(bin) >= %{_emacs_version}

#%description -n emacs-cython-mode
#cython-mode is an Emacs major mode for editing Cython source files.


%prep
%autosetup -n cython-%{version} -p1


%build
%py3_build -- %{!?with_cython_compile:--no-cython-compile}

# emacs-cython-mode build
#echo ";;
#(require 'cython-mode)" > cython-mode-init.el
#cp -p Tools/cython-mode.el .
#%{_emacs_bytecompile} *.el


%install
%py3_install -- %{!?with_cython_compile:--no-cython-compile}
rm -rf %{buildroot}%{python3_sitelib}/setuptools/tests

# emacs-cython-mode install
#mkdir -p %{buildroot}%{_emacs_sitelispdir}/
#cp -p cython-mode.el cython-mode.elc %{buildroot}%{_emacs_sitelispdir}/
#mkdir -p %{buildroot}%{_emacs_sitestartdir}/
#cp -p cython-mode-init.el cython-mode-init.elc %{buildroot}%{_emacs_sitestartdir}/


%if %{with tests}
%check
%{python3} runtests.py -vv --no-pyregr %{?_smp_mflags} \
  %ifarch %{ix86}
  --exclude run.parallel  # https://github.com/cython/cython/issues/2807
  %endif

%endif


%files -n python3-Cython
%license LICENSE.txt
%doc *.txt Demos Doc Tools
%{_bindir}/cython
%{_bindir}/cygdb
%{_bindir}/cythonize
%{python3_site}/Cython-*.egg-info/
%{python3_site}/Cython/
%{python3_site}/pyximport/
%pycached %{python3_site}/cython.py

#%files -n emacs-cython-mode
#%license LICENSE.txt
#%{_emacs_sitelispdir}/cython*.el*
#%{_emacs_sitestartdir}/cython*.el*


%changelog
* Wed Feb 16 2022 Tomas Orsava <torsava@redhat.com> - 0.29.22-7
- Add gating configuration and a simple smoke test
- Related: rhbz#1950291

* Tue Feb 08 2022 Tomas Orsava <torsava@redhat.com> - 0.29.22-6
- Add automatically generated Obsoletes tag with the python39- prefix
  for smoother upgrade from RHEL8
- Related: rhbz#1990421

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com>
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com>
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Wed Mar 10 2021 Charalampos Stratakis <cstratak@redhat.com> - 0.29.22-3
- Disable tests on RHEL9 as to not pull in the test dependencies

* Tue Mar 09 2021 Miro Hrončok <mhroncok@redhat.com> - 0.29.22-2
- Remove an obsoleted patch
- Remove old Obsoletes and Conflicts
- Update description
- Provide cython, python3-cython

* Thu Mar 04 2021 Miro Hrončok <mhroncok@redhat.com> - 0.29.22-1
- Update to 0.29.22

* Mon Jan 25 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.29.21-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Nov 13 2020 Miro Hrončok <mhroncok@redhat.com> - 0.29.21-4
- Drop build dependency on coverage

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.29.21-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul 22 2020 Gwyn Ciesla <gwync@protonmail.com> - 0.29.21-2
- Re-enable tests.

* Wed Jul 22 2020 Gwyn Ciesla <gwync@protonmail.com> - 0.29.21-1
- 0.29.21

* Wed May 27 2020 sguelton@redhat.com - 0.29.19-1
- Update to 0.29.19

* Mon May 25 2020 Miro Hrončok <mhroncok@redhat.com> - 0.29.17-4
- Rebuilt for Python 3.9

* Fri May 22 2020 Miro Hrončok <mhroncok@redhat.com> - 0.29.17-3
- Bootstrap for Python 3.9

* Wed May 13 2020 Petr Viktorin <pviktori@redhat.com> - 0.29.17-2
- Backport classmethod fixes
  Fixes: https://bugzilla.redhat.com/show_bug.cgi?id=1788506

* Tue Apr 28 2020 Marcel Plch <mplch@redhat.com> - 0.29.17-1
- Update to 0.29.17

* Wed Mar 25 2020 Miro Hrončok <mhroncok@redhat.com> - 0.29.16-1
- Update to 0.29.16 (#1816785)

* Sat Feb 08 2020 Miro Hrončok <mhroncok@redhat.com> - 0.29.15-1
- Update to 0.29.15 (#1800158)

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.29.14-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Nov 04 2019 Miro Hrončok <mhroncok@redhat.com> - 0.29.14-1
- Update to 0.29.14 (#1768034)
- Python 2 subpackage has been removed

* Thu Oct 03 2019 Miro Hrončok <mhroncok@redhat.com> - 0.29.13-5
- Rebuilt for Python 3.8.0rc1 (#1748018)

* Thu Aug 15 2019 Miro Hrončok <mhroncok@redhat.com> - 0.29.13-4
- Rebuilt for Python 3.8

* Thu Aug 15 2019 Miro Hrončok <mhroncok@redhat.com> - 0.29.13-3
- Bootstrap for Python 3.8

* Thu Aug 01 2019 Gwyn Ciesla <gwync@protonmail.com> 0.29.13-2
- Rebuild with new numpy.

* Sat Jul 27 11:58:51 CEST 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.29.13-1
- Update to 0.29.13

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.29.12-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Jul 22 2019 Petr Viktorin <pviktori@redhat.com> - 0.29.12-2
- Remove non-essential Python 2 test dependencies

* Thu Jul 11 2019 Miro Hrončok <mhroncok@redhat.com> - 0.29.12-1
- Update to 0.29.12 (#1727580)

* Mon Jul 01 2019 Miro Hrončok <mhroncok@redhat.com> - 0.29.11-1
- Update to 0.29.11 (#1725361)

* Sun Jun 02 2019 Charalampos Stratakis <cstratak@redhat.com> - 0.29.10-1
- Update to 0.29.10 (#1716146)

* Thu May 30 2019 Miro Hrončok <mhroncok@redhat.com> - 0.29.9-1
- Update to 0.29.9 (#1714365)

* Mon May 13 07:10:35 CEST 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.29.7-1
- Update to 0.29.7

* Wed Feb 27 2019 Miro Hrončok <mhroncok@redhat.com> - 0.29.6-1
- Update to 0.29.6 (#1683661)

* Fri Feb 08 2019 Miro Hrončok <mhroncok@redhat.com> - 0.29.5-1
- Update to 0.29.5 (#1667643)

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.29.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sat Jan 19 2019 Miro Hrončok <mhroncok@redhat.com> - 0.29.3-1
- Update to 0.29.3 (#1667643)

* Tue Jan 08 2019 Alex Cobb <alex.cobb@smart.mit.edu> - 0.29.1-2
- Added emacs-cython-mode subpackage

* Mon Dec 10 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.29.1-1
- Update to 0.29.1

* Mon Dec 10 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.29-1
- Update to 0.29

* Wed Oct 03 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.29~rc2-1
- Update to 0.29~rc2

* Sat Aug 11 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.28.5-1
- Update to 0.28.5

* Sun Aug 05 2018 Miro Hrončok <mhroncok@redhat.com> - 0.28.4-3
- Only have one /usr/bin/cython

* Sun Jul 15 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.28.4-1
- Update to 0.28.4

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.28.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jun 15 2018 Miro Hrončok <mhroncok@redhat.com> - 0.28.1-2
- Rebuilt for Python 3.7

* Mon Mar 19 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.28.1-1
- Update to 0.28.1

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.27.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Nov 06 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.27.3-1
- Update to 0.27.3

* Mon Oct 02 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.27.1-1
- Update to 0.27.1

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.25.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.25.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed May 03 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.25.2-5
- Fix license

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.25.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Dec 22 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.25.2-3
- Backport couple of patches

* Mon Dec 12 2016 Charalampos Stratakis <cstratak@redhat.com> - 0.25.2-2
- Rebuild for Python 3.6

* Sat Dec 10 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.25.2-1
- Update to 0.25.2

* Sat Aug 27 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.24.1-8
- Fix provides (RHBZ #1370879)

* Thu Aug 25 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.24.1-7
- Run test suite

* Thu Aug 25 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.24.1-6
- Provide old names

* Thu Aug 25 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.24.1-5
- Use %%python_provide

* Tue Aug 23 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.24.1-4
- Update to 0.24.1

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.23.4-4
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.23.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 13 2016 Orion Poplawski <orion@cora.nwra.com> - 0.23.4-1
- Update to 0.23.4
- Ship cythonize3
- Modernize and cleanup spec
- Run tests, one python3 test fails with 3.5

* Tue Oct 13 2015 Robert Kuska <rkuska@redhat.com> - 0.23-2
- Rebuilt for Python3.5 rebuild

* Wed Aug 12 2015 Neal Becker <ndbecker2@gmail.com> - 0.23-2
- Update to 0.23

* Tue Jun 16 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.22-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Feb 13 2015 nbecker <ndbecker2@gmail.com> - 0.22-1
- oops, that should be 0.22 not 0.22.1

* Fri Feb 13 2015 nbecker <ndbecker2@gmail.com> - 0.22.1-1
- Update to 0.22

* Sat Nov 22 2014 nbecker <ndbecker2@gmail.com> - 0.21.1-1
- Update to 0.21.1 (br #1164297)

* Mon Sep 15 2014 nbecker <ndbecker2@gmail.com> - 0.21-5
- Add /bin/cythonize

* Mon Sep 15 2014 nbecker <ndbecker2@gmail.com> - 0.21-1
- Update to 0.21

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.20.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jun 06 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.20.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 28 2014 Thomas Spura <tomspur@fedoraproject.org> - 0.20.1-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/Python_3.4

* Fri May  9 2014 Orion Poplawski <orion@cora.nwra.com> - 0.20.1-2
- Rebuild for Python 3.4

* Fri May  9 2014 Orion Poplawski <orion@cora.nwra.com> - 0.20.1-1
- Update to 0.20.1

* Mon Jan 20 2014 nbecker <ndbecker2@gmail.com> - 0.20-1
- Update to 0.20

* Thu Oct 17 2013 nbecker <ndbecker2@gmail.com> - 0.19.2-2
- Fix BR 1019498

* Sun Oct 13 2013 nbecker <ndbecker2@gmail.com> - 0.19-2
- Update to 0.19.2

* Fri Aug 02 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.19-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Apr 19 2013 nbecker <ndbecker2@gmail.com> - 0.19-1
- Update to 0.19

* Tue Jan 29 2013 Neal Becker <ndbecker2@gmail.com> - 0.18-1
- update to 0.18

* Sat Dec 15 2012 Neal Becker <ndbecker2@gmail.com> - 0.17.3-1
- Update to 0.17.3

* Wed Nov 21 2012 Neal Becker <ndbecker2@gmail.com> - 0.17.2-1
- update to 0.17.2

* Wed Sep 26 2012 Neal Becker <ndbecker2@gmail.com> - 0.17.1-1
- Update to 0.17.1

* Mon Sep  3 2012 Neal Becker <ndbecker2@gmail.com> - 0.17-1
- Update to 0.17

* Tue Aug 28 2012 Neal Becker <ndbecker2@gmail.com> - 0.17-3.b3
- Turn on check (temporarily)
- Add br numpy from check

* Tue Aug 28 2012 Neal Becker <ndbecker2@gmail.com> - 0.17-1.b3
- Test 0.17b3

* Fri Aug 24 2012 David Malcolm <dmalcolm@redhat.com> - 0.16-3
- generalize egg-info logic to support RHEL (rhbz#851528)

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.16-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Apr 27 2012 Neal Becker <ndbecker2@gmail.com> - 0.16-1
- Update to 0.16

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.15.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Sep 20 2011 Neal Becker <ndbecker2@gmail.com> - 0.15.1-1
- Update to 0.15.1

* Sat Aug  6 2011 Neal Becker <ndbecker2@gmail.com> - 0.15-1
- Update to 0.15

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.14.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Feb  5 2011 Neal Becker <ndbecker2@gmail.com> - 0.14.1-1
- Update to 0.14.1

* Wed Dec 15 2010 Neal Becker <ndbecker2@gmail.com> - 0.14-2
- Add cygdb

* Wed Dec 15 2010 Neal Becker <ndbecker2@gmail.com> - 0.14-1
- Update to 0.14

* Wed Aug 25 2010 Neal Becker <ndbecker2@gmail.com> - 0.13-1
- Update to 0.13

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 0.12.1-5
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Fri Feb  5 2010 Neal Becker <ndbecker2@gmail.com> - 0.12.1-4
- Disable check for now as it fails on PPC

* Tue Feb  2 2010 Neal Becker <ndbecker2@gmail.com> - 0.12.1-2
- typo
- stupid rpm comments

* Mon Nov 23 2009 Neal Becker <ndbecker2@gmail.com> - 0.12-1.rc1
- Make that 0.12

* Mon Nov 23 2009 Neal Becker <ndbecker2@gmail.com> - 0.12.1-1.rc1
- Update to 0.12.1

* Sun Sep 27 2009 Neal Becker <ndbecker2@gmail.com> - 0.11.3-1.rc1
- Update to 0.11.3rc1
- Update to 0.11.3

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed May 20 2009 Neal Becker <ndbecker2@gmail.com> - 0.11.2-1
- Update to 0.11.2

* Thu Apr 16 2009 Neal Becker <ndbecker2@gmail.com> - 0.11.1-1
- Update to 0.11.1

* Sat Mar 14 2009 Neal Becker <ndbecker2@gmail.com> - 0.11-2
- Missed cython.py*

* Sat Mar 14 2009 Neal Becker <ndbecker2@gmail.com> - 0.11-1
- Update to 0.11
- Exclude numpy from tests so we don't have to BR it

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Dec 17 2008 Neal Becker <ndbecker2@gmail.com> - 0.10.3-1
- Update to 0.10.3

* Thu Dec 04 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.10.2-2
- Rebuild for Python 2.6

* Mon Dec  1 2008 Neal Becker <ndbecker2@gmail.com> - 0.10.2-1
- Update to 0.10.2

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.10.1-2
- Rebuild for Python 2.6

* Wed Nov 19 2008 Neal Becker <ndbecker2@gmail.com> - 0.10.1-1
- Update to 0.10.1

* Sun Nov  9 2008 Neal Becker <ndbecker2@gmail.com> - 0.10-3
- Fix typo

* Sun Nov  9 2008 Neal Becker <ndbecker2@gmail.com> - 0.10-1
- Update to 0.10

* Fri Jun 13 2008 Neal Becker <ndbecker2@gmail.com> - 0.9.8-2
- Install into python_sitearch
- Add %%check

* Fri Jun 13 2008 Neal Becker <ndbecker2@gmail.com> - 0.9.8-1
- Update to 0.9.8

* Mon Apr 14 2008 José Matos <jamatos[AT]fc.up.pt> - 0.9.6.13.1-3
- Remove remaining --record.
- Add more documentation (Doc and Tools).
- Add correct entry for egg-info (F9+).

* Mon Apr 14 2008 Neal Becker <ndbecker2@gmail.com> - 0.9.6.13.1-2
- Change License to Python
- Install About.html
- Fix mixed spaces/tabs
- Don't use --record

* Tue Apr  8 2008 Neal Becker <ndbecker2@gmail.com> - 0.9.6.13.1-1
- Update to 0.9.6.13.1

* Mon Apr  7 2008 Neal Becker <ndbecker2@gmail.com> - 0.9.6.13-1
- Update to 0.9.6.13
- Add docs

* Tue Feb 26 2008 Neal Becker <ndbecker2@gmail.com> - 0.9.6.12-1
- Initial version
