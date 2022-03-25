import subprocess, pymysql

db = pymysql.connect(host='localhost', user='root', password='1q2w3e4R!', charset='utf8', db='servers')
cursor = db.cursor()
'''
sql = """
    CREATE TABLE servers (
            ip VARCHAR(20) NOT NULL,
            connect VARCHAR(10) NOT NULL,
	        docker VARCHAR(3),
            node VARCHAR(3),
            apache VARCHAR(3),
            jmx VARCHAR(3),
            mysqld VARCHAR(3),
            PRIMARY KEY(ip)
    );
    """
cursor.execute(sql)
db.commit()
'''
hosts_dir = "/etc/ansible/hosts"

def delete_lastline():
    subprocess.run(['sudo', 'sed', '-i','$d','/etc/ansible/hosts']) 

def add_prometheus_targets(select_num):
    with open("/home/daou_docker/prometheus/prometheus.yml", "a") as f:
        for i in select_num:
            if i != '0':
                f.write("  - job_name: '"+ip+"-"+exporter_type[int(i)]+"'\n")
                f.write("    static_configs:\n")
                f.write("      - targets: ['"+ip+":"+str(exporter[exporter_type[int(i)]])+"']\n\n")
        f.close()
        print('Added prometheus targets')

def select_exporters():
    print("\n      ip      , status ,docker, node, apache, jmx, mysqld")
    cursor.execute("SELECT * FROM servers WHERE ip = %s;", str(ip))
    result = cursor.fetchall()
    for i in result:
        print(i)
    print("\n\n0. Install Docker \n")
    print("1. Node Exporter \n")
    print("2. Apache Exporter \n")
    print("3. Jmx Exporter \n")
    print("4. Mysqld Exporter \n")
    select_num = str(input("Enter Exporter Number : "))
    return select_num

def install_exporters(select_num):
    for i in select_num:
        if i == '0':
            flag = subprocess.run(['ansible-playbook', 'docker-play.yml'])
            if flag.returncode != 0:
                print('error docker-playbook')
            else:    
                sql = "UPDATE servers SET docker = 1 WHERE ip = "+str("'"+ip+"'")
                cursor.execute(sql)
                db.commit()

        elif i == '1':
            flag = subprocess.run(['ansible-playbook', 'node-play.yml'])
            if flag.returncode != 0:
                print('error node-playbook')
            else:
                sql = "UPDATE servers SET node = 1 WHERE ip = "+str("'"+ip+"'")
                cursor.execute(sql)
                db.commit
        elif i == '2':
            flag = subprocess.run(['ansible-playbook', 'apache-play.yml'])
            if flag.returncode != 0:
                print('error apache-playbook')
            else:
                sql = "UPDATE servers SET apache = 1 WHERE ip = "+str("'"+ip+"'")
                cursor.execute(sql)
                db.commit()

        elif i == '3':
            flag = subprocess.run(['ansible-playbook', 'jmx-play.yml'])
            if flag.returncode != 0:
                print('error jmx-playbook')
            else:    
                sql = "UPDATE servers SET jmx = 1 WHERE ip = "+str("'"+ip+"'")
                cursor.execute(sql)
                db.commit()
        elif i == '4':
            flag = subprocess.run(['ansible-playbook', 'mysqld-play.yml'])
            if flag.returncode != 0:
                print('error mysqld-playbook')
            else:
                sql = "UPDATE servers SET mysqld = 1 WHERE ip = "+str("'"+ip+"'")
                cursor.execute(sql)
                db.commit()
        else:
            print('Please try again')


if __name__ == '__main__':
    subprocess.run(['cd', '/etc/ansible'])
    exporter_type = ["docker", "node", "apache", "jmx", "mysqld"]
    exporter = {"docker":0000, "node":9100, "apache":9117, "jmx":8081, "mysqld":9104}
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
                f.write('\n'+ip)
                f.close()
        else:
            print("Already added IP")

        
        flag = subprocess.run(['ansible', 'exporter', '-m', 'ping'])
        if flag.returncode != 0:
            print("Coneecting error")
            val = (str(ip), "not connect")
            cursor.execute('INSERT INTO servers (ip, connect) Values(%s, %s) ON DUPLICATE KEY UPDATE connect="not connect"', val)
            db.commit()
            delete_lastline()
        else:
            val = (str(ip), "connect")
            cursor.execute('INSERT INTO servers (ip, connect) Values(%s, %s) ON DUPLICATE KEY UPDATE connect="connect"', val)
            db.commit()
            select_num = select_exporters()
            install_exporters(select_num)
            add_prometheus_targets(select_num)            
            subprocess.run(['sudo', 'docker', 'restart', 'my_prometheus'])

    delete_lastline()
    db.close()
        




    
