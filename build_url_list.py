import yaml, json, os
with open('scripts/configuration.json', 'r') as configuration_file:
    configuration = json.load(configuration_file)
    environments = configuration.get('environments')
    for environment in environments:
        accounts = configuration.get(environment)
        for account, account_info in accounts.items():
          file_name = environment + "/whitelist/" + account + "_whitelist.json"
          try:
            with open(file_name, 'r') as json_file:
                    json_data = json.load(json_file)

                    baseline_yaml = [ {
                                      "hosts": "FW00",
                                      "collections": "[fortinet.fortios]",
                                      "connection": "httpapi",
                                      "vars": {
                                              "vdom": "root",
                                              "ansible_httpapi_use_ssl": "no",
                                              "ansible_httpapi_validate_certs": "no",
                                              "ansible_httpapi_port": "80",
                                              "ansible_network_os": "fortinet.fortios.fortios"
                                              },

                                      "tasks": [ {
                                                 "name": "Configure url to be filtered by fortigate",
                                                 "fortios_webfilter_urlfilter": {
                                                                                "vdom": "{{ vdom }}",
                                                                                "access_token": "6kyx54wpbpp8q5GHGktrN4fpj5jsnq",
                                                                                "state": "present",
                                                                                "webfilter_urlfilter": {

                                                                                                       "id": "351",
                                                                                                       "name": "poopy20",
                                                                                                       "entries": []
                                                                                                        }
                                                                                 }


                                                 }
                                               ]
                                             }
                                           ]
                    urls = json_data.get('whitelist_urls')
                    url_id = 0
                    if urls:
                        for url in urls:
                            url_id += 1
                            tasks = baseline_yaml[0].get("tasks")[0]
                            entries = tasks.get('fortios_webfilter_urlfilter').get('webfilter_urlfilter').get('entries')
                            if url[0] == "." or url[0] == "*":
                                entries.append({
                                    "action": "allow",
                                    "dns_address_family": "ipv4",
                                    "id": str(url_id),
                                    "referrer_host": "myhostname",
                                    "status": "enable",
                                    "type": "wildcard",
                                    "url": url.strip()
                                })
                            else:
                                entries.append({
                                    "action": "allow",
                                    "dns_address_family": "ipv4",
                                    "id": str(url_id),
                                    "referrer_host": "myhostname",
                                    "status": "enable",
                                    "type": "simple",
                                    "url": url.strip()
                                })
                        url_id += 1
                        tasks = baseline_yaml[0].get("tasks")[0]
                        entries = tasks.get('fortios_webfilter_urlfilter').get('webfilter_urlfilter').get('entries')
                        entries.append({

                                    "action": "block",
                                    "dns_address_family": "ipv4",
                                    "id": str(url_id),
                                    "referrer_host": "myhostname",
                                    "status": "enable",
                                    "type": "wildcard",
                                    "url": "*"
                        })
                    json_file.close()
                    url_playbook_filename = os.path.join(environment, "ansible_playbooks", "webfilter_url_playbooks",
                                                         account + "_webfilter_add_url.yaml")
                    print(os.path.abspath(url_playbook_filename))
                    with open(url_playbook_filename, 'w+') as file:
                        documents = yaml.dump(baseline_yaml, file, allow_unicode=True, sort_keys=False)
                    file.close()
                    del baseline_yaml[:]
                    del baseline_yaml
          except Exception as e:
               print("something went wrong: ", e)





