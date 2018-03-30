%global pypi_name apispec

%if 0%{?fedora} || 0%{?rhel} >= 8
%global build_py3   1
%endif

Name:           python-%{pypi_name}
Version:        0.33.0
Release:        1%{?dist}
Summary:        A pluggable API specification generator. Currently supports the OpenAPI specification (f.k.a. Swagger 2.0)

License:        MIT
URL:            https://github.com/marshmallow-code/apispec
Source0:        https://files.pythonhosted.org/packages/source/a/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch
 
BuildRequires:  python2-devel
BuildRequires:  python-setuptools

%if 0%{?build_py3}
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
%endif

%description
apispec is a pluggable API specification generator. Currently supports the OpenAPI specification (f.k.a. Swagger 2.0). Includes plugins for marshmallow, Flask, Tornado and bottle.

%package -n     python2-%{pypi_name}
Summary:        %{summary}
%{?python_provide:%python_provide python2-%{pypi_name}}
Requires:       PyYAML >= 3.10
%description -n python2-%{pypi_name}
apispec is a pluggable API specification generator. Currently supports the OpenAPI specification (f.k.a. Swagger 2.0). Includes plugins for marshmallow, Flask, Tornado and bottle.

%if 0%{?build_py3}
%package -n     python3-%{pypi_name}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{pypi_name}}
Requires:       python3-PyYAML >= 3.10
%description -n python3-%{pypi_name}
apispec is a pluggable API specification generator. Currently supports the OpenAPI specification (f.k.a. Swagger 2.0). Includes plugins for marshmallow, Flask, Tornado and bottle.
%endif

%prep
%autosetup -n %{pypi_name}-%{version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%build
%py2_build
%if 0%{?build_py3}
%py3_build
%endif

%install
# Must do the subpackages' install first because the scripts in /usr/bin are
# overwritten with every setup.py install.
%if 0%{?build_py3}
%py3_install
%endif
%py2_install

%check

%files -n python2-%{pypi_name}
%license docs/license.rst LICENSE
%doc README.rst
%{python2_sitelib}/%{pypi_name}
%{python2_sitelib}/%{pypi_name}-%{version}-py?.?.egg-info

%if 0%{?build_py3}
%files -n python3-%{pypi_name}
%license docs/license.rst LICENSE
%doc README.rst
%{python3_sitelib}/%{pypi_name}
%{python3_sitelib}/%{pypi_name}-%{version}-py?.?.egg-info
%endif

%changelog
* Fri Mar 30 2018 Jan Dobes <jdobes@redhat.com> - 0.33.0-1
- Initial package.
