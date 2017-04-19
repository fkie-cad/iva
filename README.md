# Inventory Vulnerability Analysis (IVA)

### Index <a name="index"></a>

- [Summary](#summary)
- [Modules](#modules)
- [Installation](#installation)
- [Tests](#tests)
- [Usage](#usage)
- [Configuration](#configuration)
- [Authors](#authors)
- [License](#license)

## Summary <a name="summary"></a>

IVA is a system (written in Python 3) to automate the process of finding possible vulnerabilities in software products installed inside an organization.
It receives as input a list of software products (the inventory) in JSON format. Each JSON document contains three attributes: vendor, product, and version. IVA retrieves the software inventory from a [GLPI](http://glpi-project.org/spip.php?lang=en) database ([GLPI](http://glpi-project.org/spip.php?lang=en) is currently the only DB supported by IVA).

To find possible vulnerabilities for the software products, IVA employs the [CPE dictionary](https://nvd.nist.gov/cpe.cfm) and the [CVE feeds](https://nvd.nist.gov/download.cfm). First, IVA provides a list of CPE candidates that match a software product.  Once a CPE is assigned to a product, IVA searches for CVEs that possibly match the assigned CPE. IVA also generates alerts (in case the user confirms a CVE as match for a product) and allows to send, via [SMTP](https://www.ietf.org/rfc/rfc2821.txt), notifications about the vulnerable software.

### Main Features

* Software inventory import from [GLPI](http://glpi-project.org/spip.php?lang=en)
* [CPE](https://nvd.nist.gov/cpe.cfm) and [CVE](https://cve.mitre.org/) support
* Additional infos on matching CVEs by linking to a local copy of [cve-search](https://github.com/cve-search/cve-search)
* CPE and CVE matching algorithms to semi-automatically find vulnerable software products
* Matching algorithms based on the CPE Well-Formed Name (WFN) format
* Automatic update of the CPE and CVE repositories
* Usage via a web interface
* LDAP support for user authentication
* Notifications of vulnerable software via email (SMTP(S)) and GPG support
* Implemented with [Python](https://www.python.org/) 3, [Django](https://www.djangoproject.com/), and [MongoDB](https://www.mongodb.com/)

[Index](#index)

## Modules <a name="modules"></a>

IVA is basically composed of 8 modules: Inventory, CPE and CVE Database, Well-Formed Name Converter, CPE and CVE Matching, Alerts, Security, and Tasks Manager. In the following sections, each module is briefly explained.

### Inventory <a name="inventory"></a>

This module allows to read the software products from an inventory database (currently, IVA only supports [GLPI](http://glpi-project.org/spip.php?lang=en) database), and then, the information read about each software product is converted into JSON format, as shown in the following example: 

```json
{"id": "d6218a56203853300f4862ae8c23a103", "vendor": "Microsoft Corporation", "product": "Internet Explorer", "version": "8.0.7"}
```

The JSON documents of each software product are stored in the IVA database. The id attribute is the MD5 hash value of the vendor, product, and version. IVA uses the id to avoid creating a new document for a product that is already in the IVA database.

[Index](#index)

### Local Repositories <a name="cpe_cve_db"></a>

To carry out the CPE and CVE matching (see CPE and CVE Matching sections), IVA does not query the public [CPE dictionary](https://nvd.nist.gov/cpe.cfm) and the [CVE feeds](https://nvd.nist.gov/download.cfm). Instead, it queries its _local database_ which contains a copy of both repositories. To fetch the CPE dictionary and the CVE feeds from the NVD public repositories, IVA uses [cve-search](https://github.com/cve-search/cve-search). Having a local copy of the CPE and CVE repositories allows a fast lookup when executing the CPE and CVE matching algorithms. 

#### Tasks 

To keep the local repositories updated, IVA defines three tasks:

1. <b>Daily DB Update </b> This task is scheduled daily. It updates the local repositories (CPE and CVE) with the new entries fetched from the public repositories using [cve-search](https://github.com/cve-search/cve-search). Thereafter, it performs a search of CVE matches for the software products which already have a CPE assigned.
2. <b>Populate DB </b> This task is used to populate the local repositories when they are empty.
3. <b>Repopulate DB </b> This task is used to repopulate the local repositories.


[Index](#index)

### Well-Formed Name (WFN) Converter <a name="wfn"></a>

To facilitate the lookup of CPE candidates and possible CVE matches for a software product (see CPE and CVE Matching sections), this module converts the URI binding of a CPE into its well-formed name format. The conversion is based on the [CPE Naming Specification Version 2.3](https://www.nist.gov/node/589966). In the following, an example of a conversion is shown:

<b>CPE URI binding:</b>

```
cpe:/a:microsoft:internet_explorer:8.*::en~-~~windows~x86~
```

<b>CPE WFN:</b>

```json
{"part": "a", "vendor": "microsoft", "product": "internet_explorer", "version": "8.*", "update": "ANY", "edition": "NA", "language": "en", "sw_edition": "ANY", "target_sw": "windows", "target_hw": "x86", "other": "ANY"}
```

Specially, this conversion is important when searching for CVE matches for a given CPE. When a CPE entry is modified (e.g., due to a typo) in the CPE Dictionary, the modification is not synchronized with the CVE feeds. This can prevent from finding the CVE entries that must otherwise match the modified CPE. This is the case when comparing the _CPE URI binding of the CPE dictionary_ with the _CPE URI binding of the CVE feeds_. This can however be overcome with string matching algorithms that determine the similarity of two strings. However, if we apply such methods, we cannot establish which attributes (e.g., vendor, product, version) of both CPEs (CPE in the CPE dictionary and CPE in the CVE feed) are unequal. 

On the other hand, by comparing both CPEs based on their WFNs, we can determine which attributes are unequal, and moreover, we can assign weights to the attributes. For example, the attributes `vendor`, `product`, and `version` should have higher weights than the attributes `target_sw`, `target_hw`, or `other`. In this way, we are able to calculate a more accurate similarity score. In addition, this method allows us to perform logical comparisons between two CPEs' versions. For example, the version <b>8.* is equal to 8.2.7</b>, due to the special character <b>*</b>.  

[Index](#index) 
 
### CPE Matching <a name="cpe_matching"></a>

This module allows assigning a suitable [CPE](https://cpe.mitre.org/) to a software product. To do this, IVA searches in the CPE collection (local copy of the [CPE dictionary](https://nvd.nist.gov/cpe.cfm)) for the _best candidates_ that could match that software product. The selection of the CPE candidates is performed by comparing the software's information (vendor, product, and version) with the CPE entries' attributes (wfn.vendor, wfn.product, and wfn.version). This comparison is based on regular expressions, edit distance, and other string matching methods. 

Once the user has selected a CPE for that software product, IVA adds the selected CPE (well-formed name and URI binding) to the software document. Following the example shown above, the resulting document after the CPE assignment is shown below:

```json
{"id": "d6218a56203853300f4862ae8c23a103", "vendor": "Microsoft Corporation", "product": "Internet Explorer", "version": "8.0.7", "cpe": {"uri_binding": "cpe:/a:microsoft:internet_explorer:8.*", "wfn": {"part": "a", "vendor": "microsoft", "product": "internet_explorer", "version": "8.*", "update": "ANY", "edition": "ANY", "language": "ANY", "sw_edition": "ANY", "target_sw": "ANY", "target_hw": "ANY", "other": "ANY"}}
```

[Index](#index)

### CVE Matching <a name="cve_matching"></a>

This module searches for possible CVE matches for a software product based on the product's CPE and the CPE entries of a CVE. If a CVE does not have any CPE entry, the search is carried out using the CVE description. The comparison of the CPE WFN attributes (or the CVE description) is based on regular expressions, edit distance, and other string matching methods.

After finding possible matches, they are added to the software document in a list with the key `cve_matches`, as shown in the example below. Each CVE match contains four elements: 

* `cve_id` CVE Identifier 
* `cpe_entries` CPE entries of the affected software products. However, only the entries that are relevant for the product of the inventory.
* `removed` 0 means that the CVE was not yet discarded as a match, and 1 means the opposite.
* `positive` 0 means that the CVE was not yet confirmed as a match, and 1 means the opposite.

```json
{"id": "d6218a56203853300f4862ae8c23a103", "vendor": "Microsoft Corporation", "product": "Internet Explorer", "cpe": {"uri_binding": "cpe:/a:microsoft:internet_explorer:8.*:::de", "wfn": {"target_sw": "ANY", "sw_edition": "ANY", "version": "8.*", "vendor": "microsoft", "language": "de", "other": "ANY", "target_hw": "ANY", "part": "a", "edition": "ANY", "product": "internet_explorer", "update": "ANY"}}, "version": "8.0.7601.17514", "cve_matches": [{"removed": 0, "cpe_entries": ["cpe:/a:microsoft:internet_explorer:8"], "cve_id": "CVE-2008-2948", "positive": 0}, {"removed": 0, "cpe_entries": ["cpe:/a:microsoft:internet_explorer:8:beta2"], "cve_id": "CVE-2008-5551", "positive": 0}, {"removed": 0, "cpe_entries": ["cpe:/a:microsoft:internet_explorer:8:beta2"], "cve_id": "CVE-2008-5552", "positive": 0}, {"removed": 0, "cpe_entries": ["cpe:/a:microsoft:internet_explorer:8:beta2"], "cve_id": "CVE-2008-5553", "positive": 0}, {"removed": 0, "cpe_entries": ["cpe:/a:microsoft:internet_explorer:8:beta2"], "cve_id": "CVE-2008-5554", "positive": 0}]}
```

[Index](#index)

### Alerts <a name="alerts"></a>

This module generates an alert when a user confirms that a CVE is a match for a software product. The alerts represent a list of vulnerable software in the inventory. In addition, this module allows sending notifications (via email) containing information about a vulnerable software.   

[Index](#index)

### Security <a name="security"></a>

This module assures that only authorized users can access the IVA system. To authenticate a user, this module queries the IVA database (<b>local authentication</b>) and verifies the user's credentials (username and password). Moreover, user authentication can be performed via LDAP (<b>LDAP authentication</b>). To use this method, the user must configure the LDAP options (see section Configuration) in order to query the LDAP directory.

[Index](#index)

## Installation <a name="installation"></a>

The following sections explain how to install IVA and its requirements. The installation steps were tested on CentOS 6.8. Installation on Ubuntu 14.04 LTS was also tested and works similarly, but is not documented here.

### Source Code

[Git](https://git-scm.com/) is needed download the source code. To install it on CentOS, open a terminal and enter the following command as root:
```
yum install git
```

To download IVA, enter the following [Git](https://git-scm.com/) command from the directory where you want to install IVA (e.g., /usr/local/share): 

```
git clone https://github.com/fkie-cad/iva.git
```
If you get a 401 error, try:
```
git clone https://username@github.com/fkie-cad/iva.git
```

### Requirements

At the moment, Python3 and MongoDB must be installed manually on CentOS 6.8 as there are no yum packages available. Please refer to the respective installation instructions.

1. <b>[Python 3](https://www.python.org/downloads/)</b>
2. <b>[MongoDB](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-red-hat/)</b>
3. <b>[cve-search](https://github.com/cve-search/cve-search)</b>
4. <b>Python dependencies:</b> To facilitate the installation of the Python dependencies, the source code is shipped with a <b>requirements.txt</b> file, which can be found in the root directory. To install the dependencies, execute the following [pip](https://pip.pypa.io) 3 command:
	```
	pip3 install -r requirements.txt
	```

### Installation Test

To test the installation, run the file <b>main.py</b>, which is located at the root directory of the source code, with the option `test`:

```
python3 main.py test
```

If all the requirements were installed correctly, IVA can now be accessed at: http://localhost:8080/iva/index.html. To log into the IVA system, use the credentials that were printed in the terminal. Alternatively, you can find the credentials in <b>./user_authentication/dummy_user_credentials.txt</b>. 

The _installation test modus_ allow you to test some functionalities of IVA. For example, if you go to `new software` (this option is shown on the menu of the IVA web interface), you will see a list of software products without assigned CPEs. By clicking on the search icon of a product, you can search CPE candidates for that product. You can assign a suitable CPE for that product and then search CVEs for it. If you click on the option `software with CPE`, you will see a list of products that already have CPEs assigned to them.

#### Configuration Remarks

In some cases, in order to test the installation, some configuration options must be modified in <b>./dummy/config.ini</b>.

<b>Frontend: </b> If `localhost:8080` does not match with your setup (e.g., you installed IVA on a virtual machine, but you want to access it from your host machine), the following options must be configured:

`[frontend]` 

- `host=` host name of IVA web interface (e.g., 192.168.56.101).
- `port=` port of IVA web interface (e.g., 8080).

<b>Database Authentication: </b> If MongoDB authentication is required, the following options must be configured:

`[database]`

- `authentication=` This option must be set to 1. 
- `user=` Username of the user granted to read and write the IVA database.
- `password=` Password of the user granted to read and write the IVA database.

[Index](#index)

## Tests <a name="tests"></a>

IVA is delivered with a set of UnitTests, which can be executed from the root directory of the IVA source code with the following command:  

```
python3 -m unittest discover -s tests
```

[Index](#index)

## Usage <a name="usage"></a>

The following sections explain how to use the main functionalities of IVA.

### Start IVA

To start IVA, run <b>main.py</b> which can be found in the root directory of the source code:
```
python3 main.py
```
The first time you run IVA, a user is created so that you can log in. The credentials (username and password) of this user are saved in <b>./user_authentication/dummy_user_credentials.txt</b>. After the first login, we recommend you to create a new user (see [Users](#users)), delete the dummy user, and delete the file <b>./user_authentication/dummy_user_credentials.txt</b>. 

### Log in 

IVA is accessed via its web interface. To log in, open a web browser and go to:
``` 
http://host:port/iva/sign_in.html  
``` 
Replace `host` and `port` with the information you provided in the section `[frontend]` of <b>config.ini</b> (see section [Configuration](#configuration)). 

After providing your credentials in the login form, IVA verifies whether the entered information is valid. This is done by searching the user in the local database or via LDAP. If you want to use LDAP, you must configure the section `[ldap]` of <b>config.ini</b> (see Section [Configuration](#configuration)).  

### Read Inventory

To read the software inventory from the GLPI database, from the IVA web interface, select the option New Software of the main menu, and then click on the GLPI icon. Note that, to be able to read the inventory, you must first configure the section `[inventory-database]` of <b>config.ini</b> (see section [Configuration](#configuration)).

### Populate Local Repositories

To populate the local repositories (CPE dictionary and CVE feeds), click on the option Local Repositories of the main menu, and then press the Populate button. If this button is not available, it means that the repositories were already populated. In this case, you will see the Repopulate button. 

### Daily Repository Update <a name="daily_update"></a>

To schedule a daily update of the CPE dictionary and CVE feeds, select the option Local Repositories of the main menu. On the section Daily Update, click on the clock icon to activate the daily update. The task is activated when the clock icon does not have a red circle on it. To change the schedule time, click on the change execution time icon and enter the time you want the update to be executed.    

### Assign CPE

To assign a CPE to a software product, select the option New Software in the main menu. On this page, you will see a list of software products which don't have a CPE yet. Then, click on the Search icon of the software product you want to assign a CPE to. IVA will search CPEs that could match the software product. Once you selected a suitable CPE, press the button Assign CPE. If none of the CPE candidates completely match the software product, you can edit the CPE attributes (e.g., version, update, edition).

The CPEs of software products can be modified from Software with CPE. On this page, you will see a list of products that have a CPE already. To edit one, click on the Edit CPE icon.

### Search CVE Matches

To search CVE matches for a software product, click on the option Software with CPE in the main menu and then click on the Search icon of the product you want to search CVEs for. If you already configured the [daily repository update](#daily_update), the search of CVEs for each software product with CPE is performed daily. 

### Process CVE Matches <a href="cve_match"></a>

To see all the CVE matches, click on the option CVE Matches in the main menu. On this page, you see all the found matches for the software products with assigned CPEs. Here, you can confirm a CVE match (you are sure that the vulnerability corresponds to the software product) or you can remove the CVE match (you are sure that the CVE is not a match for the software product). When you confirm a CVE match, an alert is generated.    

### Process Alerts <a name="alerts"></a>

To see all the alerts that have been generated, click on the option Alerts in the main menu. On this page, the following actions can be performed: 
 
* <b>Change Alert Status</b> An alert can have the following status: 
	- <b>New</b> The alert was generated due to the confirmation of a CVE match (see [CVE Matches](#cve_match)). This status can be changed to Closed or Removed.
	- <b>Closed</b> The alert was was closed, for example, because the software product was patched or uninstalled, thus it is not longer in the inventory. This status can be changed to New or Removed.   
	- <b>Removed</b> If an alert was mistakenly generated, you can set its status to removed.
* <b>Send Notification</b> To send a notification (via Email) of the vulnerable software product, click on the notify icon. To use this functionality, you must configure the section `[smtp]` of <b>config.ini</b> (see Section [Configuration](#configuration)).

### Manage Users <a name="users"></a>

To manage (add new, modify, remove or change password) the users that are allowed to access to the system, select the option Users in the main menu. On this page, a list of the users is provided. Since IVA supports user authentication via LDAP, these are not the only users that can access the system. 

[Index](#index)

## Configuration <a name="configuration"></a>

Before using IVA, the following options must be configured. The configuration file (<b>config.ini</b>) is found at the root directory of the source code.

<b>[database]</b> In this section, the configuration used to access the MongoDB database is provided

`host` host name or IP of the computer where the MongoDB service is listening (e.g., localhost)

`port`  port at where the MongoDB service is listening. The default is 27017. For mor information about MongoDB configuration see [MongoDB documentation](https://docs.mongodb.com/manual/reference/configuration-options/)

`name` name of the IVA database (e.g., iva)

`authentication` This option must be set to 1 when MongoDB authentication is required

`user` Username of the user granted to read and write the IVA database

`password` Password of the user granted to read and write the IVA database

<b>[inventory-database]</b> In this section, the options to access the GLPI inventory database (MySql) are given

`host` host name or IP of the computer where the MySql server is listening

`user` user name to access the GLPI database

`password` password of the configured user to access the GLPI database

`name` name of the GLPI database (default name is glpi)

<b>[frontend] </b> IVA is accessed via its web frontend. In this section, the host and port of the HTTP server that receives the requests for IVA are configured. For example, if the host is _localhost_ and the port _8080_, then IVA is accessed at http://localhost:8080/iva/index.html

`host` host name or IP at where the HTTP server is listening (e.g., 127.0.0.1)

`port` port at where the HTTP server is listening (e.g., 8080)

<b>[cve-search]</b> IVA uses [cve-search](https://www.cve-search.org/) to synchronize its local repositories with the public [CPE](https://nvd.nist.gov/cpe.cfm) and [CVE](https://nvd.nist.gov/download.cfm) repositories. In this section, the configuration to use [cve-search](https://www.cve-search.org/) is provided

`dir` directory where the cve-search tool is installed (e.g., /usr/local/share/cve-search)

`db` name of the cve-search database. The default name is cvedb. For more information see [cve-search Configuration](#cve_search_configuration)

`url` url to access the cve-search web interface (e.g., http://192.168.56.125:5000). For more information see [cve-search Configuration](#cve_search_configuration)

<b>[smtp]</b> IVA allows sending emails (notifications) when a software product is confirmed to be vulnerable. In this section, options to send emails via SMTP are configured

`host` host name or IP of the SMTP server

`port` port number at which the SMTP server is listening (normally SMTP uses port 25)

`user` user name for authentication with the server

`password` password for authentication with the server

`sender` Email address of the sender (e.g., iva_admin@example.com)

`receiver` Email address of the receiver (e.g., receiver@example.com)

`smtps` to enable [SMTPS](https://en.wikipedia.org/wiki/SMTPS) (SMTP over TLS/SSL), this option must be set to 1. Note that you need also to configure the port (normally SMTPS listing on port 465). 

`starttls` to enable STARTTLS (method to upgrade SMTP insecure connections to TLS [RFC3207](https://www.ietf.org/rfc/rfc3207.txt)), this option must be set to 1. Note that if the option `smtps` is set to 1, `starttls` is not considered. SMTPS is preferred

`verify_server_cert` if this option is set to 1, the SSL/TLS certificate of the SMTP server is verified with the CA certificate provided in the option `ca_cert_file`. Note that this option can be used with both `smtps` and `starttls` 

`ca_cert_file` path to the CA certificate (in PEM format) used to verify the server certificate (e.g. /usr/local/share/iva/ssl/smtp/ca_cert.pem)

<b>[gpg]</b> IVA allows encrypting (with [GPG](https://www.gnupg.org/)) the notifications that are sent when a software product is vulnerable. In this section, the GPG options are configured

`required` to activate GPG encryption, this option must be set to 1

`home_dir` directory where GPG stores its keyring (e.g., /usr/local/share/iva/gpg). Note that is not necessary to generate a key pair for IVA, since the notifications are only encrypted with the public key of the receiver. The notifications are not signed

`pub_key_file` path to the public key of the receiver (e.g., /usr/local/share/iva/gpg/0xF4G24G5Q.asc)

<b>[ldap]</b> Access to IVA system can be also granted via LDAP. In this section, the LDAP configuration is provided

`host` host name or IP of the LDAP server

`port` port number at which the SMTP server is listening. Normally, for insecure connections (no TLS) the port 389 is used, and 636 for TLS connections (LDAPS). However, by using the method StartTLS, it is possible to secure connections handled at port 389. IVA supports this method, when the option `tls` is activated   

`base_dn` This option indicates the LDAP server where to find the user in the LDAP directory. (e.g., ou=users,dc=my-ldap-server,dc=com)

`tls` to activate the StartTLS method set the value <b>1</b>

`cacert` When TLS is activated, the authenticity of the LDAP server must be verified. To do this, the path to the CA certificate, with which the certificate of the LDAP server is signed, is provided here (e.g., /etc/ssl/certs/cacert.pem)

<b>[logging]</b>

`file` path of the IVA logging file (/var/log/iva.log)

### cve-search Configuration <a name="cve_search_configuration"></a>

[cve-search](https://www.cve-search.org/) comes with a configuration file example: <b>cve-search/etc/configuration.ini.sample</b>. To use this configuration rename the file to <b>configuration.ini</b>. In addition, the following options must be configured:

<b>[Mongo]</b> if the MongoDB authentication is required, the following options must be added and configured:

`Username` username of the user granted to read and write the cve-search database

`Password` password of the user granted to read and write the cve-search database

`DB` this value must be the same as the value of `db` in section <b>[cve-search]</b> in the [IVA configuration](#configuration)

<b>[Webserver]</b> 

`Host` host name or IP at where the HTTP server of cve-search is listening (e.g., 127.0.0.1)  

`Port` port at where the HTTP server of cve-search is listening (e.g., 5000)

[Index](#index)

## Authors <a name="authors"></a>

<b>TODO</b>

[Index](#index)

## License <a name="license"></a>

Copyright 2017 Fraunhofer FKIE

IVA is free software: you can redistribute it and/or modify it under the terms of the <b>GNU Lesser General Public License</b> as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

IVA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.

IVA source code is shipped with a copy of the GNU Lesser General Public License (see COPYING and COPYING.LESSER). If not, see <http://www.gnu.org/licenses/>.

[Index](#index)

## References

[1] [GLPI](http://glpi-project.org/spip.php?lang=en)

<b>TODO</b>

[Index](#index)
