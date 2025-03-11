#!/usr/bin/python3 -tt
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# pylint: enable=invalid-name

"""
Copyright 2017-2018 Paul Wouters <pwouters@redhat.com>

License: GPLv3

A simple script that adds the right magical flags to certificates for use with IPsec.
The X.509 SubjectAltName (SAN) and Extended Key Usage (EKU) attributes are tailored
to be compatible with Apple iOS/OSX, Android and Microsoft IKE/IPsec implementations.

This script also generates (poorly but functional) Apple style .mobileconfig profiles
that can be distributed via email or web links to Apple device users to make installation
of the VPN profile a one click process.

Use the --wipe option to remove all created certificates, keys and CAs and create fresh
new ones for CA and the VPN server itself (in case of use as VPN Remote Access server)
"""

from __future__ import print_function
import base64
import datetime
import os
import shutil
import sys
from OpenSSL import crypto

SERVER_NAME = 'ipsec'
DOMAIN_NAME = 'example.com'
VPN_NAME = 'IKEv2 VPN Server'
VPN_ORG = 'Test Org'
CA_NAME = 'CA for %s' % VPN_ORG
PASSPHRASE = b'secret'
MOBILECONFIG = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>PayloadContent</key>
	<array>
		<dict>
			<key>IKEv2</key>
			<dict>
				<key>AuthenticationMethod</key>
				<string>Certificate</string>
				<key>ChildSecurityAssociationParameters</key>
				<dict>
					<key>DiffieHellmanGroup</key>
					<integer>14</integer>
					<key>EncryptionAlgorithm</key>
					<string>AES-256-GCM</string>
					<key>LifeTimeInMinutes</key>
					<integer>1440</integer>
				</dict>
				<key>DeadPeerDetectionRate</key>
				<string>Medium</string>
				<key>DisableRedirect</key>
				<true/>
				<key>EnableCertificateRevocationCheck</key>
				<integer>0</integer>
				<key>EnablePFS</key>
				<integer>0</integer>
				<key>IKESecurityAssociationParameters</key>
				<dict>
					<key>DiffieHellmanGroup</key>
					<integer>14</integer>
					<key>EncryptionAlgorithm</key>
					<string>AES-256</string>
					<key>IntegrityAlgorithm</key>
					<string>SHA2-512</string>
					<key>LifeTimeInMinutes</key>
					<integer>1440</integer>
				</dict>
				<key>LocalIdentifier</key>
				<string>@CLIENT_DN@</string>
				<key>PayloadCertificateUUID</key>
				<string>1E2E3E4E-5E6E-7E8E-9EAE-BECEDEEEFE0E</string>
				<key>RemoteAddress</key>
				<string>193.110.157.148</string>
				<key>RemoteIdentifier</key>
				<string>vpn.nohats.ca</string>
				<key>UseConfigurationAttributeInternalIPSubnet</key>
				<integer>0</integer>
			</dict>
			<key>IPv4</key>
			<dict>
				<key>OverridePrimary</key>
				<integer>1</integer>
			</dict>
			<key>PayloadDescription</key>
			<string>Configures VPN settings</string>
			<key>PayloadDisplayName</key>
			<string>VPN</string>
			<key>PayloadIdentifier</key>
			<string>com.apple.vpn.managed.0B0851BB-8131-455C-BF78-EE155C18085C</string>
			<key>PayloadType</key>
			<string>com.apple.vpn.managed</string>
			<key>PayloadUUID</key>
			<string>0B0851BB-8131-455C-BF78-EE155C18085C</string>
			<key>PayloadVersion</key>
			<integer>1</integer>
			<key>Proxies</key>
			<dict>
				<key>HTTPEnable</key>
				<integer>0</integer>
				<key>HTTPSEnable</key>
				<integer>0</integer>
			</dict>
			<key>UserDefinedName</key>
			<string>@VPN_NAME@</string>
			<key>VPNType</key>
			<string>IKEv2</string>
		</dict>
		<dict>
			<key>Password</key>
			<string>foobar</string>
			<key>PayloadCertificateFileName</key>
			<string>.zonecloud.ca.p12</string>
			<key>PayloadContent</key>
			<data>
