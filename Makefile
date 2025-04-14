postgres:
	docker run --name postgres_boilerplate_container -p 8005:5432 \
	-e POSTGRES_USER=postgres \
	-e POSTGRES_PASSWORD=postgres \
	-v postgres_data:/var/lib/postgresql/data \
	--rm \
	-d postgres:latest

redis:
	docker run --name redis_boilerplate_container -p 8006:6379 \
	-v redis_data:/var/lib/redis/data \
	--rm \
	-d  docker.arvancloud.ir/redis:7.4.2

broker:
	docker run --name broker_boilerplate_container -p 8007:6379 \
	-v redis_data:/var/lib/redis/data \
	--rm \
	-d  docker.arvancloud.ir/redis:7.4.2

createdb:
	docker exec -it postgres_boilerplate_container createdb --username=postgres --owner=postgres boilerplate

dropdb:
	docker exec -it postgres_boilerplate_container dropdb --username=postgres boilerplate


celerybeat :
	celery -A core beat -l info

celeryworker:
	celery -A core worker -l info


minio:
	docker run --name minio_boilerplate_container -p 9000:9000 -p 9001:9001 \
	-e MINIO_ROOT_USER=minioadmin \
	-e MINIO_ROOT_PASSWORD=minioadmin \
	-v minio_data:/data \
	--rm \
	-d minio/minio:latest server /data --console-address ":9001"
