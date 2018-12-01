%global debug_package %{nil}
%global gitdate 20181026
%global commit0 c10e7a30c8f63c50a13770a3a1df73263a545bb7
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})
%global gver .git%{shortcommit0}


Name: opensnitch
Version: 1.0.0
Release: 3%{?dist}
Summary: OpenSnitch is a GNU/Linux port of the Little Snitch application firewall
License: GPLv3
Group: Applications/Internet
Url: https://opensnitch.io/

Source0: https://github.com/evilsocket/opensnitch/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
Patch:	 nosudo.patch

BuildRequires: python3-devel
BuildRequires: compiler(go-compiler)
BuildRequires: git
BuildRequires: libnetfilter_queue-devel 
BuildRequires: protobuf proprotobuf-compiler protobuf-devel
BuildRequires: python3-qt5 python-qt5-devel 
BuildRequires: python3-pip python3-slugify python3-inotify
BuildRequires: libpcap-devel
BuildRequires: golang-github-matttproud-golang_protobuf_extensions-devel
BuildRequires: golang-github-fsnotify-fsnotify-devel
BuildRequires: golang-github-grpc-grpc-go-devel
BuildRequires: golang-golang-org-net-devel
BuildRequires: golang-github-golang-sys-devel
BuildRequires: golang-golangorg-text-devel
BuildRequires: golang-github-google-go-genproto-devel
BuildRequires: dep
Requires: python3-qt5
Requires: python3-dbus
Requires: libcap
ExclusiveArch:  %{go_arches}


%description
OpenSnitch is a GNU/Linux port of the Little Snitch application firewall.

%package daemon
Summary: OpenSnitch is a GNU/Linux port of the Little Snitch application firewall
Group: Applications/Internet

%description daemon
OpenSnitch is a GNU/Linux port of the Little Snitch application firewall.

This package contains opensnitch daemon.

%package ui
Summary: OpenSnitch is a GNU/Linux port of the Little Snitch application firewall
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-daemon = %{version}-%{release}

%description ui
OpenSnitch is a GNU/Linux port of the Little Snitch application firewall.

This package contains opensnitch ui.

%prep

tar xmzvf %{S:0} -C $PWD/
mv -f %{name}-%{commit0} %{name}

# We need to disble sudo
# Patch thanks to adisbladis
pushd %{name}
%patch -p1
popd
#---------------------------------------------
# trick
        if [ -L %{name} ]; then
                rm %{name} -rf
                mv .go/src/%{name}/ %{name}
        fi

        rm -rf ".go/src"
        mkdir -p ".go/src"
        mv "%{name}" ".go/src/"

        pushd ".go/src/%{name}/"
        ln -sf ".go/src/%{name}/" "%{name}"
	popd
#---------------------------------------------
%setup -T -D -n .go

%build
export GOPATH="%{_builddir}/.go"
pushd "$GOPATH/src/opensnitch/daemon"
# We need some dependencies 
# go get -u github.com/golang/dep/cmd/dep
# go get github.com/golang/protobuf/protoc-gen-go
go get github.com/natefinch/pie
python3 -m pip install --user grpcio grpcio-tools

# We need to said where is our build tools
export PATH=$PATH:$GOPATH/bin/
dep ensure
pushd "$GOPATH/src/opensnitch"
# The real build
%make_build

%install
export GOPATH="%{_builddir}/.go"
pushd "$GOPATH/src/opensnitch/"
mkdir -p %{buildroot}/usr/lib/systemd/system
mkdir -p %{buildroot}/%{_bindir}
%make_install
popd
# the GUI
pushd "$GOPATH/src/opensnitch/ui"
python3 -m pip install --isolated --root=%{buildroot} grpcio grpcio-tools unicode_slugify==0.1.3 pyinotify==0.9.6 configparser==3.5.0
popd

%post
systemctl enable opensnitchd
systemctl start opensnitchd 

%postun
systemctl stop opensnitchd 
systemctl disable opensnitchd

%files daemon
%license src/opensnitch/LICENSE 
%doc src/opensnitch/README.md
%dir %{_sysconfdir}/opensnitchd
%dir %{_sysconfdir}/opensnitchd/rules
%{_unitdir}/*
%{_bindir}/opensnitchd
%{_datadir}/kservices5/kcm_opensnitch.desktop

%files ui
%{_bindir}/opensnitch-ui
%{_datadir}/applications/opensnitch_ui.desktop
%{python3_sitelib}/opensnitch/
%{python3_sitelib}/opensnitch_ui-*.egg-info/

%changelog

* Sat Oct 27 2018 Pavlo Rudyi <paulcarroty at riseup dot net> 1.0.0-3
- Added build deps

* Sat Oct 27 2018 David Va <davidva AT tuta DOT io> 1.0.0-2
- Updated to 1.0.0-2
- First round 

* Fri May 18 2018 Aleksei Nikiforov <darktemplar@altlinux.org> 1.0.0-alt1.b.gitf71d8ce%ubt
- Initial build for ALT.
