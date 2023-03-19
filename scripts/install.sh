# postgres
docker run --name postgresql-container -p 5432:5432 -e POSTGRES_USER=user -e POSTGRES_PASSWORD=1234 -d postgres
# pgadmin on http://localhost:5051
docker pull dpage/pgadmin4:latest
docker run --name pgadmin-baeldung -p 5051:80 -e "PGADMIN_DEFAULT_EMAIL=user@baeldung.com" -e "PGADMIN_DEFAULT_PASSWORD=baeldung" -d dpage/pgadmin4
# find hostname (172.17.0.1)
docker inspect postgresql-container -f "{{json .NetworkSettings.Networks }}"