import docker

#def _check_db_ready(container):
#    db_config = get_db_config(container)
#
#    try:
#        with scoped_session(db_config) as session:
#            session.execute("SELECT 1")
#            return True
#    except OperationalError:
#        return False


def create_redis_container():
    client = docker.from_env(assert_hostname=False)
    container = client.containers.run("redis:4", detach=True)

    # Wait for db to be ready
    #while not _check_db_ready(container):
    #    time.sleep(.1)

    #db_upgrade(get_db_config(container))

    return container


def get_redis_container():
    return create_redis_container()


def get_redis_config(redis_container):
    container = redis_container.client.api.containers(filters={'id': redis_container.id})[0]

    return {'host': container['NetworkSettings']['Networks']['bridge']['IPAddress'],
            'port': 6379}
