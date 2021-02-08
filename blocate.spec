# https://fedoraproject.org/wiki/How_to_create_an_RPM_package
# Built and maintained by John Boero - boeroboy@gmail.com
# In honor of Seth Vidal https://www.redhat.com/it/blog/thank-you-seth-vidal

Name:		blocate
Version:	1.0
Release:	0%{?dist}
Summary:	Blocate directory indexing and searching.
License:	GPL
Source0:    https://github.com/jboero/blocate/archive/main.tar.gz
Requires:   sqlite-3 xargs bash
URL:        https://github.com/jboero/blocate

%define debug_package %{nil}

%description
A sqlite-based slocate and mlocate alternative using simple scripts.

%prep
%autosetup -c %{name}-%{version}

%build

%install
mkdir -p %{buildroot}%{_bindir}/
cp -p blocate bindex %{buildroot}%{_bindir}/

%clean
rm -rf %{buildroot}
rm -rf %{_builddir}/*

%files
%{_bindir}/blocate
%{_bindir}/bindex
