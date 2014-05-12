__author__ = 'peersp'

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from oauth2client import tools
import sys
import argparse

import compute_lab

def main(argv):

    flow = flow_from_clientsecrets('client_secrets.json', scope='https://www.googleapis.com/auth/compute')
    storage = Storage('oauth2.dat')
    credentials = storage.get()

    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])

    flags = parser.parse_args(argv[1:])

    if credentials is None or credentials.invalid:
        print 'fail'
        credentials = run_flow(flow, storage, flags)

    project_id = 'grand-century-576'
    lab_zone = 'europe-west1-b'
    image = 'debian-7-wheezy-v20140415'
    machine_type = 'f1-micro'
    name_format = 'pjp-lab-'
    user_list = [{'user': 'testuser', 'pass': 'password'}, {'user': 'testuser', 'pass': 'password'}, {'user': 'testuser', 'pass': 'password'}]

    lab = compute_lab.ComputeLab(credentials, project_id, lab_zone)

    # lab.create_instances(image, machine_type, name_format, user_list)

    lab.delete_instances(['pjp-lab-0', 'pjp-lab-1', 'pjp-lab-2'])

if __name__ == '__main__':
  main(sys.argv)