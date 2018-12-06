#!/bin/sh

coordinator_host=$1
coordinator_port=$2
worker_1_host=$3
worker_1_port=$4
worker_2_host=$5
worker_2_port=$6

shift 2
cmd="$@"

# wait for the coordinator docker to be running
while ! pg_isready -h $coordinator_host -p $coordinator_port -q -U postgres; do
  >&2 echo "Postgres on coordinator is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres on coordinator is up - executing command"


# wait for the coordinator docker to be running
while ! pg_isready -h $worker_1_host -p $worker_1_port -q -U postgres; do
  >&2 echo "Postgres on worker 1 is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres on worker 1 is up - executing command"


# wait for the coordinator docker to be running
while ! pg_isready -h $worker_2_host -p $worker_2_port -q -U postgres; do
  >&2 echo "Postgres on worker 2 is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres on worker 2 is up - executing command"
