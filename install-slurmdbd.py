import mysql.connector as mysql



def slurm_connect_mysql():
    
    try:

        db = mysql.connect(host = 'localhost', user = 'root', passwd = 'root')
        #cursor = db.cursor.execute("create database slurm_acct_db")
        operation = "create database slurm_acct_db; create user 'slurm'@'localhost'; set password for 'slurm'@'localhost' = password('slurmdbpass'); set password for 'slurm'@'localhost' = password('slurmdbpass'); grant all privileges on slurm_acct_db.* to 'slurm'@'localhost'; flush privileges;"
        db.cursor.execute(operation, multi=True)

    except: 
        print("not connected !")

