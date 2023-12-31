%global apiversion 1.15

Name: cppunit
Version: 1.15.1
Release: 8%{?dist}

Summary: C++ unit testing framework
# no license in files
License: LGPLv2+
Url: https://www.freedesktop.org/wiki/Software/cppunit/
Source: http://dev-www.libreoffice.org/src/%{name}-%{version}.tar.gz

BuildRequires: doxygen
BuildRequires: gcc-c++
BuildRequires: graphviz
BuildRequires: make

%description
CppUnit is the C++ port of the famous JUnit framework for unit testing.
Test output is in XML for automatic testing and GUI based for supervised 
tests.

%package devel
Summary: Libraries and headers for cppunit development
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
This package contains the libraries and headers necessary for developing
programs that use cppunit.

%package doc
Summary: HTML formatted API documention for cppunit

%description doc
The cppunit-doc package contains HTML formatted API documention generated by
the popular doxygen documentation generation tool.

%prep
%autosetup -p1

%build
%configure --disable-doxygen --disable-static --disable-silent-rules
sed -i \
    -e 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' \
    -e 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' \
    libtool

%make_build

%install
%make_install

rm %{buildroot}%{_libdir}/*.la
# remove double of doc
rm -rf %{buildroot}%{_datadir}/doc/cppunit %{buildroot}%{_datadir}/%{name}/html

# clean up examples
rm -rf __dist-examples __dist-examples-dir
cp -a examples __dist-examples
make -C __dist-examples distclean
# Makefile.am files are left as documentation
find __dist-examples \( -name Makefile.in -o -name .gitignore -o -name '*.opt' -o -name '*.sln' -o -name '*.vcproj' \) -exec rm {} \;
mkdir __dist-examples-dir
mv __dist-examples __dist-examples-dir/examples


%ldconfig_scriptlets

%files
%doc AUTHORS NEWS README THANKS TODO BUGS doc/FAQ
%license COPYING
%{_bindir}/DllPlugInTester
%{_libdir}/libcppunit-%{apiversion}.so.1
%{_libdir}/libcppunit-%{apiversion}.so.1.*

%files devel
%{_includedir}/cppunit
%{_libdir}/libcppunit.so
%{_libdir}/pkgconfig/cppunit.pc

%files doc
%license COPYING
%doc __dist-examples-dir/examples/
#%doc doc/html

%changelog
* Wed Jan 26 2022 Caolán McNamara <caolanm@redhat.com> - 1.15.1-8
- Resolves: rhbz#2040997 skip cppunit-devel

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.15.1-7
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 1.15.1-6
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.15.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.15.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.15.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Dec 25 2019 David Tardon <dtardon@redhat.com> - 1.15.1-2
- try again

* Wed Dec 25 2019 David Tardon <dtardon@redhat.com> - 1.15.1-1
- new upstream release

* Sat Dec 21 2019 David Tardon <dtardon@redhat.com> - 1.15.0-1
- new upstream release

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.14.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.14.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.14.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Jun 28 2018 Rex Dieter <rdieter@fedoraproject.org> - 1.14.0-5
- use %%make_build %%make_install %%ldconfig_scriptlets
- -devel: tighten dep on main pkg with %%_isa

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.14.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.14.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.14.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue May 02 2017 David Tardon <dtardon@redhat.com> - 1.14.0-1
- new upstream release

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.13.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sat Feb 13 2016 David Tardon <dtardon@redhat.com> - 1.13.2-2
- drop obsolete cppunit-config

* Sat Feb 13 2016 David Tardon <dtardon@redhat.com> - 1.13.2-1
- switch to new upstream

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.1-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.12.1-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Apr 11 2015 David Tardon <dtardon@redhat.com> - 1.12.1-15
- rebuild for yet another C++ ABI break

* Fri Feb 20 2015 David Tardon <dtardon@redhat.com> - 1.12.1-14
- rebuild for C++ stdlib ABI change in gcc5

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.12.1-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.12.1-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May 20 2014 David Tardon <dtardon@redhat.com> - 1.12.1-11
- rhbz#925193 add support for aarch64

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.12.1-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.12.1-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.12.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.12.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Oct 05 2011 Caolán McNamara <caolanm@redhat.com> - 1.12.1-6
- add sf#2912630 fix for unused argument warnings

* Tue Jun 28 2011 Steven M. Parrish <smparrish@gmail.com> - 1.12.1-5
- Fix for bug 452340

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.12.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.12.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.12.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Sep 18 2008 Patrice Dumas <pertusus@free.fr> 1.12.1-1
- Update to 1.12.1

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.12.0-5
- Autorebuild for GCC 4.3

* Mon Dec 17 2007 Patrice Dumas <pertusus@free.fr> 1.12.0-4
- remove libdir reference to cppunit-config, should fix multiarch conflict
  (#340951)
- fix encoding and remove windows related files in examples
- keep timestamps

* Mon Jan 29 2007 Patrice Dumas <pertusus@free.fr> 1.12.0-3
- add rightly files to -devel (#224106)
- add necessary requires for -devel (#224106)
- ship examples

* Sun Sep 10 2006 Patrice Dumas <pertusus@free.fr> 1.12.0-2
- rebuild for FC6

* Wed Jul  5 2006 Patrice Dumas <pertusus@free.fr> 1.12.0-1
- update to 1.12

* Sun May 21 2006 Patrice Dumas <pertusus@free.fr> 1.11.6-1
- update to 1.11.6

* Wed Dec 21 2005 Patrice Dumas <pertusus@free.fr> 1.11.4-1
- update

* Mon Aug 15 2005 Tom "spot" Callaway <tcallawa@redhat.com> 1.11.0-2
- various cleanups

* Mon Jul  4 2005 Patrice Dumas <pertusus@free.fr> 1.11.0-1
- update using the fedora template 
 
* Sat Apr 14 2001 Bastiaan Bakker <bastiaan.bakker@lifeline.nl>
- Initial release