@COMMON_EE_CERT_PKCS12@
			</data>
			<key>PayloadDescription</key>
			<string>Adds a PKCS#12-formatted certificate</string>
			<key>PayloadDisplayName</key>
			<string>@CLIENT_DN@</string>
			<key>PayloadIdentifier</key>
			<string>com.apple.security.pkcs12.1E2E3E4E-5E6E-7E8E-9EAE-BECEDEEEFE0E</string>
			<key>PayloadType</key>
			<string>com.apple.security.pkcs12</string>
			<key>PayloadUUID</key>
			<string>1E2E3E4E-5E6E-7E8E-9EAE-BECEDEEEFE0E</string>
			<key>PayloadVersion</key>
			<integer>1</integer>
		</dict>
		<dict>
			<key>PayloadCertificateFileName</key>
			<string>@CLIENT_DN@.crt</string>
			<key>PayloadContent</key>
			<data>
@COMMON_CACERT_BASE64@
			</data>
			<key>PayloadDescription</key>
			<string>Adds a CA root certificate</string>
			<key>PayloadDisplayName</key>
			<string>Certificate Agency (CA)</string>
			<key>PayloadIdentifier</key>
			<string>com.apple.security.root.F0000001-5A01-1010-1010-111111111111</string>
			<key>PayloadType</key>
			<string>com.apple.security.root</string>
			<key>PayloadUUID</key>
			<string>F0000001-5A01-1010-1010-111111111111</string>
			<key>PayloadVersion</key>
			<integer>1</integer>
		</dict>
	</array>
	<key>PayloadDisplayName</key>
	<string>@VPN_NAME@</string>
	<key>PayloadIdentifier</key>
	<string>com.apple.vpn.managed.DDDDDDDD-BA2E-473E-B7CF-D3DDDD7EDFDD</string>
	<key>PayloadRemovalDisallowed</key>
	<false/>
	<key>PayloadType</key>
	<string>Configuration</string>
	<key>PayloadUUID</key>
	<string>22222222-2344-1850-93A6-562750E7ACA1</string>
	<key>PayloadVersion</key>
	<integer>1</integer>
