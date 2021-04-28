
# PR-Web-01-Ubuntu

1. IP = 
	1. Pub : 13.66.168.190
	2. Priv : 10.0.0.4
2. Version = Ubuntu 18.04-LTS
3. Ports
	1. Inbound
		1. 3000 : Web service
	2. Outband
		1. 5000 : Middleware - Database


4. Start Services
	1. Polyester-Road dir 
	2. execute ```npm run dev```
	3. server starts at ```localhost:3000```

# PR-MiddleApp-Ubuntu

1. IP = 
	1. Pub : 13.66.135.19
	2. Priv : 10.0.1.4
2. Version = Ubuntu 18.04-LTS
3. Ports
	1. Inbound
		1. 5000 : Middleware - Database
	2. Outband
		1. 3306 : MySQl database at server pr-customerdb-mysql

4. Start Services
	1. Polyester-Road-Backend dir 
	2. execute ```python3 main.py```


# PR-Secret Wallet Sever-Ubuntu

1. IP = 
	1. Pub : 52.149.8.244
	2. Priv : 10.0.2.4
2. Version = Ubuntu 18.04-LTS
3. Ports
	1. Inbound
		1. 3306 : MySQl database at server pr-customerdb-mysql
	2. Outband

4. Start Services




# PR-customerdb-mysql

1. Server Name : pr-customerdb-mysql.mysql.database.azure.com
2. admin login : userisme@pr-customerdb-mysql
3. password : 07XTf1s4mU07XTf1s4mU
4. Login cmd 
```sh
mysql -h pr-customerdb-mysql.mysql.database.azure.com -u userisme@pr-customerdb-mysql -p
```
5. database:table - transactions:transactions (id: trans id: email : item id(price) : quant)

