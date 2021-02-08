# https://fedoraproject.org/wiki/How_to_create_an_RPM_package
# Built and maintained by John Boero - jboero@hashicorp.com
# In honor of Seth Vidal https://www.redhat.com/it/blog/thank-you-seth-vidal

%define hashiarch %(if [ "%{_arch}" == 'x86_64' ]; then echo 'amd64'; elif [ "%{_arch}" == 'aarch64' ]; then echo 'arm'; elif [ "%_arch" == 'i386' ]; then echo '386'; else echo "%{_arch}"; fi)

Name:		restool
Version:	20.04
Release:	5%{?dist}
Summary:	Restool network tool
License:	GPL
# Our engineering uses "amd64" instead of "x86_64" so ugly mapping...
Source0:        https://github.com/WindRiver-Labs/source.codeaurora.org.external.qoriq.qoriq-components.restool/archive/LSDK-%{version}.tar.gz

BuildRequires:  systemd coreutils unzip make gcc
Requires(pre):	shadow-utils
Requires(post):	systemd libcap
#Requires(preun):	systemd
#Requires(postun):	systemd
#URL:		https://github.com/qoriq-open-source/restool
URL:  https://github.com/WindRiver-Labs/source.codeaurora.org.external.qoriq.qoriq-components.restool

%define debug_package %{nil}

%description

%prep
%autosetup -c %{name}-LSDK-%{version}

%build
cd source.codeaurora.org.external.qoriq.qoriq-components.restool-LSDK-%{version}
ls -lh
export LDFLAGS="$LDFLAGS -z muldefs"
make -j

%install
mkdir -p %{buildroot}%{_bindir}/
cp -p source.codeaurora.org.external.qoriq.qoriq-components.restool-LSDK-%{version}/%{name} %{buildroot}%{_bindir}/
cp -p source.codeaurora.org.external.qoriq.qoriq-components.restool-LSDK-%{version}/scripts/* %{buildroot}%{_bindir}/

cd %{buildroot}%{_bindir}
ln -s ls-main ls-addmux
ln -s ls-main ls-addsw
ln -s ls-main ls-addni
ln -s ls-main ls-listni
ln -s ls-main ls-listmac

mkdir -p %{buildroot}/usr/lib/systemd/system
cat <<-EOF > %{buildroot}/usr/lib/systemd/system/dpmac@.service
[Unit]
Description=SFP+ Ports manual activation

[Service]
Type=oneshot
Restart=on-failure
ExecStart=/usr/bin/sleep %i ; /usr/bin/ls-addni dpmac.%i
RestartSec=5
TimeoutStartSec=10

[Install]
WantedBy=network.target
EOF

%clean
rm -rf %{buildroot}
rm -rf %{_builddir}/*

%files
%{_bindir}/%{name}
%{_bindir}/ls-append-dpl
%{_bindir}/ls-debug
%{_bindir}/ls-main
%{_bindir}/ls-addmux
%{_bindir}/ls-addsw
%{_bindir}/ls-addni
%{_bindir}/ls-listni
%{_bindir}/ls-listmac
/usr/lib/systemd/system/dpmac@.service

%pre
%post
%systemd_post dpmac@.service
%preun
%systemd_preun dpmac@.service
%postun
%systemd_postun_with_restart dpmac@.service
