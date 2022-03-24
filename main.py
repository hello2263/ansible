import subprocess

hosts_dir = "/etc/ansible/hosts"

def delete_lastline(dir):
    subprocess.call(['sed','-i','/.*dog.*/d','animal.txt']) 

def add_prometheus_targets():
    with open("/home/daou_docker/prometheus/prometheus.yml", "a") as f:
        for i in range(4):
            f.write("  - job_name: '"+ip+"-"+user[i]+"'\n")
            f.write("    static_configs:\n")
            f.write("      - targets: ['"+ip+":"+str(exporter[user[i]])+"']\n\n")
        f.close()
        print('Added prometheus targets')


if __name__ == '__main__':
    user = ["node", "apache", "jmx", "mysqld"]
    exporter = {"node":9100, "apache":9117, "jmx":8081, "mysqld":9104}
    state = input('Selected Mode: 1.creat 2.manage\n')
    if state == 'creat' or state == '1':
        state = 1
    elif state == 'manage' or state == '2':
        state = 2
    else:
        print("Please Retry")

    if state == 1:
        ip = input('Enter NodePC IP\n')
        with open('/etc/ansible/hosts', 'r') as f:
            for line in f:
                pass
            last_line = line
            f.close()
        if last_line != ip:
            with open("/etc/ansible/hosts", "a") as f:
                f.write("\n"+ip)
                f.close()
        else:
            print("Already added IP")

        
        flag = subprocess.run(['ansible', 'connect', '-m', 'ping'])
        if flag.returncode != 0:
            print("Coneecting error")
            #delete_lastline('/etc/ansible/hosts')
        else:
            add_prometheus_targets()            
            subprocess.run(['sudo', 'docker', 'restart', 'my_prometheus'])

        




    
