import yaml, json, os
with open('scripts/configuration.json', 'r') as configuration_file:
    configuration = json.load(configuration_file)
    environments = configuration.get('environments')
    print(environments)
    for environment in environments:
        accounts = configuration.get(environment)
        for account, account_info in accounts.items():
            file_name = environment + "/whitelist/" + account + "_whitelist.json"
            try:
              with open(file_name, 'r') as json_file:
                    json_data = json.load(json_file)
                    baseline_yaml = [
                        {
                            "hosts": "localhost",
                            "vars": {
                                "username": "admin",
                                "vdom": "root"
                            },
                            "tasks": [
                                {
                                    "shell": "aws ssm get-parameters --name 'ansible_fortigates_egress_ips' --query Parameters[*].Value --output text",
                                    "register": "IPs"
                                },
                                {
                                    "shell": "aws ssm get-parameters --name 'ansible_fortigates_egress_password' --query Parameters[*].Value --output text --with-decryption",
                                    "register": "secret"
                                },
                                {
                                    "name": "Configure url to be filtered by fortigate",
                                    "fortios_webfilter_urlfilter": {
                                        "host": "{{ item }}",
                                        "username": "{{ username }}",
                                        "password": "{{ secret.stdout }}",
                                        "vdom": "{{ vdom }}",
                                        "https": True,
                                        "ssl_verify": False,
                                        "webfilter_urlfilter": {
                                            "state": "present",
                                            "id": str(account_info.get('id')),
                                            "name": account + "_urlfilter",
                                            "comment": account + "_urlfilter",
                                            "entries": []
                                        }
                                    },
                                    "with_items": [
                                        '{{ IPs.stdout.split(",")[0] }}',
                                        '{{ IPs.stdout.split(",")[1] }}',
                                        '{{ IPs.stdout.split(",")[2] }}'
                                    ]
                                }
                            ]
                        }
                    ]
                    urls = json_data.get('whitelist_urls')
                    url_id = 0
                    if urls:
                        for url in urls:
                            url_id += 1
                            tasks = baseline_yaml[0].get("tasks")[2]
                            entries = tasks.get('fortios_webfilter_urlfilter').get('webfilter_urlfilter').get('entries')
                            if url[0] == "." or url[0] == "*":
                                entries.append({
                                    "id": str(url_id),
                                    "url": url.strip(),
                                    "type": "wildcard",
                                    "action": "allow",
                                    "status": "enable",
                                    "exempt": "pass",
                                    "web_proxy_profile": account + "_profile",
                                    "referrer-host": ""
                                })
                            else:
                                entries.append({
                                    "id": str(url_id),
                                    "url": url.strip(),
                                    "type": "simple",
                                    "action": "allow",
                                    "status": "enable",
                                    "exempt": "pass",
                                    "web_proxy_profile": account + "_profile",
                                    "referrer-host": ""
                                })


                        url_id += 1
                        tasks = baseline_yaml[0].get("tasks")[2]
                        entries = tasks.get('fortios_webfilter_urlfilter').get('webfilter_urlfilter').get('entries')
                        entries.append({
                            "id": str(url_id),
                            "url": '*',
                            "type": "wildcard",
                            "action": "block",
                            "status": "enable",
                            "exempt": "pass",
                            "web_proxy_profile": account + "_profile",
                            "referrer-host": ""
                        })
                    json_file.close()
                    url_playbook_filename = os.path.join(environment, "ansible_playbooks", "webfilter_url_playbooks",
                                                         account + "_webfilter_add_url.yaml")
                    print(os.path.abspath(url_playbook_filename))
                    #for x in os.path.abspath(url_playbook_filename):
                    with open(url_playbook_filename, 'w+') as file:
                        documents = yaml.dump(baseline_yaml, file, allow_unicode=True, sort_keys=False)
                    file.close()
                    del baseline_yaml[:]
                    del baseline_yaml
            except Exception as e:
                print("something went wrong: ", e)





