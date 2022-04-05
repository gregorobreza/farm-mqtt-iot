# FARM stack and MQTT Broker
This is dev enviroment for FARM stack with mosquitto MQTT Broker. Ideal for simple IoT projects or creating microservice. 

# Security
You must add the environment variables MONGO_USER and MONGO_PASSWORD to your environment. You can also add a ".env" file to the root of your system with the environment variables.

Example .env contents

```
MONGO_USER=root

MONGO_PASSWORD=OTNmYTdjYmZkMjE5ZmYzODg0MDZiYWJh
```
Mosquitto MQTT Broker is already preconfigured. You can add your own user with connecting to container and adding new user:

```
mosquitto_passwd -b /mosquitto/config/pwfile <username> <password>
```

# Run
You can run the FARM stack by running the following command.

```
docker-compose up --build
```

And after you are sure it runs without error in detached mode:
```
docker-compose up -d
```