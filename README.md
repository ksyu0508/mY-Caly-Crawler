# mY-Caly-Crawler
GDSC oTP service mY-Caly team crawling back-end api

## direnv setting
```
sudo apt-get install direnv

echo 'eval "$(direnv hook bash)"' >> ~/.bashrc
```

## port setting
```
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8000
```

## Postgres-Container setting
Run postgres container with this command
```
docker run --name my-postgres -e POSTGRES_USER=pguser -e POSTGRES_PASSWORD=pgpassword -e POSTGRES_DB=mycaly -v /home/ubuntu/mY-Caly-Crawler/postgres-data:/var/lib/postgresql/data -p 5432:5432 -d postgres
```