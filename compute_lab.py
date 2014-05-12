__author__ = 'peersp'

import httplib2
from apiclient.discovery import build
import apiclient.http


class ComputeLab(object):

    def __init__(self, credentials, project_id, lab_zone):

        api_version = 'v1'
        self.gce_url = 'https://www.googleapis.com/compute/%s/projects/' % api_version

        self.project_id = project_id
        self.lab_zone = lab_zone

        #Authorisation
        http = httplib2.Http()

        self.auth_http = credentials.authorize(http)

        #Build Service
        self.gce_service = build('compute', api_version)

    def create_instances(self, image, machine_type, instance_name_format, accounts):

        default_network = 'default' #use default network settings
        # default_root_pd_name = 'my-root-pd' #defaults to instance name if omitted
        default_service_email = 'default'
        default_scopes = ['https://www.googleapis.com/auth/devstorage.read_only']

        batch = apiclient.http.BatchHttpRequest(callback=self._exception_handler)

        image_url = '%s%s%s/global/images/%s' % (self.gce_url, image.split('-')[0], '-cloud', image)
        machine_type_url = '%s%s/zones/%s/machineTypes/%s' % (self.gce_url, self.project_id, self.lab_zone, machine_type)
        network_url = '%s%s/global/networks/%s' % (self.gce_url, self.project_id, default_network)

        for n in range(len(accounts)):
            batch.add(self.gce_service.instances().insert(project=self.project_id,
                                                     body={
                                                        'name': '%s%s' % (instance_name_format, n),
                                                        'machineType': machine_type_url,
                                                        'disks': [{
                                                            'autoDelete': 'true',
                                                            'boot': 'true',
                                                            'type': 'PERSISTENT',
                                                            'initializeParams' : {
                                                              # 'diskName': default_root_pd_name,
                                                              'sourceImage': image_url
                                                            }
                                                        }],
                                                        'networkInterfaces': [{
                                                            'accessConfigs': [{
                                                                'type': 'ONE_TO_ONE_NAT',
                                                                'name': 'External NAT'
                                                        }],
                                                        'network': network_url
                                                        }],
                                                        'metadata':  [{
                                                            'items': [ {
                                                                'key': 'user',
                                                                'value': accounts[n]['user']
                                                            }, {
                                                                'key': 'pass',
                                                                'value': accounts[n]['pass']
                                                            }, {
                                                                'key': 'startup-script-url',
                                                                'value': 'gs://pjp-scripts/startup.sh'
                                                            }]
                                                        }],
                                                        'serviceAccounts': [{
                                                            'email': default_service_email,
                                                            'scopes': default_scopes
                                                        }]
                                                    },
                                                     zone=self.lab_zone))


        batch.execute(http=self.auth_http)

    def delete_instances(self, instances):

        batch = apiclient.http.BatchHttpRequest(callback=self._exception_handler)

        for instance in instances:
            batch.add(self.gce_service.instances().delete(project=self.project_id,
                                                          instance=instance,
                                                          zone=self.lab_zone))
        batch.execute(http=self.auth_http)

    def _exception_handler(self, request_id, response, exception):
        if exception is not None:
            print exception
            pass
        else:
            # print response
            pass