</dict>
</plist>
"""


def create_keypair(algo=crypto.TYPE_RSA, bits=2048):
    """ Create an OpenSSL keypair """
    pkey = crypto.PKey()
    pkey.generate_key(algo, bits)
    return pkey


def create_csr(
        pkey, CN, C=None, ST=None, L=None, O=None, OU=None,
        emailAddress=None, algo='sha256'):
    """ Create certificate request """
    # pylint: disable=invalid-name, too-many-arguments
    req = crypto.X509Req()
    subject = req.get_subject()
    subject.CN = CN
    subject.C = C
    subject.ST = ST
    subject.L = L
    subject.O = O
    subject.OU = OU
    subject.CN = CN
    subject.emailAddress = emailAddress
    req.set_pubkey(pkey)
    req.sign(pkey, algo)
    return req


def add_ext(cert, kind, crit, string):
    """ Helper to set single extension """
    cert.add_extensions([crypto.X509Extension(kind.encode('utf-8'), crit, string.encode('utf-8'))])


def set_cert_extensions(cert, is_ca):
    """ Set certificate extensions. """
    ku_str = 'digitalSignature'
    if is_ca:
        ku_str = ku_str + ',keyCertSign,cRLSign'
        add_ext(cert, 'basicConstraints', False, 'CA:TRUE')
    else:
        add_ext(cert, 'basicConstraints', False, 'CA:FALSE')
        cnstr = str(cert.get_subject().commonName)
        ipstr = ""
        if cnstr == "ipsec.example.com":
           ipstr = ", IP:192.168.0.22"
        if cnstr == "ipsec2.example.com":
           ipstr = ", IP:192.168.0.23"
        if cnstr == "audit.example.com":
           ipstr = ", IP:192.168.0.16"
        if cnstr == "servera.example.com":
           ipstr = ", IP:192.168.0.10"
        if cnstr == "usbguard.example.com":
           ipstr = ", IP:192.168.0.18"
        add_ext(cert, 'subjectAltName', False, 'DNS: ' + cnstr + ipstr)
    add_ext(cert, 'keyUsage', False, ku_str)
    # Technically serverAuth is only needed for VPN server
    # but clientAuth is needed for Windows
    add_ext(cert, 'extendedKeyUsage', False, 'serverAuth, clientAuth')



def create_sub_cert(
        CN, CACert, CAkey, snum, START, END, C='CA', ST='Ontario', L='Toronto',
        O=VPN_ORG, OU='Clients', emailAddress='pwouters@redhat.com',
        ty=crypto.TYPE_RSA, keybits=2048, sign_alg='sha256', isCA=False):
    """ Create a subordinate cert and return the cert, key tuple
    This could be a CA for an intermediate, or not for an EE
    """
    # pylint: disable=invalid-name, too-many-arguments, too-many-locals
    certkey = create_keypair(ty, keybits)
    certreq = create_csr(certkey, CN, C, ST, L, O, OU, emailAddress, sign_alg)
    cert = crypto.X509()
    cert.set_serial_number(snum)
    cert.set_notBefore(START.encode('utf-8'))
    cert.set_notAfter(END.encode('utf-8'))
    cert.set_issuer(CACert.get_subject())
    cert.set_subject(certreq.get_subject())
    cert.set_pubkey(certreq.get_pubkey())
    cert.set_version(2)
    set_cert_extensions(cert, isCA)
    cert.sign(CAkey, sign_alg)
    return cert, certkey


def create_root_ca(
        CN, START, END, C='CA', ST='Ontario', L='Ottawa', O=VPN_ORG,
        OU='Clients', emailAddress='info@%s' % DOMAIN_NAME,
        ty=crypto.TYPE_RSA, keybits=2048, sign_alg='sha256'):
    """ Create a root CA - Returns the cert, key tuple """
    # pylint: disable=invalid-name, too-many-arguments
    cakey = create_keypair(ty, keybits)
    careq = create_csr(cakey, CN, C, ST, L, O, OU, emailAddress, sign_alg)
    cacert = crypto.X509()
    cacert.set_serial_number(0)
    cacert.set_notBefore(START.encode('utf-8'))
    cacert.set_notAfter(END.encode('utf-8'))
    cacert.set_issuer(careq.get_subject())
    cacert.set_subject(careq.get_subject())
    cacert.set_pubkey(careq.get_pubkey())
    cacert.set_version(2)
    set_cert_extensions(cacert, True)
    cacert.sign(cakey, sign_alg)
    return cacert, cakey


def generate_dates():
    """ Generate before/after dates. """
    now = datetime.datetime.utcnow()
    notbefore = now - datetime.timedelta(days=1)
    notafter = now + datetime.timedelta(days=10 * 365)
    return (
        notbefore.strftime('%Y%m%d%H%M%SZ'),
        notafter.strftime('%Y%m%d%H%M%SZ'),
    )


def writeout_cert_and_key(certdir, name, cert, privkey):
    """ Write the cert and key files """
    with open(certdir + name + '.crt', 'wb') as fhn:
        fhn.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open('keys/' + name + '.key', 'wb') as fhn:
        fhn.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, privkey))


def create_ca(ca_name):
    """ Create the core root cert """
    print('creating CA cert')
    notbefore, notafter = generate_dates()
    cert, key = create_root_ca('Certificate Agency (CA)', notbefore, notafter)
    writeout_cert_and_key('cacerts/', ca_name, cert, key)
    return (cert, key)


def create_pkcs12(path, name, cert, key, cacert):
    """ Package and write out a .p12 file """
    p12 = crypto.PKCS12()
    p12.set_certificate(cert)
    p12.set_privatekey(key)
    p12.set_friendlyname(name.encode('utf-8'))
    p12.set_ca_certificates([cacert])
    with open(path + name + '.p12', 'wb') as fhn:
        fhn.write(p12.export(passphrase=PASSPHRASE))


def create_mobileconfig(username):
    """ Write a custom iOS profile """
    # Replace metas
    profile = MOBILECONFIG
    profile = profile.replace(
        '@COMMON_CACERT_BASE64@',
        ''.join(open('cacerts/exampleca.crt', 'r').readlines()[1:-1]))
    profile = profile.replace(
        '@COMMON_EE_CERT_PKCS12@',
        str(base64.b64encode(
            open('pkcs12/%s.%s.p12' % (username, DOMAIN_NAME), 'rb').read())))
    profile = profile.replace('@CLIENT_DN@', '%s.%s' % (username, DOMAIN_NAME))
    profile = profile.replace('@CA_NAME@', CA_NAME)
    profile = profile.replace('@SERVER_NAME@', SERVER_NAME)
    profile = profile.replace('@VPN_NAME@', VPN_NAME)
    profile = profile.replace('@VPN_ORG@', VPN_ORG)
    profile = profile.replace('@PASSPHRASE@', str(PASSPHRASE))
    profile = profile.replace('@DOMAIN_NAME@', DOMAIN_NAME)

    # Create file
    with open('mobileconfig/%s.mobileconfig' % username, 'w') as fhn:
        fhn.write(profile)


def create_end_certs(cacert, cakey, end_certs):
    """ Create end certificates """
    # Read current serial
    try:
        serial = int(open('serial.txt', 'r').read())
    except IOError:
        serial = 2

    # Create certificates
    notbefore, notafter = generate_dates()
    for name in end_certs:
        common_name = name + '.' + DOMAIN_NAME
        cert, key = create_sub_cert(
            common_name, cacert, cakey, serial, notbefore, notafter)
        writeout_cert_and_key('certs/', name, cert, key)
        create_pkcs12('pkcs12/', common_name, cert, key, cacert)
        create_mobileconfig(name)
        serial += 1

    # Write new serial
    with open('serial.txt', 'w') as fhn:
        fhn.write(str(serial))


def reset_files():
    """ Delete all files and create empty subdirs. """
    for item in ('keys', 'cacerts', 'certs', 'pkcs12', 'mobileconfig'):
        if os.path.isdir(item):
            shutil.rmtree(item)
        os.mkdir(item)
    for item in ('serial.txt',):
        if os.path.isfile(item):
            os.remove(item)


def run_dist_certs():
    """ Generate new x509 certificates, p12 files, CA, keys, and CRLs """
    cacert, cakey = create_ca('exampleca')
    create_end_certs(cacert, cakey, (
        'ipsec', 'ipsec2' , 'audit', 'usbguard', 'servera'
    ))


def main(argv):
    """ Main program. """
    # Check arguments
    if len(argv) != 2:
        sys.exit('%s: [--wipe] username' % argv[0])
    ##os.chdir('labcerts/')

    # --wipe
    if argv[1] == '--wipe':
        reset_files()
        run_dist_certs()
        print('OK: CA system completely re-initialized')
        return

    # Create new username
    username = argv[1]
    if not username.isalnum():
        sys.exit('Error: bad username')
    if os.path.isfile('certs/%s.crt' % username):
        sys.exit('Error: user %s already exists' % username)

    cacert = crypto.load_certificate(
        crypto.FILETYPE_PEM, open('cacerts/exampleca.crt', 'r').read())
    cakey = crypto.load_privatekey(
        crypto.FILETYPE_PEM, open('keys/exampleca.key', 'r').read())
    create_end_certs(cacert, cakey, (username,))
    print('OK: Generated X.509 certificate for %s' % username)


if __name__ == '__main__':
    main(sys.argv)
